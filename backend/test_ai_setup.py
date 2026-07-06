"""
Test script to verify AI model setup
Run this before enabling real AI mode
"""
import sys
import os

print("=" * 60)
print("SkinGuard AI Model Setup Test")
print("=" * 60)

# Test 1: Check Python packages
print("\n1. Checking Python packages...")
required_packages = {
    'torch': 'PyTorch',
    'torchvision': 'TorchVision',
    'timm': 'PyTorch Image Models',
    'PIL': 'Pillow',
    'numpy': 'NumPy',
    'cv2': 'OpenCV'
}

missing_packages = []
for package, name in required_packages.items():
    try:
        __import__(package)
        print(f"  ✓ {name} installed")
    except ImportError:
        print(f"  ✗ {name} NOT installed")
        missing_packages.append(name)

if missing_packages:
    print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 2: Check CUDA availability
print("\n2. Checking GPU/CUDA availability...")
import torch
if torch.cuda.is_available():
    print(f"  ✓ CUDA available")
    print(f"  ✓ GPU: {torch.cuda.get_device_name(0)}")
    print(f"  ✓ CUDA version: {torch.version.cuda}")
else:
    print(f"  ⚠ CUDA not available - will use CPU")
    print(f"  ℹ This is OK but inference will be slower")

# Test 3: Check model cache directory
print("\n3. Checking model cache directory...")
from pathlib import Path
cache_dir = Path("models/cache")
if cache_dir.exists():
    print(f"  ✓ Cache directory exists: {cache_dir.absolute()}")
else:
    print(f"  ℹ Creating cache directory: {cache_dir.absolute()}")
    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"  ✓ Cache directory created")

# Test 4: Test model loading (this will download models if needed)
print("\n4. Testing AI model loading...")
print("  ⚠ This may take 1-2 minutes on first run (downloading models)")

try:
    from app.ai_models import get_model_manager
    
    manager = get_model_manager()
    print(f"  ✓ Model manager initialized")
    print(f"  ✓ Device: {manager.device}")
    
    # Test Swin Transformer
    print("\n  Loading Swin Transformer...")
    swin_model = manager.get_swin_model()
    print(f"  ✓ Swin Transformer loaded successfully")
    
    # Test EfficientNet
    print("\n  Loading EfficientNet-B7...")
    efficientnet_model = manager.get_efficientnet_model()
    print(f"  ✓ EfficientNet-B7 loaded successfully")
    
    # Get model info
    print("\n  Model Information:")
    info = manager.get_model_info()
    for key, value in info.items():
        print(f"    {key}: {value}")
    
except Exception as e:
    print(f"  ✗ Model loading failed: {str(e)}")
    print(f"\nError details:")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Check environment configuration
print("\n5. Checking environment configuration...")
from dotenv import load_dotenv
load_dotenv()

demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if demo_mode:
    print(f"  ⚠ DEMO_MODE is enabled")
    print(f"    To use real AI, set DEMO_MODE=false in .env")
else:
    print(f"  ✓ DEMO_MODE is disabled - real AI will be used")

if supabase_url and supabase_key:
    print(f"  ✓ Supabase credentials configured")
else:
    print(f"  ⚠ Supabase credentials not configured")
    print(f"    Set SUPABASE_URL and SUPABASE_KEY in .env")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if missing_packages:
    print("❌ Setup incomplete - missing packages")
    print(f"   Run: pip install -r requirements.txt")
elif demo_mode:
    print("⚠ Setup complete but DEMO_MODE is enabled")
    print("  To enable real AI predictions:")
    print("  1. Set DEMO_MODE=false in backend/.env")
    print("  2. Configure Supabase credentials")
    print("  3. Restart the backend server")
else:
    print("✓ Setup complete - ready for real AI predictions!")
    print("  Restart the backend server to apply changes")

print("=" * 60)
