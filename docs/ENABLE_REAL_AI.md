# Enable Real AI Predictions - Quick Guide

## Current Status
✅ AI models are loaded and working (Swin Transformer + EfficientNet-B7)
✅ All Python packages installed
✅ Supabase credentials configured
⚠️ Demo mode is currently ENABLED

## What Will Change

### Before (Demo Mode - Current):
```
User uploads image → Returns fixed mock data
- Melanoma: 45%
- Benign Keratosis: 28%
- Risk: Medium
- Time: ~0.5 seconds
```

### After (Real AI Mode):
```
User uploads image → Real AI analysis
- Quality check (resolution, blur, brightness)
- NSFW filtering
- Lesion detection (Swin Transformer finds lesions)
- Cancer classification (EfficientNet-B7 classifies)
- Risk assessment based on predictions
- Time: 5-15 seconds (CPU) or 2-5 seconds (GPU)
```

## Steps to Enable

### Step 1: Update .env File

Edit `backend/.env` and change:
```env
DEMO_MODE=false
```

### Step 2: Restart Backend Server

Stop the current server (Ctrl+C in the terminal) and restart:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the batch file:
```bash
cd backend
.\start-server.bat
```

### Step 3: Test with Real Image

1. Log out and log back in (to refresh auth token)
2. Upload a REAL skin lesion image (not a portrait)
3. Wait 5-15 seconds for analysis
4. View real AI predictions

## Important Notes

### ⚠️ First Request Will Be Slow
- Models load into memory: ~30-60 seconds
- Subsequent requests: 5-15 seconds each

### ⚠️ Use Appropriate Images
The AI is trained for:
- Close-up photos of skin lesions
- Clear, well-lit images
- Focused on the lesion area

NOT for:
- Portrait photos
- Full body images
- Non-skin images

### ⚠️ Medical Disclaimer
- AI predictions are screening tools, not diagnoses
- Always recommend professional medical consultation
- Results should be verified by dermatologists

## Performance Expectations

### CPU Mode (Current - No GPU):
- First analysis: ~45-75 seconds (includes model loading)
- Subsequent: ~5-15 seconds per image
- Memory usage: ~2-4 GB RAM

### GPU Mode (If you have NVIDIA GPU):
- First analysis: ~35-45 seconds
- Subsequent: ~2-5 seconds per image
- Much faster and more efficient

## Troubleshooting

### Issue: "Model loading timeout"
**Solution**: First request takes longer, be patient

### Issue: "Out of memory"
**Solution**: Close other applications, or reduce batch size

### Issue: "Slow performance"
**Solution**: This is normal on CPU. Consider:
1. Using a GPU
2. Reducing image resolution
3. Using cloud GPU services

## Reverting to Demo Mode

If you want to go back to demo mode:
1. Edit `backend/.env`
2. Set `DEMO_MODE=true`
3. Restart server

## Next Steps After Enabling

1. **Test thoroughly** with various skin lesion images
2. **Monitor performance** (check logs for timing)
3. **Validate accuracy** (compare with known diagnoses if available)
4. **Consider fine-tuning** models on medical datasets for better accuracy
5. **Implement caching** for faster repeated analyses

## Cost & Resource Implications

### Development (Local):
- No additional cost
- Uses your computer's CPU/GPU
- Free Supabase tier sufficient

### Production:
- Need dedicated server with GPU
- AWS/GCP GPU instances: $0.50-$3/hour
- Or serverless GPU: ~$0.10 per request
- Supabase Pro: ~$25/month

## Ready to Enable?

Run these commands:

```bash
# 1. Update .env
cd backend
# Edit .env file and set DEMO_MODE=false

# 2. Restart server
.\start-server.bat

# 3. Test
# Go to http://localhost:3000
# Log in and upload a skin lesion image
```

The system will now use real AI models for predictions!
