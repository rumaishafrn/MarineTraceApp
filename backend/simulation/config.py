import os
from pathlib import Path
from datetime import datetime

# ==============================================================================
# GLOBAL CONFIGURATION
# ==============================================================================

# Paths using Pathlib for OS-agnostic handling
BASE_DIR = Path(__file__).resolve().parent
DATA_REPO_DIR = BASE_DIR / "data_repository"  # Persistent storage for daily files
TEMP_RUNTIME_DIR = BASE_DIR / "temp_runtime"  # Temporary merged files for simulation
OUTPUT_DIR = BASE_DIR / "simulation_output"   # Final results

def set_output_dir(path: Path):
    """Allows overriding the output directory (e.g., for Flask static folder)."""
    global OUTPUT_DIR
    OUTPUT_DIR = Path(path)

def ensure_directories() -> None:
    """Creates necessary directories if they do not exist."""
    DATA_REPO_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_daily_filename(source: str, date_obj: datetime, lat: float, lon: float) -> str:
    """
    Generates a standardized filename for daily data.
    Format: source_YYYY-MM-DD_lat_lon.nc
    """
    date_str = date_obj.strftime("%Y-%m-%d")
    return f"{source}_{date_str}_{lat:.1f}_{lon:.1f}.nc"

def get_bbox(lat: float, lon: float, buffer: float) -> list:
    """Returns Bounding Box [North, West, South, East]."""
    return [lat + buffer, lon - buffer, lat - buffer, lon + buffer]
