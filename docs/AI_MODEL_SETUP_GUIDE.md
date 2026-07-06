# SkinGuard AI Model Setup Guide

## Overview
This guide will help you enable real AI-powered skin cancer predictions instead of demo mode mock data.

## Current Status
- ✅ AI model infrastructure code is complete
- ✅ Python packages are installed (torch, timm, etc.)
- ⚠️ Running in DEMO MODE (returns mock predictions)
- ❌ Real AI models not loaded
- ❌ Database not connected

---

## What You Need

### 1. Hardware Requirements
- **CPU**: Modern multi-core processor (Intel i5/i7 or AMD Ryzen 5/7+)
- **RAM**: Minimum 8GB, Recommended 16GB+
- **GPU** (Optional but recommended): NVIDIA GPU with CUDA support
  - Speeds up inference significantly
  - Models will work on CPU but slower

### 2. AI Models
The system uses pre-trained models from the `timm` library:
- **Swin Transformer** (`swin_base_patch4_window7_224`) - Lesion detection
- **EfficientNet-B7** (`tf_efficientnet_b7`) - Cancer classification

These models will be automatically downloaded when first loaded.

### 3. Database (Supabase)
- Supabase project URL
- Supabase service role key
- Database tables created (see schema in deployment docs)

---

## Setup Steps

### Step 1: Install PyTorch with CUDA (Optional - for GPU acceleration)

If you have an NVIDIA GPU, install PyTorch with CUDA support:

```bash
# Check your CUDA version first
nvidia-smi

# Install PyTorch with CUDA 11.8 (adjust version as needed)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Step 2: Verify AI Package Installation

```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Set Up Supabase Database

1. Create a Supabase project at https://supabase.com
2. Run the database schema (see `deployment/database_schema.sql`)
3. Get your credentials:
   - Project URL
   - Service role key (from Settings > API)

### Step 4: Configure Environment Variables

Edit `backend/.env`:

```env
# Disable demo mode
DEMO_MODE=false

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key-here

# JWT Configuration
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# CORS
CORS_ORIGINS=http://localhost:3000

# Email (optional - for notifications)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@skinguard.com
```

### Step 5: Test Model Loading

Create a test script `backend/test_models.py`:

```python
import sys
sys.path.append('.')

from app.ai_models import get_model_manager

print("Testing AI model loading...")
manager = get_model_manager()

print("\n1. Loading Swin Transformer...")
swin = manager.get_swin_model()
print(f"✓ Swin model loaded on {manager.device}")

print("\n2. Loading EfficientNet-B7...")
efficientnet = manager.get_efficientnet_model()
print(f"✓ EfficientNet model loaded on {manager.device}")

print("\n3. Model Info:")
info = manager.get_model_info()
for key, value in info.items():
    print(f"  {key}: {value}")

print("\n✓ All models loaded successfully!")
```

Run it:
```bash
cd backend
python test_models.py
```

### Step 6: Restart Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## What Happens When You Enable Real AI

### Before (Demo Mode):
- Returns fixed mock predictions (Melanoma 45%, etc.)
- No actual image analysis
- Instant response
- No GPU/CPU usage

### After (Real AI Mode):
- Downloads models on first run (~500MB-1GB)
- Analyzes actual image content
- Returns real predictions based on image features
- Takes 5-15 seconds per image (CPU) or 2-5 seconds (GPU)
- Uses significant RAM and processing power

---

## Expected Performance

### First Request (Cold Start):
- **Model Loading**: 30-60 seconds
- **Inference**: 5-15 seconds (CPU) / 2-5 seconds (GPU)
- **Total**: ~45-75 seconds

### Subsequent Requests (Warm):
- **Inference Only**: 5-15 seconds (CPU) / 2-5 seconds (GPU)

---

## Troubleshooting

### Issue: "CUDA out of memory"
**Solution**: Models are too large for your GPU
```python
# In backend/app/ai_models.py, force CPU usage:
DEVICE = "cpu"  # Instead of auto-detection
```

### Issue: "Model download failed"
**Solution**: Check internet connection, models download from HuggingFace
```bash
# Pre-download models manually:
python -c "import timm; timm.create_model('swin_base_patch4_window7_224', pretrained=True)"
python -c "import timm; timm.create_model('tf_efficientnet_b7', pretrained=True)"
```

### Issue: "Supabase connection failed"
**Solution**: Verify credentials in `.env` file
```bash
# Test Supabase connection:
python backend/test_supabase.py
```

### Issue: Slow inference on CPU
**Solution**: This is normal. Options:
1. Use a GPU (recommended)
2. Reduce image resolution
3. Use model quantization (advanced)

---

## Important Notes

### Medical Disclaimer
Even with real AI models:
- This is a screening tool, NOT a diagnostic tool
- AI predictions should be verified by medical professionals
- Always recommend users consult dermatologists
- Include proper disclaimers in the UI

### Model Accuracy
The pre-trained models from `timm` are:
- Trained on ImageNet (general images)
- NOT specifically fine-tuned for skin cancer
- For production use, you should:
  - Fine-tune on skin lesion datasets (HAM10000, ISIC)
  - Validate on medical test sets
  - Get regulatory approval if required

### Data Privacy
- Images are processed in memory
- Stored in Supabase (ensure encryption)
- Follow HIPAA/GDPR requirements
- Implement proper access controls

---

## Next Steps After Setup

1. **Test with real skin lesion images** (not portraits)
2. **Monitor performance** (processing time, accuracy)
3. **Fine-tune models** on medical datasets
4. **Implement caching** for faster responses
5. **Add monitoring** (Sentry, logging)
6. **Scale infrastructure** (load balancing, GPU servers)

---

## Cost Considerations

### Development (Current):
- Free tier Supabase: $0/month
- Local compute: $0/month
- **Total: $0/month**

### Production:
- Supabase Pro: ~$25/month
- GPU Server (AWS p3.2xlarge): ~$3/hour = ~$2,160/month
- Or CPU Server (AWS c5.4xlarge): ~$0.68/hour = ~$490/month
- **Total: $515-$2,185/month**

### Optimization:
- Use serverless GPU (AWS Lambda + EFS): ~$0.10/request
- Batch processing: Reduce costs by 50-70%
- Model quantization: Reduce memory and speed up inference

---

## Support

For issues or questions:
1. Check backend logs: `backend/logs/`
2. Review error messages in browser console
3. Test individual components (models, database, API)
4. Consult documentation in `deployment/` folder
