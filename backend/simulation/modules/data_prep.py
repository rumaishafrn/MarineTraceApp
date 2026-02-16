import logging
import uuid
import xarray as xr
from datetime import datetime, timedelta
from .. import config

logger = logging.getLogger(__name__)

def prepare_merged_dataset(
    source: str, 
    start_date: datetime, 
    days: int, 
    lat: float, 
    lon: float
) -> str:
    """
    Identifies required daily files and merges them into a temporary runtime file.

    Args:
        source (str): 'era5' or 'hycom'.
        start_date (datetime): Simulation start time.
        days (int): Duration of backtracking.
        lat (float): Target latitude.
        lon (float): Target longitude.

    Returns:
        str: Path to the merged NetCDF file.

    Raises:
        FileNotFoundError: If a single daily file is missing.
    """
    # Calculate time range: Start - Duration (Backwards) + Buffer
    req_start = start_date - timedelta(days=days + 1)
    req_end = start_date + timedelta(days=2)
    
    logger.info(f"Preparing {source.upper()} dataset...")
    logger.info(f"Target Data Range: {req_start.date()} to {req_end.date()}")
    
    files_to_merge = []
    curr = req_start
    
    # Loop through every day in the required range
    while curr <= req_end:
        fname = config.get_daily_filename(source, curr, lat, lon)
        fpath = config.DATA_REPO_DIR / fname
        
        if fpath.exists():
            files_to_merge.append(fpath)
        else:
            # STRICT MODE: Stop immediately if a file is missing
            error_msg = (
                f"Missing required daily file: {fname}. "
                f"Please run the downloader script for date: {curr.date()}"
            )
            logger.critical(error_msg)
            raise FileNotFoundError(error_msg)
            
        curr += timedelta(days=1)

    # Merge files
    unique_id = uuid.uuid4().hex[:8]
    merged_path = config.TEMP_RUNTIME_DIR / f"merged_run_{source}_{unique_id}.nc"
    logger.info(f"Merging {len(files_to_merge)} daily files into temporary dataset: {merged_path}")
    
    try:
        # Sort files to ensure correct time ordering
        files_to_merge.sort()
        # Open and merge using xarray
        with xr.open_mfdataset(files_to_merge, combine='by_coords') as ds:
            ds.to_netcdf(merged_path)
    except Exception as e:
        logger.error(f"Failed to merge {source} files: {e}")
        raise RuntimeError(f"Merge failed: {e}")
        
    return str(merged_path)