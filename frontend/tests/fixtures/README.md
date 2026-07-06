# Test Fixtures

This directory contains test images and data files used in E2E tests.

## Required Test Images

The following test images should be placed in this directory:

### 1. test-lesion.jpg
- **Purpose**: Valid skin lesion image for testing AI analysis
- **Requirements**: 
  - Resolution: At least 512x512 pixels
  - Format: JPEG
  - Content: Clear image of a skin lesion
  - NSFW Score: < 0.35
  - Non-Skin Score: < 0.8

### 2. low-res-image.jpg
- **Purpose**: Test image quality validation
- **Requirements**:
  - Resolution: Less than 512x512 pixels (e.g., 256x256)
  - Format: JPEG
  - Should trigger "resolution too low" error

### 3. nsfw-test.jpg
- **Purpose**: Test NSFW content filtering
- **Requirements**:
  - NSFW Score: > 0.35
  - Should be rejected by the gatekeeper
  - Used to verify content moderation works

### 4. melanoma-info.jpg
- **Purpose**: Educational content image for Skin-Wiki
- **Requirements**:
  - Resolution: 800x600 or higher
  - Format: JPEG
  - Content: Medical illustration or diagram

## Creating Test Images

If you don't have real test images, you can create placeholder images:

```bash
# Create a valid test lesion image (512x512)
convert -size 512x512 xc:white -fill brown -draw "circle 256,256 256,200" test-lesion.jpg

# Create a low-resolution image (256x256)
convert -size 256x256 xc:white -fill brown -draw "circle 128,128 128,100" low-res-image.jpg

# Create a placeholder for educational content
convert -size 800x600 xc:white -pointsize 30 -draw "text 200,300 'Melanoma Information'" melanoma-info.jpg
```

## Security Note

**DO NOT** commit actual NSFW images to the repository. For testing NSFW filtering:
- Use synthetic test images that trigger the NSFW detector
- Or use a mock/stub for the NSFW detection service in tests
- Keep test images appropriate for a professional codebase

## Usage in Tests

Test images are referenced in E2E tests like this:

```typescript
import path from 'path'

const testImagePath = path.join(__dirname, '../fixtures/test-lesion.jpg')
await page.setInputFiles('input[type=file]', testImagePath)
```

## Maintenance

- Keep test images small (< 1MB each) to avoid bloating the repository
- Update this README if new test fixtures are added
- Ensure all test images are properly licensed for testing purposes
