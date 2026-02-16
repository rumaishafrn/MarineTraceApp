"""
Script untuk membuat dummy YOLO model untuk testing
HANYA UNTUK DEVELOPMENT - Ganti dengan model asli Anda untuk production!
"""

import torch
import os

def create_dummy_model():
    """
    Create a minimal dummy YOLO model for testing purposes
    This is NOT a real trained model - just for testing the pipeline
    """
    
    print("Creating dummy YOLO model for testing...")
    print("⚠️  WARNING: This is NOT a real model! Replace with your trained model!")
    
    # Create models directory (relative to backend root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    models_dir = os.path.join(backend_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Create a minimal model structure
    # This structure is too simple for recent ultralytics versions which expect more attributes
    # Instead, we will use a small real model if possible, or skip loading it in tests if it's dummy
    # But for now let's try to mimic a structure that might pass basic checks or just save a dict
    # that our test code can recognize as "dummy" and handle gracefully if needed.
    
    # Actually, ultralytics YOLO() expects a file that can be loaded by torch.load and has specific keys.
    # Creating a valid YOLO model from scratch is hard.
    # Better approach for dummy: Create a file that we can check existence of, but for loading test
    # we might need to mock or skip if it's not a real model.
    
    # However, to make the test pass with the "dummy" model, we can try to save a resnet18 or similar
    # as a placeholder if we just want to test 'loading', but YOLO class expects specific structure.
    
    # Alternative: Use a tiny real YOLO model (yolov8n.pt) if available, or just create a text file
    # and catch the error in the test script saying "It's a dummy file".
    
    # Let's create a simple dict that MIGHT fail load but proves file creation works.
    model_dict = {
        'model': None,
        'train_args': {},  # Added to satisfy some checks
        'names': {
            0: 'plastic_bag',
            1: 'bottle', 
            2: 'wrapper'
        }
    }
    
    # Save dummy model
    model_path = os.path.join(models_dir, 'best.pt')
    torch.save(model_dict, model_path)
    print(f"✅ Dummy model created at: {model_path}")
    print("")
    print("To use this dummy model:")
    print("1. Update app.py line 20:")
    print("   MODEL_PATH = os.path.join(BASE_DIR, 'models', 'dummy.pt')")
    print("")
    print("2. Or copy your real model:")
    print("   cp your-real-model.pt backend/models/best.pt")
    print("")

if __name__ == "__main__":
    try:
        create_dummy_model()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have PyTorch installed:")
        print("pip install torch --break-system-packages")
