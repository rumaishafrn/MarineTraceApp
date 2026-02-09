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
    
    # Create models directory
    os.makedirs('backend/models', exist_ok=True)
    
    # Create a minimal model structure
    model_dict = {
        'model': None,  # Simplified for dummy
        'names': {
            0: 'plastic_bag',
            1: 'bottle', 
            2: 'wrapper'
        }
    }
    
    # Save dummy model
    dummy_path = 'backend/models/dummy.pt'
    torch.save(model_dict, dummy_path)
    
    print(f"✅ Dummy model created at: {dummy_path}")
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
