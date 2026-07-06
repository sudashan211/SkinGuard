# NSFW Content Filter (Gatekeeper) Implementation

## Overview

The NSFW Content Filter is the first line of defense in the SkinGuard image processing pipeline. It validates all uploaded images for inappropriate content before allowing them to proceed to medical AI analysis.

**Requirements:** 3.1, 3.2, 3.3, 3.4, 3.6, 18.4

## Architecture

### Components

1. **NSFWDetector** (`nsfw_filter.py`)
   - Core NSFW detection logic
   - Image preprocessing
   - Score calculation
   - Rejection logic

2. **AuditLogger** (`audit.py`)
   - Logs content violations
   - Logs data access events
   - Maintains compliance audit trail

3. **ContentFilter** (`content_filter.py`)
   - Integrates NSFW detection with audit logging
   - Main gatekeeper interface

### Flow Diagram

```
Image Upload
    ↓
ContentFilter.validate_image()
    ↓
NSFWDetector.check_nsfw()
    ↓
Calculate Scores:
  - nsfw_score
  - non_skin_score
  - safe_score
    ↓
Check Thresholds:
  - nsfw_score > 0.35? → REJECT
  - non_skin_score > 0.8? → REJECT
    ↓
If REJECTED:
  - AuditLogger.log_content_violation()
  - Raise ContentViolationError (HTTP 403)
    ↓
If PASSED:
  - Return NSFWResult
  - Proceed to Quality Validation
```

## Rejection Criteria

### NSFW Score Threshold: 0.35
- **Purpose:** Detect explicit/inappropriate content
- **Action:** Reject if `nsfw_score > 0.35`
- **Response:** HTTP 403 with message "Inappropriate content detected"

### Non-Skin Score Threshold: 0.8
- **Purpose:** Detect non-medical images (objects, landscapes, etc.)
- **Action:** Reject if `non_skin_score > 0.8`
- **Response:** HTTP 403 with message "Inappropriate content detected"

## Implementation Details

### Current Implementation

The current implementation uses a **heuristic-based approach** for demonstration purposes:

- **Skin tone detection:** Analyzes RGB color distribution
- **Color variance:** Measures scene complexity
- **Brightness analysis:** Evaluates lighting conditions

