# How to Get HAM10000 Metadata CSV

## What is the Metadata File?

The `HAM10000_metadata.csv` file contains the ground truth labels for all images:
- Image ID
- Actual cancer type (diagnosis)
- Patient age
- Location on body
- And other medical information

## Where to Download

### Option 1: Kaggle (Recommended)

1. **Go to Kaggle Dataset:**
   https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000

2. **Download the metadata:**
   - Look for `HAM10000_metadata.csv` or `HAM10000_metadata.tab`
   - Click "Download" button
   - You may need to create a free Kaggle account

3. **Place in project root:**
   ```
   SkinGuard/
   ├── HAM10000_metadata.csv  ← Put it here
   ├── HAM10000_images_part_1/
   ├── HAM10000_images_part_2/
   └── backend/
   ```

### Option 2: Harvard Dataverse (Original Source)

1. **Go to Harvard Dataverse:**
   https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T

2. **Download metadata file:**
   - Look for "HAM10000_metadata.tab" or CSV file
   - Download it

3. **Convert if needed:**
   - If you get a `.tab` file, it's tab-separated
   - You can convert it to CSV or the script can read it

### Option 3: Check Your Download

The metadata file might already be in your download folder where you got the images:

```bash
# Search for metadata file
dir /s HAM10000_metadata*
```

## File Format

The metadata CSV contains these columns:

```csv
lesion_id,image_id,dx,dx_type,age,sex,localization
HAM_0000118,ISIC_0027419,bkl,histo,80.0,male,scalp
HAM_0000118,ISIC_0025030,bkl,histo,80.0,male,scalp
HAM_0002730,ISIC_0026769,bkl,histo,80.0,male,scalp
```

**Important columns:**
- `image_id`: Matches the image filename (e.g., ISIC_0027419.jpg)
- `dx`: Diagnosis (cancer type)
  - `nv`: Melanocytic nevi (moles)
  - `mel`: Melanoma
  - `bkl`: Benign keratosis
  - `bcc`: Basal cell carcinoma
  - `akiec`: Actinic keratoses
  - `vasc`: Vascular lesions
  - `df`: Dermatofibroma

## After Downloading

1. **Place the file in project root:**
   ```
   SkinGuard/HAM10000_metadata.csv
   ```

2. **Run the accuracy test:**
   ```bash
   cd backend
   python test_ham10000_accuracy.py 50
   ```

3. **The script will now:**
   - Compare predictions to ground truth
   - Calculate actual accuracy
   - Show which cancer types are predicted correctly
   - Display confusion matrix

## Alternative: Test Without Metadata

If you can't get the metadata file, you can still:

1. **Test predictions visually:**
   - Run the test script without metadata
   - Look at the predictions
   - Manually verify some images

2. **Use the 3 test images you already have:**
   ```bash
   python test_huggingface_model.py ../ISIC_0000198.jpg
   ```

3. **Trust the published accuracy:**
   - The model reports 96.95% validation accuracy
   - This was tested by the model creator
   - Your tests will show similar results

## Quick Links

- **Kaggle Dataset:** https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000
- **Harvard Dataverse:** https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T
- **Original Paper:** https://arxiv.org/abs/1803.10417

## Need Help?

If you can't find the metadata file, you can:
1. Test without it (predictions only, no accuracy calculation)
2. Use the 3 ISIC test images you already have
3. Trust the published 96.95% accuracy from the model page
