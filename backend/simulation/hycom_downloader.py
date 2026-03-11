import argparse
import xarray as xr
import warnings
from datetime import datetime, timedelta
import config

warnings.filterwarnings("ignore")

def process_daily_hycom(target_date: datetime, lat: float, lon: float, buffer: float = 1.0):
    """Downloads a single day of HYCOM currents."""
    config.ensure_directories()
    
    filename = config.get_daily_filename("hycom", target_date, lat, lon)
    final_path = config.DATA_REPO_DIR / filename
    
    if final_path.exists():
        print(f"[SKIP] File exists: {filename}")
        return

    print(f"[HYCOM] Processing date: {target_date.date()}")
    
    # HYCOM OPeNDAP URL (GLBy0.08/expt_93.0 is standard reanalysis)
    hycom_url = 'https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0'
    bbox = config.get_bbox(lat, lon, buffer)
    
    try:
        # Time slice covers full day (00:00 to 23:00)
        t_start = target_date
        t_end = target_date + timedelta(hours=23)

        # drop_variables=['tau'] prevents decoding errors
        ds = xr.open_dataset(hycom_url, drop_variables=['tau'], decode_times=True)
        
        # Slice spatially and temporally
        subset = ds.sel(
            lat=slice(bbox[2], bbox[0]), 
            lon=slice(bbox[1], bbox[3]), 
            time=slice(t_start, t_end)
        )
        
        # Select Surface Currents only (depth=0)
        subset = subset[['water_u', 'water_v']].sel(depth=0, method='nearest')
        
        # Save
        subset.to_netcdf(final_path)
        print(f"[SUCCESS] Saved: {filename}")
        
    except Exception as e:
        print(f"[FAIL] HYCOM Download failed for {target_date.date()}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HYCOM Daily Downloader")
    parser.add_argument("--start", required=True, help="Start Date (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=1, help="Number of days")
    parser.add_argument("--lat", type=float, required=True, help="Center Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Center Longitude")
    args = parser.parse_args()
    
    start_dt = datetime.strptime(args.start, "%Y-%m-%d")
    for i in range(args.days):
        process_daily_hycom(start_dt + timedelta(days=i), args.lat, args.lon)