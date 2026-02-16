import argparse
import logging
import sys
import os
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# OpenDrift Imports
from opendrift.readers import reader_netCDF_CF_generic
import xarray as xr

# Local Module Imports
from . import config
from .modules.physics import LitterDrift
from .modules.data_prep import prepare_merged_dataset
from .modules.visualization import generate_realistic_map

# ==============================================================================
# LOGGING SETUP
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    km = 6371 * c
    return km

def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    Calculates the initial bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    
    x = np.sin(dlon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1) * np.cos(lat2) * np.cos(dlon))
    
    initial_bearing = np.arctan2(x, y)
    
    # Now we have the initial bearing but math.atan2() returns values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = np.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    
    return compass_bearing

def get_cardinal_direction(bearing):
    directions = ["Utara", "Timur Laut", "Timur", "Tenggara", "Selatan", "Barat Daya", "Barat", "Barat Laut"]
    index = round(bearing / 45) % 8
    return directions[index]

# ==============================================================================
# MAIN SIMULATION CONTROLLER
# ==============================================================================
def run_backtracking_simulation(lat, lon, start_time, days, particles, out_filename,
                              radius=300, windage=0.02, coastline="stranding",
                              buffer=0.05, plot=True, verbose=False, output_dir=None):
    """
    Core simulation logic that can be called from CLI or API.
    Returns a dictionary of generated file paths.
    """
    # Determine output directory
    if output_dir:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        config.ensure_directories()
        out_dir = config.OUTPUT_DIR

    if isinstance(start_time, str):
        t_start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    else:
        t_start = start_time
    
    # Track temp files for cleanup
    temp_files = []

    try:
        # ---------------------------------------------------------
        # 1. Data Preparation Phase
        # ---------------------------------------------------------
        # Initialize readers to None for cleanup
        reader_era5 = None
        reader_hycom = None

        try:
            path_era5 = prepare_merged_dataset("era5", t_start, days, lat, lon)
            temp_files.append(path_era5)
            path_hycom = prepare_merged_dataset("hycom", t_start, days, lat, lon)
            temp_files.append(path_hycom)
        except FileNotFoundError as e:
            logger.critical("Simulation aborted due to missing data.")
            raise RuntimeError(f"Missing data: {e}")
        except Exception as e:
            logger.critical(f"Unexpected error during data preparation: {e}")
            raise RuntimeError(f"Data preparation error: {e}")

        # ---------------------------------------------------------
        # 2. Model Initialization
        # ---------------------------------------------------------
        logger.info("Initializing LitterDrift Model...")
        o = LitterDrift(loglevel=20) # 20 = INFO level
        
        try:
            reader_era5 = reader_netCDF_CF_generic.Reader(path_era5)
            reader_hycom = reader_netCDF_CF_generic.Reader(path_hycom)
            o.add_reader([reader_hycom, reader_era5])
            logger.info("Readers loaded successfully.")
            
            # Verbose debugging for forces
            if verbose:
                logger.info(f"ERA5 Variables: {reader_era5.variables}")
                
        except Exception as e:
            logger.critical(f"Failed to initialize readers: {e}")
            raise RuntimeError(f"Reader initialization failed: {e}")

        # ---------------------------------------------------------
        # 3. Physics Configuration
        # ---------------------------------------------------------
        o.set_config('drift:vertical_mixing', False)
        o.set_config('drift:advection_scheme', 'runge-kutta4')
        # 'previous' allows particles to slide along coastlines
        logger.info(f"Coastline behavior set to: {coastline}")
        o.set_config('general:coastline_action', coastline)

        # ---------------------------------------------------------
        # 4. Seeding (Release Particles)
        # ---------------------------------------------------------
        logger.info(f"Seeding {particles} particles at Lat: {lat}, Lon: {lon}")
        o.seed_elements(
            lat=lat, 
            lon=lon, 
            radius=radius,
            number=particles, 
            time=t_start,
            wind_drift_factor=windage
        )

        # ---------------------------------------------------------
        # 5. Execution (Backtracking)
        # ---------------------------------------------------------
        out_file = out_dir / out_filename
        if out_file.exists():
            os.remove(out_file)
        
        logger.info(f"Starting backtracking simulation for {days} days...")
        
        try:
            o.run(
                duration=timedelta(days=days),
                time_step=-3600,       # Backwards in time
                time_step_output=3600, # Output every hour
                outfile=str(out_file)
            )
            logger.info(f"Simulation completed successfully.")
            logger.info(f"Result saved to: {out_file}")
        except Exception as e:
            logger.critical(f"Simulation crashed during runtime: {e}")
            raise RuntimeError(f"Simulation execution failed: {e}")

        # ---------------------------------------------------------
        # 6. Visualization & Result Collection
        # ---------------------------------------------------------
        generated_files = {
            "netcdf": str(out_file)
        }

        # ---------------------------------------------------------
        # 7. Statistics Calculation
        # ---------------------------------------------------------
        try:
            ds = xr.open_dataset(out_file)
            
            # Check if we have valid data
            if 'lon' in ds and 'lat' in ds and ds.lon.size > 0:
                lons = ds.lon.values
                lats = ds.lat.values
                
                # Calculate distance between consecutive steps
                # Shape: (trajectory, time)
                # We need to handle cases where there is only 1 time step
                if lons.shape[1] > 1:
                    lons_1 = lons[:, :-1]
                    lats_1 = lats[:, :-1]
                    lons_2 = lons[:, 1:]
                    lats_2 = lats[:, 1:]
                    
                    # Calculate segment distances
                    dists = haversine_np(lons_1, lats_1, lons_2, lats_2)
                    
                    # Sum distance per particle (ignoring NaNs)
                    total_dists = np.nansum(dists, axis=1)
                    
                    # Mean distance (km)
                    mean_dist_km = np.mean(total_dists)
                    
                    # Mean speed (m/s)
                    # Distance (km) * 1000 / Time (s)
                    duration_seconds = days * 24 * 3600
                    if duration_seconds > 0:
                        mean_speed_ms = (mean_dist_km * 1000) / duration_seconds
                    else:
                        mean_speed_ms = 0.0
                    
                    # Calculate Drift Direction (Source -> Sink)
                    # Source is average of last positions (Past, index -1)
                    # Sink is average of first positions (Present, index 0) - or just user input lat/lon
                    
                    # Average position at t=end (Past)
                    # Note: some particles might be stranded earlier, but we take the last recorded position
                    
                    # Filter valid last positions
                    last_lons = lons[:, -1]
                    last_lats = lats[:, -1]
                    
                    # Ignore NaNs if any
                    valid_mask = ~np.isnan(last_lons) & ~np.isnan(last_lats)
                    
                    if np.any(valid_mask):
                        mean_source_lon = np.mean(last_lons[valid_mask])
                        mean_source_lat = np.mean(last_lats[valid_mask])
                        
                        # Sink is the release point (t=0)
                        mean_sink_lon = np.mean(lons[:, 0])
                        mean_sink_lat = np.mean(lats[:, 0])
                        
                        # Calculate bearing from Source to Sink (Direction of flow)
                        bearing = calculate_bearing(mean_source_lat, mean_source_lon, mean_sink_lat, mean_sink_lon)
                        cardinal_dir = get_cardinal_direction(bearing)
                    else:
                        cardinal_dir = "Tidak diketahui"
    
                    generated_files["stats"] = {
                        "mean_distance_km": float(mean_dist_km),
                        "mean_speed_ms": float(mean_speed_ms),
                        "dominant_direction": cardinal_dir
                    }
                    logger.info(f"Statistics: Mean Distance={mean_dist_km:.2f} km, Mean Speed={mean_speed_ms:.4f} m/s, Direction={cardinal_dir}")
                else:
                    generated_files["stats"] = {"mean_distance_km": 0.0, "mean_speed_ms": 0.0, "dominant_direction": "N/A"}
            else:
                generated_files["stats"] = {"mean_distance_km": 0.0, "mean_speed_ms": 0.0, "dominant_direction": "N/A"}
                
            ds.close()
        except Exception as e:
            logger.warning(f"Failed to calculate statistics: {e}")
            generated_files["stats"] = {"mean_distance_km": 0.0, "mean_speed_ms": 0.0, "dominant_direction": "Error"}

        if plot:
            nc_path = str(out_file)

            # Animation (GIF)
            anim_file = str(out_file).replace('.nc', '.gif')
            try:
                # Generate animation without title (title="")
                o.animation(filename=anim_file, buffer=buffer, fast=False, title="")
                generated_files["animation"] = anim_file
                logger.info(f"Animation saved: {anim_file}")
            except Exception as e:
                logger.warning(f"Failed to generate animation: {e}")
            
            # Option A: OpenStreetMap (OSM)
            osm_file = str(out_file).replace('.nc', '_osm.png')
            try:
                generate_realistic_map(nc_path, osm_file, buffer=buffer, map_type='osm')
                generated_files["osm_plot"] = osm_file
            except Exception as e:
                logger.warning(f"Failed to generate OSM plot: {e}")
            
            # Note: Satellite, Base, and Interactive HTML plots are currently disabled.


        return generated_files

    finally:
        # Close readers to release file locks
        if reader_era5 is not None and hasattr(reader_era5, 'Dataset'):
            try:
                reader_era5.Dataset.close()
                logger.info("Closed ERA5 reader dataset.")
            except Exception as e:
                logger.warning(f"Failed to close ERA5 reader: {e}")
        
        if reader_hycom is not None and hasattr(reader_hycom, 'Dataset'):
            try:
                reader_hycom.Dataset.close()
                logger.info("Closed HYCOM reader dataset.")
            except Exception as e:
                logger.warning(f"Failed to close HYCOM reader: {e}")

        # Cleanup temp files
        for f in temp_files:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                    logger.info(f"Cleaned up temporary file: {f}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file {f}: {e}")

