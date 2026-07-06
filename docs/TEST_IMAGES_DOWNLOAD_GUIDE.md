# Download Test Images for SkinGuard AI

## Quick Links to Download Skin Lesion Images

---

## 🏥 Official Medical Datasets (Best Quality)

### 1. ISIC Archive (International Skin Imaging Collaboration)
**Best source for dermoscopic images**

**Direct Link**: https://www.isic-archive.com/

**How to Download**:
1. Go to https://www.isic-archive.com/
2. Click "Gallery" or "Browse Images"
3. Filter by diagnosis type (melanoma, nevus, etc.)
4. Click on any image to view
5. Click "Download" button to save

**What You Get**:
- High-quality dermoscopic images
- Expert-labeled diagnoses
- Various lesion types
- Different skin tones
- Free for research/testing

**Recommended Searches**:
- Melanoma
- Basal cell carcinoma
- Seborrheic keratosis
- Nevus (mole)

---

### 2. HAM10000 Dataset
**10,000+ dermatoscopic images**

**Direct Link**: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T

**How to Download**:
1. Go to the link above
2. Scroll down to "Data Files"
3. Download "HAM10000_images_part_1.zip" (5GB)
4. Download "HAM10000_images_part_2.zip" (5GB)
5. Extract the ZIP files

**What You Get**:
- 10,015 images
- 7 diagnostic categories (same as our model!)
- CSV file with metadata
- Expert annotations

**Note**: Large download (10GB total)

---

### 3. DermNet NZ (Dermatology Image Library)
**Comprehensive dermatology resource**

**Direct Link**: https://dermnetnz.org/

**How to Browse**:
1. Go to https://dermnetnz.org/
2. Use search bar or browse by condition
3. Search for:
   - "Melanoma"
   - "Basal cell carcinoma"
   - "Squamous cell carcinoma"
   - "Seborrheic keratosis"
   - "Actinic keratosis"
4. Right-click images and "Save Image As"

**What You Get**:
- Clinical photographs
- Educational images
- Various conditions
- Free for educational use

---

## 🔍 Quick Google Image Search (Easiest)

### Search Terms to Use:

**For Melanoma**:
- "melanoma dermoscopy"
- "melanoma close up"
- "ABCD melanoma"

**For Basal Cell Carcinoma**:
- "basal cell carcinoma dermoscopy"
- "BCC skin lesion"

**For Squamous Cell Carcinoma**:
- "squamous cell carcinoma dermoscopy"
- "SCC skin lesion"

**For Benign Lesions**:
- "seborrheic keratosis dermoscopy"
- "dermatofibroma close up"
- "benign nevus dermoscopy"

**Important**: 
- Add "dermoscopy" or "close up" to get proper images
- Look for images showing just the lesion, not full body
- Avoid watermarked or copyrighted images

---

## 📥 Sample Images - Direct Download Links

### Melanoma Examples:
1. **ISIC Sample 1**: https://isic-archive-api.appspot.com/api/v1/image/5436e3abbae478396759f0cf/thumbnail
2. **ISIC Sample 2**: https://isic-archive-api.appspot.com/api/v1/image/5436e3abbae478396759f0d1/thumbnail

### Nevus (Mole) Examples:
1. **ISIC Sample 1**: https://isic-archive-api.appspot.com/api/v1/image/5436e3abbae478396759f0d3/thumbnail
2. **ISIC Sample 2**: https://isic-archive-api.appspot.com/api/v1/image/5436e3abbae478396759f0d5/thumbnail

**Note**: These are thumbnail versions. For full resolution, visit the ISIC website.

---

## 🎯 Recommended Test Images

### Start with These:

1. **Clear Melanoma** - To test high-risk detection
2. **Benign Nevus** - To test low-risk detection
3. **Seborrheic Keratosis** - To test benign classification
4. **Basal Cell Carcinoma** - To test moderate-risk detection

---

## 📋 Step-by-Step: Download from ISIC

### Detailed Instructions:

1. **Go to ISIC Archive**
   - URL: https://www.isic-archive.com/

2. **Browse Images**
   - Click "Gallery" in the top menu
   - Or go directly to: https://www.isic-archive.com/#!/topWithHeader/onlyHeaderTop/gallery

3. **Filter by Diagnosis**
   - Click "Filters" button
   - Under "Diagnosis", select:
     - Melanoma
     - Basal cell carcinoma
     - Seborrheic keratosis
     - Nevus
   - Click "Apply"

4. **Select an Image**
   - Click on any image thumbnail
   - Image details will open

