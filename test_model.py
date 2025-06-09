#!/usr/bin/env python3
"""
Test script to check if YOLO model can be loaded with current PyTorch version
"""

import os
import torch
from ultralytics import YOLO

def test_model_loading():
    print(f"PyTorch version: {torch.__version__}")
    print(f"Ultralytics version: {YOLO.__version__ if hasattr(YOLO, '__version__') else 'Unknown'}")
    
    model_path = 'models/best_nano_111.pt'
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found at {model_path}")
        return False
    
    try:
        # Method 1: Direct loading (should work with newer ultralytics)
        print("🔄 Attempting to load model with ultralytics...")
        model = YOLO(model_path)
        print(f"✅ Model loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        
        # Method 2: Try with safe globals
        try:
            print("🔄 Trying with safe globals...")
            torch.serialization.add_safe_globals([
                'ultralytics.nn.tasks.DetectionModel',
                'ultralytics.nn.modules',
                'ultralytics.nn.modules.block',
                'ultralytics.nn.modules.conv',
                'ultralytics.nn.modules.head'
            ])
            model = YOLO(model_path)
            print(f"✅ Model loaded successfully with safe globals!")
            return True
            
        except Exception as e2:
            print(f"❌ Alternative method also failed: {str(e2)}")
            
            # Method 3: Try downgrading torch loading behavior
            try:
                print("🔄 Trying with weights_only=False...")
                # This is a more advanced fix that requires modifying ultralytics internally
                print("💡 Consider updating to ultralytics>=8.1.0 or PyTorch<2.6")
                return False
                
            except Exception as e3:
                print(f"❌ All methods failed: {str(e3)}")
                return False

if __name__ == "__main__":
    success = test_model_loading()
    if success:
        print("🎉 Model loading test passed!")
    else:
        print("❌ Model loading test failed!")
        print("\n💡 Potential solutions:")
        print("1. Update ultralytics: pip install ultralytics>=8.1.0")
        print("2. Or downgrade PyTorch: pip install torch<2.6")
        print("3. Or set environment variable: PYTORCH_DISABLE_STRICT_LOADING=1")