**IMPORTANT:** This is a simplified implementation. In production, replace with:
- [NudeNet](https://github.com/notAI-tech/NudeNet)
- [Yahoo Open NSFW](https://github.com/yahoo/open_nsfw)
- Or similar pre-trained NSFW detection models

### Production Recommendations

For production deployment:

1. **Use Pre-trained Models:**
   ```python
   # Example with NudeNet
   from nudenet import NudeDetector
   
   detector = NudeDetector()
   result = detector.detect('image.jpg')
   ```

2. **GPU Acceleration:**
   - Deploy models on GPU instances for faster inference
   - Use batch processing for multiple images

3. **Model Updates:**
   - Regularly update models with latest versions
   - Monitor false positive/negative rates
   - Adjust thresholds based on real-world data

## API Endpoint

### POST /api/patient/validate-image

Validates uploaded image for NSFW content.

**Request:**
```bash
curl -X POST http://localhost:8000/api/patient/validate-image \
  -H "Authorization: Bearer <token>" \
  -F "image=@lesion.jpg"
```

**Success Response (200):**
```json
{
  "message": "Image passed content validation",
  "validation": {
    "safe": true,
    "nsfw_score": 0.15,
    "non_skin_score": 0.25,
    "safe_score": 0.85
  },
  "thresholds": {
    "nsfw_threshold": 0.35,
    "non_skin_threshold": 0.8
  },
  "next_steps": "Image is ready for quality validation and medical analysis"
}
```

**Rejection Response (403):**
```json
{
  "error": {
    "code": "CONTENT_VIOLATION",
    "message": "Inappropriate content detected",
    "details": {
      "nsfw_score": 0.45,
      "non_skin_score": 0.2
    },
    "timestamp": "2024-02-10T12:00:00Z",
    "request_id": "req_123456"
  }
}
```

## Audit Logging

All content violations are automatically logged to the `audit_logs` table:

```sql
SELECT * FROM audit_logs 
WHERE action = 'content_violation' 
ORDER BY created_at DESC;
```

**Audit Log Entry:**
```json
{
  "id": "audit-uuid",
  "user_id": "user-uuid",
  "action": "content_violation",
  "resource_type": "image_upload",
  "metadata": {
    "nsfw_score": 0.45,
    "non_skin_score": 0.2,
    "rejection_reason": "Inappropriate content detected",
    "threshold_nsfw": 0.35,
    "threshold_non_skin": 0.8
  },
  "ip_address": "192.168.1.1",
  "created_at": "2024-02-10T12:00:00Z"
}
```

## Testing

### Unit Tests

Run unit tests:
```bash
pytest tests/unit/test_nsfw_filter.py -v
pytest tests/unit/test_audit_logging.py -v
```

### Test Coverage

- ✅ NSFW detector initialization
- ✅ Safe image validation
- ✅ Non-skin image detection
- ✅ Threshold boundaries
- ✅ Invalid image handling
- ✅ Error attributes
- ✅ Image preprocessing
- ✅ Score calculation
- ✅ Audit log creation
- ✅ Content violation logging
- ✅ Data access logging
- ✅ Authentication event logging
- ✅ Admin action logging
- ✅ Error handling

### Property-Based Tests

Property-based tests are defined in task 6.2 and will validate:
- **Property 8:** NSFW Score Rejection Threshold
- **Property 9:** Non-Skin Score Rejection Threshold
- **Property 10:** Flagged Content Audit Logging
- **Property 54:** Data Access Audit Logging

## Integration with Pipeline

The NSFW filter integrates into the complete analysis pipeline:

```python
from app.content_filter import create_content_filter
from app.nsfw_filter import detector as nsfw_detector
from app.audit import create_audit_logger
from app.image_quality import validator as quality_validator

# Create content filter
content_filter = create_content_filter(nsfw_detector, audit_logger)

# Complete pipeline
async def analyze_image(image_data, user_id, ip_address):
    # Step 1: Quality validation
    quality_result = quality_validator.validate_quality(image_data)
    if not quality_result.passed:
        raise QualityError(quality_result.message)
    
    # Step 2: NSFW filtering (Gatekeeper)
    nsfw_result = await content_filter.validate_image(
        image_data, user_id, ip_address
    )
    
    # Step 3: Medical AI analysis (future implementation)
    # ai_result = await medical_ai.analyze(image_data)
    
    return {
        "quality": quality_result,
        "nsfw": nsfw_result,
        # "ai_analysis": ai_result
    }
```

## Security Considerations

1. **Fail-Safe Behavior:**
   - On error, reject the image (fail closed)
   - Never allow unvalidated images through

2. **Audit Trail:**
   - All rejections are logged
   - IP addresses are recorded
   - User IDs are tracked (when authenticated)

3. **Rate Limiting:**
   - Implement rate limiting on upload endpoints
   - Prevent abuse and DoS attacks

4. **Privacy:**
   - Rejected images are NOT stored
   - Only metadata is logged to audit trail
   - Complies with GDPR requirements

## Performance

### Current Performance (Heuristic Mode)
- **Processing Time:** ~50-100ms per image
- **Memory Usage:** ~10MB per image
- **Throughput:** ~10-20 images/second

### Expected Performance (Production Models)
- **Processing Time:** ~200-500ms per image (CPU)
- **Processing Time:** ~50-100ms per image (GPU)
- **Memory Usage:** ~100-500MB (model loaded)
- **Throughput:** ~2-5 images/second (CPU), ~10-20 images/second (GPU)

## Configuration

Thresholds can be adjusted in `nsfw_filter.py`:

```python
class NSFWDetector:
    # Detection thresholds
    NSFW_THRESHOLD = 0.35      # Adjust based on false positive rate
    NON_SKIN_THRESHOLD = 0.8   # Adjust based on medical image characteristics
```

## Monitoring

Monitor these metrics in production:

1. **Rejection Rate:** Percentage of images rejected
2. **False Positives:** Legitimate images incorrectly rejected
3. **False Negatives:** Inappropriate images incorrectly accepted
4. **Processing Time:** Average time per image
5. **Error Rate:** Percentage of processing errors

## Future Enhancements

1. **Machine Learning Model Integration:**
   - Replace heuristic with trained model
   - Continuous model improvement
   - A/B testing of different models

2. **Multi-Model Ensemble:**
   - Combine multiple NSFW detectors
   - Improve accuracy through voting

3. **Feedback Loop:**
   - Allow doctors to flag false negatives
   - Use feedback to retrain models

4. **Advanced Features:**
   - Skin lesion vs. other skin detection
   - Body part classification
   - Medical context understanding

## Support

For questions or issues:
- Review the design document: `.kiro/specs/derman-ai-skin-screening/design.md`
- Check requirements: `.kiro/specs/derman-ai-skin-screening/requirements.md`
- Run tests: `pytest tests/unit/test_nsfw_filter.py -v`

## License

This implementation is part of the SkinGuard platform.