5. **Download**
   - Click the "Download" button (down arrow icon)
   - Choose "Original" for best quality
   - Save to your computer

6. **Repeat**
   - Download 5-10 images of different types
   - Mix malignant and benign lesions

---

## 🖼️ Image Requirements

### For Best Results:

✅ **Good Images**:
- Close-up of lesion
- Clear focus
- Good lighting
- Minimum 512x512 pixels
- Shows skin texture
- Dermoscopic images preferred

❌ **Avoid**:
- Blurry images
- Dark/poorly lit
- Too small (< 512x512)
- Full body shots
- Portrait photos
- Non-skin images

---

## 🧪 Testing Strategy

### Recommended Test Sequence:

1. **Test 1: Clear Melanoma**
   - Should return: High melanoma probability
   - Risk level: High or Urgent
   - Purpose: Verify high-risk detection

2. **Test 2: Benign Nevus**
   - Should return: Low melanoma probability
   - Risk level: Low
   - Purpose: Verify low-risk detection

3. **Test 3: Seborrheic Keratosis**
   - Should return: High benign keratosis probability
   - Risk level: Low
   - Purpose: Verify benign classification

4. **Test 4: Basal Cell Carcinoma**
   - Should return: High BCC probability
   - Risk level: Medium or High
   - Purpose: Verify malignant detection

5. **Test 5: Mixed/Unclear**
   - Should return: Mixed probabilities
   - Risk level: Medium
   - Purpose: Verify uncertainty handling

---

## 📊 Expected Results

### What to Look For:

**Good Performance**:
- Melanoma images → High melanoma probability
- Benign images → High benign probability
- Clear risk level assignment
- Reasonable confidence scores

**Limitations** (Current Model):
- May not be 100% accurate
- Pre-trained, not fine-tuned
- May confuse similar-looking lesions
- Accuracy varies by image quality

---

## 🔗 Additional Resources

### Medical Image Databases:

1. **PH² Dataset** (Melanoma)
   - https://www.fc.up.pt/addi/ph2%20database.html
   - 200 dermoscopic images
   - Melanoma and atypical nevi

2. **Dermoscopy Atlas**
   - http://www.dermoscopyatlas.com/
   - Educational dermoscopic images
   - Various conditions

3. **Dermquest**
   - https://www.dermquest.com/
   - Clinical images
   - Requires free registration

### Research Papers with Images:

1. **"Dermatologist-level classification"** (Nature, 2017)
   - Supplementary materials have sample images

2. **HAM10000 Paper**
   - https://arxiv.org/abs/1803.10417
   - Sample images in paper

---

## ⚠️ Legal & Ethical Considerations

### Important Notes:

**Copyright**:
- ISIC images: Free for research/educational use
- HAM10000: Open access dataset
- DermNet NZ: Educational use permitted
- Google Images: Check individual image licenses

**Privacy**:
- All public datasets are de-identified
- No patient information included
- Safe for testing purposes

**Medical Use**:
- These are for TESTING only
- Not for actual medical diagnosis
- Always consult healthcare professionals

---

## 🚀 Quick Start

### Fastest Way to Get Started:

1. **Go to ISIC**: https://www.isic-archive.com/#!/topWithHeader/onlyHeaderTop/gallery

2. **Download 3 images**:
   - 1 Melanoma
   - 1 Nevus (benign mole)
   - 1 Seborrheic keratosis

3. **Test on SkinGuard**:
   - Go to http://localhost:3000
   - Log in as patient
   - Upload each image
   - Compare results

4. **Verify**:
   - Melanoma → Should show high risk
   - Nevus → Should show low risk
   - Seborrheic keratosis → Should show benign

---

## 📞 Need Help?

If you have trouble downloading:
1. Check your internet connection
2. Try a different browser
3. Clear browser cache
4. Use incognito/private mode
5. Try alternative sources (DermNet NZ, Google Images)

---

## ✅ Checklist

Before testing, make sure you have:

- [ ] Downloaded 3-5 test images
- [ ] Images are clear and well-lit
- [ ] Images show close-up of lesions
- [ ] Images are at least 512x512 pixels
- [ ] Mix of malignant and benign lesions
- [ ] Backend server is running (real AI mode)
- [ ] Frontend is accessible at localhost:3000
- [ ] Logged in as patient user

---

**Ready to test? Start with ISIC Archive - it's the best source!** 🎯

Direct link: https://www.isic-archive.com/#!/topWithHeader/onlyHeaderTop/gallery
