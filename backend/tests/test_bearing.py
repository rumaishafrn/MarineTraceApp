
import sys
import os
import numpy as np
import logging

# Add backend dir to path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
    print(f"Added {BACKEND_DIR} to sys.path")

from simulation.litter_simulation import calculate_bearing, get_cardinal_direction

def test_bearing():
    # Test 1: North (0/360)
    # Lat increases, Lon same
    b1 = calculate_bearing(0, 0, 1, 0)
    d1 = get_cardinal_direction(b1)
    print(f"0,0 -> 1,0 (North): {b1:.2f}, {d1}")
    assert d1 == "Utara"

    # Test 2: East (90)
    # Lat same, Lon increases
    b2 = calculate_bearing(0, 0, 0, 1)
    d2 = get_cardinal_direction(b2)
    print(f"0,0 -> 0,1 (East): {b2:.2f}, {d2}")
    assert d2 == "Timur"
    
    # Test 3: South (180)
    # Lat decreases, Lon same
    b3 = calculate_bearing(0, 0, -1, 0)
    d3 = get_cardinal_direction(b3)
    print(f"0,0 -> -1,0 (South): {b3:.2f}, {d3}")
    assert d3 == "Selatan"

    # Test 4: West (270)
    # Lat same, Lon decreases
    b4 = calculate_bearing(0, 0, 0, -1)
    d4 = get_cardinal_direction(b4)
    print(f"0,0 -> 0,-1 (West): {b4:.2f}, {d4}")
    assert d4 == "Barat"
    
    # Test 5: Northeast (45)
    b5 = calculate_bearing(0, 0, 1, 1)
    d5 = get_cardinal_direction(b5)
    print(f"0,0 -> 1,1 (NE): {b5:.2f}, {d5}")
    assert d5 == "Timur Laut"

if __name__ == "__main__":
    try:
        test_bearing()
        print("Bearing test passed!")
    except Exception as e:
        print(f"Test failed: {e}")
