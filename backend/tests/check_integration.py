
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import shutil

# Add the backend directory to sys.path so we can import 'simulation' package
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Mock modules that might not be installed or require heavy data
sys.modules['opendrift'] = MagicMock()
sys.modules['opendrift.readers'] = MagicMock()
sys.modules['opendrift.readers.reader_netCDF_CF_generic'] = MagicMock()
sys.modules['opendrift.models'] = MagicMock()
sys.modules['opendrift.models.oceandrift'] = MagicMock()

# Now we can import the simulation module
try:
    from simulation.litter_simulation import run_backtracking_simulation
except ImportError as e:
    print(f"ImportError: {e}")
    # If the import fails due to other dependencies, we need to mock them too
    # Assuming config, modules.physics, modules.data_prep, modules.visualization exist
    # If not, we might need to mock them. 
    # Let's try to mock the internal modules of litter_simulation if the import fails
    pass

class TestSimulationIntegration(unittest.TestCase):
    
    def setUp(self):
        self.output_dir = os.path.join(BACKEND_DIR, 'tests', 'temp_output')
        os.makedirs(self.output_dir, exist_ok=True)
        
    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_run_simulation_mock(self):
        # Import inside the test method to ensure sys.path is set
        from simulation import litter_simulation
        
        # Patch dependencies on the imported module object
        with patch.object(litter_simulation, 'prepare_merged_dataset') as mock_prepare, \
             patch.object(litter_simulation, 'LitterDrift') as MockLitterDrift:
            
            # Setup mocks
            mock_prepare.return_value = "dummy_path.nc"
            
            mock_drift_instance = MockLitterDrift.return_value
            # Mock the run method to create a dummy output file
            def side_effect_run(**kwargs):
                outfile = kwargs.get('outfile')
                if outfile:
                    # Create a dummy NetCDF file
                    with open(outfile, 'w') as f:
                        f.write("dummy netcdf content")
            mock_drift_instance.run.side_effect = side_effect_run
            
            # Mock plot method
            def side_effect_plot(**kwargs):
                filename = kwargs.get('filename')
                if filename:
                    with open(filename, 'w') as f:
                        f.write("dummy plot content")
            mock_drift_instance.plot.side_effect = side_effect_plot
            
            # Mock animation
            def side_effect_animation(**kwargs):
                filename = kwargs.get('filename')
                if filename:
                    with open(filename, 'w') as f:
                        f.write("dummy animation content")
            mock_drift_instance.animation.side_effect = side_effect_animation

            # Parameters
            lat = -5.15
            lon = 119.42
            start_time = "2023-01-01 12:00:00"
            days = 1
            particles = 10
            out_filename = "test_sim.nc"
            
            # Run simulation
            try:
                results = litter_simulation.run_backtracking_simulation(
                    lat, lon, start_time, days, particles, out_filename,
                    plot=True, verbose=True, output_dir=self.output_dir
                )
                
                print("Simulation returned:", results)
                
                # Verify output files exist
                self.assertIn('netcdf', results)
                self.assertTrue(os.path.exists(results['netcdf']))
                # The plot might be .png, need to check if simulation code appends extension
                # In run_backtracking_simulation, usually plot() adds extension if not present
                # Let's assume the mock behavior handles it or the function does.
                
                # Check if function respected output_dir
                self.assertTrue(results['netcdf'].startswith(self.output_dir))
                
            except Exception as e:
                self.fail(f"Simulation failed with error: {e}")

if __name__ == '__main__':
    unittest.main()
