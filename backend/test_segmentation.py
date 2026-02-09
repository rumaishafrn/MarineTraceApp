"""
Test script khusus untuk YOLO Segmentation Model
Gunakan untuk test model segmentation Anda dengan gambar asli
"""

from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
import sys

def test_segmentation_model(image_path=None):
    """
    Test YOLO segmentation model dengan gambar
    
    Args:
        image_path: Path ke gambar test. Jika None, akan pakai dummy image
    """
    
    print("="*60)
    print("YOLO Segmentation Model Tester")
    print("="*60)
    print()
    
    # Load model
    model_path = 'models/best.pt'
    
    try:
        print(f"Loading model from: {model_path}")
        model = YOLO(model_path)
        print("✅ Model loaded successfully!")
        print()
        
        # Print model info
        print("📊 Model Information:")
        print(f"   Task: {model.task}")
        print(f"   Classes: {model.names}")
        print(f"   Number of classes: {len(model.names)}")
        print()
        
        if model.task != 'segment':
            print("⚠️  WARNING: Model task is not 'segment'")
            print(f"   Current task: {model.task}")
            print("   This might not be a segmentation model!")
            print()
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False
    
    # Prepare image
    if image_path and Path(image_path).exists():
        print(f"Using image: {image_path}")
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Error: Could not read image from {image_path}")
            return False
    else:
        if image_path:
            print(f"⚠️  Image not found: {image_path}")
        print("Creating dummy test image (640x640)...")
        # Create more realistic test image with some patterns
        image = np.random.randint(50, 200, (640, 640, 3), dtype=np.uint8)
    
    print(f"Image shape: {image.shape}")
    print()
    
    # Run inference
    print("Running inference...")
    try:
        results = model(image, verbose=False)
        print("✅ Inference successful!")
        print()
        
    except Exception as e:
        print(f"❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Process results
    result = results[0]
    boxes = result.boxes
    
    print("📋 Detection Results:")
    print(f"   Total objects detected: {len(boxes)}")
    
    if len(boxes) == 0:
        if image_path:
            print("   ⚠️  No objects detected in the image")
            print("   Try with a different image or check confidence threshold")
        else:
            print("   ℹ️  No objects detected (expected with random image)")
    else:
        print()
        print("   Detected objects:")
        for i, box in enumerate(boxes):
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = model.names[cls_id]
            
            # Get box coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            print(f"   {i+1}. {class_name}")
            print(f"      - Confidence: {conf:.2%}")
            print(f"      - BBox: ({x1:.0f}, {y1:.0f}) to ({x2:.0f}, {y2:.0f})")
    
    print()
    
    # Check for masks (segmentation)
    if hasattr(result, 'masks') and result.masks is not None:
        masks = result.masks
        print("✅ Segmentation Masks Found!")
        print(f"   Number of masks: {len(masks)}")
        print(f"   Mask shape: {masks.data.shape}")
        print()
        print("   🎉 This is a SEGMENTATION model - masks are working!")
    else:
        print("⚠️  No segmentation masks found")
        print("   This might be a detection model, not segmentation")
    
    print()
    
    # Save result
    print("Saving result image...")
    try:
        # Plot with boxes and masks (if available)
        result_img = result.plot()
        
        # Convert RGB to BGR for cv2
        result_img_bgr = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)
        
        output_path = 'test_segmentation_result.jpg'
        cv2.imwrite(output_path, result_img_bgr)
        
        print(f"✅ Result saved to: {output_path}")
        
        if hasattr(result, 'masks') and result.masks is not None:
            print("   The image should show colored masks over detected objects!")
        else:
            print("   The image should show bounding boxes over detected objects")
        
    except Exception as e:
        print(f"❌ Error saving result: {e}")
    
    print()
    print("="*60)
    print("Test Complete!")
    print("="*60)
    
    return True


def main():
    """Main function"""
    
    # Check if image path provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"\nTesting with image: {image_path}\n")
        test_segmentation_model(image_path)
    else:
        print("\nNo image provided. Using dummy image for testing.\n")
        print("To test with your own image, run:")
        print("   python test_segmentation.py path/to/your/image.jpg\n")
        test_segmentation_model()
    
    print()
    print("💡 Next Steps:")
    print("1. If test passed, your model is ready!")
    print("2. Update class mapping in backend/app.py (line 188-194)")
    print("3. Run: python test_backend.py")
    print("4. Start the application: python app.py")
    print()


if __name__ == "__main__":
    main()