def run_simulation(args):
    """Wrapper for CLI arguments"""
    try:
        run_backtracking_simulation(
            lat=args.lat,
            lon=args.lon,
            start_time=args.start_time,
            days=args.days,
            particles=args.particles,
            out_filename=args.out,
            radius=args.radius,
            windage=args.windage,
            coastline=args.coastline,
            buffer=args.buffer,
            plot=args.plot,
            verbose=args.verbose
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Litter Drift Simulation Engine (Backtracking)")
    
    # Coordinates & Time Arguments
    parser.add_argument("--lat", type=float, required=True, help="Target Latitude (Start Point)")
    parser.add_argument("--lon", type=float, required=True, help="Target Longitude (Start Point)")
    parser.add_argument("--start_time", required=True, help="Simulation Start Time (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--days", type=int, default=7, help="Duration of backtracking in days")
    
    # Physics & Model Arguments
    parser.add_argument(
        "--coastline", type=str, default="stranding", choices=["previous", "stranding", "none"],
        help="Coastline interaction: 'previous' (slide), 'stranding' (stop), 'none' (ignore land)"
    )
    parser.add_argument("--particles", type=int, default=30, help="Number of particles")
    parser.add_argument("--radius", type=int, default=300, help="Radius of seeding area (meters)")
    parser.add_argument("--windage", type=float, default=0.02, help="Wind drift factor (0.02 = 2%)")
    
    # Output Arguments
    parser.add_argument("--out", default="simulation_result.nc", help="Output NetCDF filename")
    parser.add_argument("--buffer", type=float, default=0.05, help="Map zoom buffer (deg)")
    parser.add_argument("--plot", action="store_true", help="Generate trajectory plots")
    parser.add_argument("--verbose", action="store_true", help="Log detailed info")

    args = parser.parse_args()
    
    run_simulation(args)