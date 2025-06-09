#!/usr/bin/env python3
"""
Quick test to verify PyTorch model loading fix
"""
import os

# Set the environment variable before importing anything
os.environ['PYTORCH_DISABLE_STRICT_LOADING'] = '1'

def test_model_loading():
    try:
        print("🔄 Testing PyTorch model loading...")
        from ultralytics import YOLO
        
        model_path = 'models/best_nano_111.pt'
        if not os.path.exists(model_path):
            print(f"❌ Model file not found: {model_path}")
            return False
            
        model = YOLO(model_path)
        print("✅ YOLO model loaded successfully!")
        
        # Test a simple prediction to ensure it works
        print("🔄 Testing model inference...")
        results = model.predict(source='data/test_image.png', verbose=False)
        print(f"✅ Model inference successful! Detected {len(results[0].boxes)} objects")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_model_loading()
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Model loading test")
