import numpy as np
import logging
from opendrift.models.oceandrift import OceanDrift

logger = logging.getLogger(__name__)

class LitterDrift(OceanDrift):
    """
    Custom Lagrangian model for Marine Debris Backtracking.
    
    Forces applied:
    1. Ocean Currents (HYCOM)
    2. Windage / Leeway (ERA5 Wind)
    3. Stokes Drift (ERA5 Waves)
    """
    
    # Define variables stored on each particle
    class ElementType(OceanDrift.ElementType):
        variables = OceanDrift.ElementType.variables.copy()
        variables.update({
            'wind_drift_factor': {'dtype': np.float32, 'units': '1', 'default': 0.02},
            'sea_surface_wave_stokes_drift_x_velocity': {'dtype': np.float32, 'units': 'm/s', 'default': 0},
            'sea_surface_wave_stokes_drift_y_velocity': {'dtype': np.float32, 'units': 'm/s', 'default': 0}
        })

    # Define variables required from external NetCDF readers
    required_variables = {
        'x_sea_water_velocity': {'fallback': 0}, 
        'y_sea_water_velocity': {'fallback': 0},
        'x_wind': {'fallback': 0}, 
        'y_wind': {'fallback': 0},
        'sea_surface_wave_stokes_drift_x_velocity': {'fallback': 0}, 
        'sea_surface_wave_stokes_drift_y_velocity': {'fallback': 0}, 
        'land_binary_mask': {'fallback': None},
    }

    def update(self):
        """
        Update particle positions based on physical forces at each time step.
        """
        # 1. Advect by Ocean Current (HYCOM)
        self.advect_ocean_current()
        
        # 2. Advect by Wind (ERA5)
        self.advect_wind()
        
        # 3. Advect by Stokes Drift (ERA5)
        # Retrieved directly from the environment (Reader)
        u_stokes = self.environment.sea_surface_wave_stokes_drift_x_velocity
        v_stokes = self.environment.sea_surface_wave_stokes_drift_y_velocity
        self.update_positions(u_stokes, v_stokes)
        
        # Store values for post-analysis
        self.elements.sea_surface_wave_stokes_drift_x_velocity = u_stokes
        self.elements.sea_surface_wave_stokes_drift_y_velocity = v_stokes