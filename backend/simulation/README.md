# MarineTrace Simulation Engine

A Python-based simulation system for tracking the drift of marine litter using oceanographic and atmospheric data from ERA5 and HYCOM sources.
Now integrated as a module within the MarineTrace backend.

## Usage

This module is designed to be used by the Flask backend, but can also be run via CLI for testing.

### Running via CLI

From the `backend` directory:

```bash
python -m simulation.litter_simulation --lat -5.15 --lon 119.42 --start_time "2024-06-28 12:00:00" --days 3 --plot
```

**Note**: Always run as a module (`-m`) to ensure relative imports work correctly.

## Project Structure

```
simulation/
├── config.py              # Global configuration and path management
├── era5_downloader.py     # Downloads and processes ERA5 atmospheric data
├── hycom_downloader.py    # Downloads and processes HYCOM ocean current data
├── litter_simulation.py   # Main simulation controller
├── modules/
│   ├── data_prep.py       # Data preprocessing and merging utilities
│   ├── physics.py         # Litter drift physics implementation
│   └── visualization.py   # Map generation and visualization tools
├── data_repository/       # Persistent storage for daily data files
├── temp_runtime/          # Temporary merged files for simulations
└── simulation_output/     # Final simulation results
```

## Dependencies

- Python 3.7+
- OpenDrift
- xarray
- numpy
- cdsapi (for ERA5 data)
- netCDF4
- matplotlib
- cartopy

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pair-particle-drift.git
   cd pair-particle-drift
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up CDS API key for ERA5 data:
   - Create an account at [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/)
   - Install the API key in your system configuration

## Usage

### Download Data

**ERA5 Atmospheric Data:**
```bash
python era5_downloader.py 2024-01-01 2024-01-31 25.5 -80.5
```

**HYCOM Ocean Current Data:**
```bash
python hycom_downloader.py 2024-01-01 2024-01-31 25.5 -80.5
```

### Run Simulation

```bash
python litter_simulation.py \
    --start_time "2024-01-01 00:00:00" \
    --days 30 \
    --lat 25.5 \
    --lon -80.5 \
    --num_particles 1000
```

### Parameters

- `--start_time`: Simulation start time (format: YYYY-MM-DD HH:MM:SS)
- `--days`: Number of days to simulate
- `--lat`: Latitude (degrees)
- `--lon`: Longitude (degrees)
- `--num_particles`: Number of particles to simulate

## Data Sources

### ERA5
- Provides atmospheric reanalysis data
- Variables: 10m wind components, wave parameters, Stokes drift
- Temporal resolution: Hourly
- Spatial resolution: ~0.25°

### HYCOM
- Provides ocean current data
- Variables: Eastward and northward water velocities
- Temporal resolution: 3-hourly
- Spatial resolution: 1/12° (~9km)

## Configuration

The `config.py` file manages:
- Directory paths for data storage
- Filename conventions for daily data
- Bounding box calculations for data downloads

## Output

Simulations generate:
- Particle trajectory data (NetCDF format)
- Visualization maps (PNG format)
- Summary statistics and logs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenDrift](https://github.com/OpenDrift/opendrift) - Framework for modeling ocean drift
- [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/) - ERA5 data provider
- [HYCOM Consortium](https://www.hycom.org/) - Ocean current data provider