import logging
import numpy as np
import xarray as xr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

logger = logging.getLogger(__name__)

def calculate_optimal_zoom(min_lon: float, max_lon: float, min_lat: float, max_lat: float) -> int:
    """
    Calculates the optimal zoom level for map tiles based on the plot extent.
    """
    lon_span = max_lon - min_lon
    lat_span = max_lat - min_lat
    max_span = max(lon_span, lat_span)

    if max_span <= 0:
        return 12 

    try:
        # Logarithmic scaling for zoom level
        zoom = int(np.round(np.log2(1440.0 / max_span)))
    except:
        zoom = 12 

    # Clamp zoom level (OSM standard 0-19)
    return max(10, min(17, zoom))

def generate_realistic_map(nc_file_path: str, output_png_path: str, buffer: float = 0.1, map_type: str = 'osm'):
    """
    Generates a High-Quality PNG with smoothed trajectories using Cartopy.
    """
    logger.info(f"Generating high-res map ({map_type.upper()}) from {nc_file_path}...")
    
    try:
        ds = xr.open_dataset(nc_file_path)
        # TRANSPOSE FIX: Ensure dimensions are (Time, Particle) for correct plotting
        lons = ds.lon.values.T
        lats = ds.lat.values.T
        ds.close()
    except Exception as e:
        logger.error(f"Failed to read NetCDF for plotting: {e}")
        return

    # Select Map Provider
    if map_type == 'satellite':
        tiler = cimgt.GoogleTiles(style='satellite')
    else:
        tiler = cimgt.OSM()

    # Setup Figure
    plt.figure(figsize=(15, 12), dpi=300) 
    ax = plt.axes(projection=tiler.crs)
    
    # Calculate Extent
    min_lon, max_lon = np.nanmin(lons), np.nanmax(lons)
    min_lat, max_lat = np.nanmin(lats), np.nanmax(lats)
    
    extent = [
        min_lon - buffer, max_lon + buffer,
        min_lat - buffer, max_lat + buffer
    ]
    try:
        ax.set_extent(extent, crs=ccrs.PlateCarree())
    except: 
        pass

    # Add Background Tiles (Auto-Zoom)
    zoom_level = calculate_optimal_zoom(min_lon, max_lon, min_lat, max_lat)
    if map_type == 'satellite' and zoom_level > 11: 
        zoom_level -= 1
    logger.info(f"Downloading map tiles (Zoom: {zoom_level})...")
    ax.add_image(tiler, zoom_level)

    # Plot Trajectories
    logger.info("Plotting trajectories...")
    
    total_particles = lons.shape[1]
    step = 10 if total_particles > 100 else 1
    
    for i in range(0, total_particles, step):
        valid_idx = ~np.isnan(lons[:, i])
        
        if np.any(valid_idx):
            # Trajectory Line
            ax.plot(
                lons[valid_idx, i], lats[valid_idx, i], 
                transform=ccrs.Geodetic(), # Creates natural curved lines
                color='red', 
                linewidth=1.0, 
                alpha=0.6
            )
            
            # Start Point
            first_idx = np.where(valid_idx)[0][0]
            ax.scatter(
                lons[first_idx, i], lats[first_idx, i],
                transform=ccrs.PlateCarree(),
                color='#00FF00', edgecolor='black', s=30, zorder=10, marker='o'
            )
            
            # End Point
            last_idx = np.where(valid_idx)[0][-1]
            ax.scatter(
                lons[last_idx, i], lats[last_idx, i],
                transform=ccrs.PlateCarree(),
                color='yellow', edgecolor='black', s=30, zorder=10, marker='X'
            )

    # Legend
    legend_start = mlines.Line2D([], [], color='#00FF00', markeredgecolor='black', marker='o', linestyle='None', label='Observation (Now)')
    legend_end = mlines.Line2D([], [], color='yellow', markeredgecolor='black', marker='X', linestyle='None', label='Estimated Source (Past)')
    legend_path = mlines.Line2D([], [], color='red', linewidth=1, label=f'Backtracking Path')
    
    legend = plt.legend(handles=[legend_start, legend_end, legend_path], loc='upper right', frameon=True)
    legend.get_frame().set_alpha(0.9)
    
    # plt.title(f"Litter Drift Simulation ({map_type.upper()})", fontsize=16, weight='bold')
    plt.savefig(output_png_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Map saved: {output_png_path}")