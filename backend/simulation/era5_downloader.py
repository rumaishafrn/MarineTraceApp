import argparse
import cdsapi
import xarray as xr
import os
import zipfile
import shutil
import warnings
from datetime import datetime, timedelta
from pathlib import Path
import config

# Suppress minor warnings for cleaner logs
warnings.filterwarnings("ignore")

def standardize_era5_dataset(raw_path: Path, final_path: Path) -> bool:
    """
    Pre-processes raw ERA5 data:
    1. Renames variables to OpenDrift internal names (x_wind, sea_surface...stokes...).
    2. Fixes dimensions (expver, valid_time).
    3. Injects CF-compliant metadata.
    """
    try:
        ds = xr.open_dataset(raw_path)

        # 1. Detect Variable Names (Handle variations in ERA5 naming)
        vars_list = list(ds.data_vars)
        u_src = next((x for x in ['u10', '10m_u_component_of_wind'] if x in vars_list), None)
        v_src = next((x for x in ['v10', '10m_v_component_of_wind'] if x in vars_list), None)
        ust_src = next((x for x in ['ust', 'u_component_stokes_drift'] if x in vars_list), None)
        vst_src = next((x for x in ['vst', 'v_component_stokes_drift'] if x in vars_list), None)

        # 2. Fix Dimensions
        if 'valid_time' in ds.coords:
            ds = ds.rename({'valid_time': 'time'})
        if 'expver' in ds.dims:
            # Combine ERA5 (expver=1) and ERA5T (expver=5)
            try:
                ds = ds.sel(expver=1).combine_first(ds.sel(expver=5))
            except:
                ds = ds.isel(expver=0)

        # 3. Rebuild Dataset with Standard Names
        ds_clean = xr.Dataset(
            data_vars={
                'x_wind': ds[u_src],
                'y_wind': ds[v_src],
                'sea_surface_wave_stokes_drift_x_velocity': ds[ust_src],
                'sea_surface_wave_stokes_drift_y_velocity': ds[vst_src],
            },
            coords=ds.coords
        )

        # 4. Inject Metadata (Crucial for OpenDrift auto-detection)
        ds_clean.attrs['proj4'] = "+proj=longlat +datum=WGS84 +no_defs"
        ds_clean['x_wind'].attrs = {'standard_name': 'eastward_wind', 'units': 'm s**-1'}
        ds_clean['y_wind'].attrs = {'standard_name': 'northward_wind', 'units': 'm s**-1'}
        ds_clean['sea_surface_wave_stokes_drift_x_velocity'].attrs = {
            'standard_name': 'sea_surface_wave_stokes_drift_x_velocity',
            'units': 'm s**-1'
        }
        ds_clean['sea_surface_wave_stokes_drift_y_velocity'].attrs = {
            'standard_name': 'sea_surface_wave_stokes_drift_y_velocity',
            'units': 'm s**-1'
        }
        
        # Save compressed NetCDF
        ds_clean.to_netcdf(final_path, engine='netcdf4')
        ds.close()
        ds_clean.close()
        return True

    except Exception as e:
        print(f"[ERROR] Standardization failed: {e}")
        return False

def process_daily_era5(target_date: datetime, lat: float, lon: float, buffer: float = 2.0):
    """Downloads and processes a single day of ERA5 data."""
    config.ensure_directories()
    
    filename = config.get_daily_filename("era5", target_date, lat, lon)
    final_path = config.DATA_REPO_DIR / filename
    
    if final_path.exists():
        print(f"[SKIP] File exists: {filename}")
        return

    print(f"[ERA5] Processing date: {target_date.date()}")
    
    # Define request parameters
    bbox = config.get_bbox(lat, lon, buffer)
    temp_raw = config.TEMP_RUNTIME_DIR / f"raw_{filename}"
    
    c = cdsapi.Client()
    
    try:
        # Request 24 hours of data
        c.retrieve('reanalysis-era5-single-levels', {
            'product_type': 'reanalysis', 'format': 'netcdf',
            'variable': ['10m_u_component_of_wind', '10m_v_component_of_wind', 
                         'u_component_stokes_drift', 'v_component_stokes_drift'],
            'year': str(target_date.year),
            'month': f"{target_date.month:02d}",
            'day': f"{target_date.day:02d}",
            'time': [f"{h:02d}:00" for h in range(24)],
            'area': bbox, 'grid': [0.25, 0.25], 
        }, str(temp_raw))

        # Handle File Type (Zip vs NC) & Merge
        is_zip = zipfile.is_zipfile(temp_raw)
        files_to_merge = [temp_raw]
        
        if is_zip:
            with zipfile.ZipFile(temp_raw, 'r') as z:
                z.extractall(config.TEMP_RUNTIME_DIR)
                files_to_merge = [config.TEMP_RUNTIME_DIR / n for n in z.namelist() if n.endswith('.nc')]
        
        # Merge if multiple files (Wind + Wave often split)
        temp_merged = config.TEMP_RUNTIME_DIR / f"merged_{filename}"
        if len(files_to_merge) > 1:
            with xr.open_mfdataset(files_to_merge) as ds:
                ds.to_netcdf(temp_merged)
        else:
            shutil.move(files_to_merge[0], temp_merged)

        # Standardize
        if standardize_era5_dataset(temp_merged, final_path):
            print(f"[SUCCESS] Saved: {filename}")

        # Cleanup
        if temp_merged.exists(): os.remove(temp_merged)
        if temp_raw.exists(): os.remove(temp_raw)
        if is_zip:
            for f in files_to_merge: 
                if f.exists(): os.remove(f)

    except Exception as e:
        print(f"[FAIL] Failed processing {target_date.date()}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ERA5 Daily Downloader & Preprocessor")
    parser.add_argument("--start", required=True, help="Start Date (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=1, help="Number of days")
    parser.add_argument("--lat", type=float, required=True, help="Center Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Center Longitude")
    args = parser.parse_args()
    
    start_dt = datetime.strptime(args.start, "%Y-%m-%d")
    for i in range(args.days):
        process_daily_era5(start_dt + timedelta(days=i), args.lat, args.lon)