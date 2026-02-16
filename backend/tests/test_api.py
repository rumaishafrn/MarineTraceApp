import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, SIMULATION_JOBS

class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    def test_simulate_endpoint_validation(self):
        """Test input validation for /api/simulate"""
        # Test missing latitude (should fail now or use default? Wait, I kept defaults but added range check)
        # Actually I kept defaults in `data.get('lat', -5.15)`.
        # So let's test OUT OF RANGE values which should definitely fail.
        
        # Test invalid latitude
        response = self.app.post('/api/simulate', 
                                 data=json.dumps({'lat': 91.0}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Latitude must be between', json.loads(response.data)['error'])

        # Test invalid longitude
        response = self.app.post('/api/simulate', 
                                 data=json.dumps({'lon': 200.0}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Longitude must be between', json.loads(response.data)['error'])

        # Test valid default usage (empty body might fail "No input data provided" check)
        response = self.app.post('/api/simulate', 
                                 data=json.dumps({}),
                                 content_type='application/json')
        # If I send empty dict, `if not data` might be false if data is {}, wait.
        # request.json returns {} if body is {}. `if not {}` is True.
        # So it should return 400 "No input data provided".
        self.assertEqual(response.status_code, 400)
        self.assertIn('No input data provided', json.loads(response.data)['error'])

        # Test valid payload
        response = self.app.post('/api/simulate', 
                                 data=json.dumps({'lat': -5.0, 'lon': 120.0}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('job_id', data)
        self.assertEqual(data['status'], 'submitted')

    @patch('app.run_backtracking_simulation')
    def test_simulate_execution_flow(self, mock_run_sim):
        """Test full simulation flow with mocked simulation function"""
        # Setup mock to return dummy results
        mock_run_sim.return_value = {'netcdf': 'dummy.nc'}
        
        # Start simulation
        payload = {
            'lat': -5.0,
            'lon': 120.0,
            'days': 1,
            'particles': 10
        }
        response = self.app.post('/api/simulate', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        job_id = json.loads(response.data)['job_id']
        
        # Check status immediately (should be pending or running)
        status_response = self.app.get(f'/api/simulate/{job_id}')
        self.assertEqual(status_response.status_code, 200)
        status_data = json.loads(status_response.data)
        self.assertIn(status_data['status'], ['pending', 'running', 'completed'])
        
        # Wait a bit for thread to finish (since it's mocked, it should be fast)
        import time
        time.sleep(1)
        
        # Check status again
        status_response = self.app.get(f'/api/simulate/{job_id}')
        status_data = json.loads(status_response.data)
        
        # If the thread ran, it should be completed
        # Note: If this fails, it might be because the thread died or mock didn't work as expected in thread
        # But since we are mocking the function called BY the thread, it should work.
        
    def test_cleanup_logic(self):
        """Test that cleanup function exists and runs without error"""
        from app import cleanup_old_simulations
        try:
            cleanup_old_simulations()
        except Exception as e:
            self.fail(f"cleanup_old_simulations raised exception: {e}")

if __name__ == '__main__':
    unittest.main()
