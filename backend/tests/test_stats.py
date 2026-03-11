
import sys
import os
import numpy as np
import logging

# Add backend dir to path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
    print(f"Added {BACKEND_DIR} to sys.path")

from simulation.litter_simulation import haversine_np

def test_haversine():
    # Test case: Distance between Jakarta (-6.2088, 106.8456) and Bandung (-6.9175, 107.6191)
    # Expected approx 120 km
    lat1, lon1 = -6.2088, 106.8456
    lat2, lon2 = -6.9175, 107.6191
    
    dist = haversine_np(lon1, lat1, lon2, lat2)
    print(f"Distance Jakarta-Bandung: {dist:.2f} km")
    
    # Test array inputs
    lons1 = np.array([100, 100])
    lats1 = np.array([0, 0])
    lons2 = np.array([101, 100]) # 1 deg lon diff at equator (~111km), 0 diff
    lats2 = np.array([0, 1])     # 0 diff, 1 deg lat diff (~111km)
    
    dists = haversine_np(lons1, lats1, lons2, lats2)
    print(f"Array distances: {dists}")
    assert np.allclose(dists, [111.19, 111.19], atol=1.0) # Approx check

if __name__ == "__main__":
    try:
        test_haversine()
        print("Haversine test passed!")
    except ImportError:
        print("Could not import litter_simulation. Check paths.")
    except Exception as e:
        print(f"Test failed: {e}")
