# NSFW Filter 403 Forbidden Error - Fix Documentation

## Problem
Patient images are being rejected with **403 Forbidden** error:
```
POST http://localhost:8001/api/analyze-skin 403 (Forbidden)
Error: "You do not have permission to perform this action"
```

Backend logs show:
```
Image rejected: Non-skin score 0.998 exceeds threshold 0.99
```

## Root Cause
The NSFW content filter (`backend/app/nsfw_filter.py`) is using a **heuristic-based approach** that calculates skin tone percentages. This heuristic is rejecting valid medical skin lesion images as "non-skin content" because:

1. The heuristic expects images with high skin-tone pixel percentage (>60%)
2. Real medical images often have:
   - Close-up lesions that don't show much surrounding skin
   - Unusual colors (dark, red, inflamed) that don't match typical skin tones
   - Specialized lighting that changes color balance

## Solution Options

### Option 1: Use Real AI Mode (Recommended - Already Configured)
The code already has a bypass for real AI mode. When `USE_REAL_AI=true`, the NSFW filter should skip the heuristic check entirely.

**Current Configuration** (in `backend/.env`):
```env
USE_REAL_AI=true
```

**Code** (lines 91-99 in `backend/app/nsfw_filter.py`):
```python
if settings.use_real_ai:
    logger.info("REAL AI MODE: Skipping NSFW filter for medical image analysis")
    return NSFWResult(
        safe=True,
        nsfw_score=0.01,
        non_skin_score=0.05,
        safe_score=0.94
    )
```

**Status**: This should already be working. Need to verify:
1. Backend has restarted since .env was updated
2. Settings are being loaded correctly
3. No other code is bypassing this check

### Option 2: Increase Non-Skin Threshold
If Option 1 doesn't work, increase the threshold to be more lenient.

**Current threshold** (line 68 in `backend/app/nsfw_filter.py`):
```python
NON_SKIN_THRESHOLD = 0.99  # Very lenient threshold
```

**Recommended change**:
```python
NON_SKIN_THRESHOLD = 0.999  # Even more lenient - allows 99.9% non-skin
```

Or completely disable for demo/testing:
```python
NON_SKIN_THRESHOLD = 1.0  # Never reject based on non-skin score
```

### Option 3: Add Demo Mode Bypass
Add a separate bypass for demo mode testing.

**Change in `nsfw_filter.py`** (after line 91):
```python
# Skip NSFW filter in real AI mode or demo mode
if settings.use_real_ai or settings.demo_mode:
    logger.info(f"Skipping NSFW filter (use_real_ai={settings.use_real_ai}, demo_mode={settings.demo_mode})")
    return NSFWResult(
        safe=True,
        nsfw_score=0.01,
        non_skin_score=0.05,
        safe_score=0.94
    )
```

### Option 4: Replace with Real NSFW Model (Production)
The current heuristic is a placeholder. For production, replace with a real NSFW detection model:

**Recommended models**:
- **NudeNet**: https://github.com/notAI-tech/NudeNet
- **Yahoo Open NSFW**: https://github.com/yahoo/open_nsfw
- **Falconsai/nsfw_image_detection** (Hugging Face)

**Example integration**:
```python
from transformers import pipeline

class NSFWDetector:
    def __init__(self):
        self.classifier = pipeline("image-classification", 
                                   model="Falconsai/nsfw_image_detection")
    
    def check_nsfw(self, image_data: bytes) -> NSFWResult:
        from PIL import Image
        from io import BytesIO
        
        image = Image.open(BytesIO(image_data))
        results = self.classifier(image)
        
        # Find NSFW score
        nsfw_score = next((r['score'] for r in results if r['label'] == 'nsfw'), 0.0)
        
        if nsfw_score > 0.35:
            raise ContentViolationError(...)
        
        return NSFWResult(safe=True, nsfw_score=nsfw_score, ...)
```

## Testing Steps

After applying any fix:

1. **Restart backend server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8001
   ```

2. **Check logs on startup**:
   - Look for "REAL AI MODE: Skipping NSFW filter" message when analyzing
   - Or "NSFW Detector initialized (heuristic mode)"

3. **Test image upload**:
   - Go to http://localhost:3000
   - Login as patient
   - Upload a skin lesion image
   - Should NOT get 403 error

4. **Verify in logs**:
   ```
   # SUCCESS - should see:
   INFO: REAL AI MODE: Skipping NSFW filter for medical image analysis
   
   # FAILURE - will see:
   WARNING: Image rejected: Non-skin score 0.998 exceeds threshold 0.99
   ```

## Current Status
- ✅ `USE_REAL_AI=true` is set in `backend/.env`
- ✅ Backend code has bypass logic (lines 91-99)
- ✅ Servers are running (backend: 8001, frontend: 3000)
- ⏳ Need to test if bypass is actually working
- ⏳ May need to manually verify settings are loaded

## Immediate Action
**Try uploading an image now** and check backend logs. If you still see "Image rejected: Non-skin score...", then the settings aren't being loaded and we need to investigate further.

## Alternative Quick Fix
If the issue persists, the fastest fix is to temporarily disable the NSFW check by changing line 117 in `nsfw_filter.py`:

```python
# OLD:
if non_skin_score > self.NON_SKIN_THRESHOLD:

# NEW (temporarily disable):
if False and non_skin_score > self.NON_SKIN_THRESHOLD:
```

This completely disables the non-skin rejection while keeping other checks active.
