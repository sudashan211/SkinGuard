# How Risk Assessment Works

## Overview

The system uses a **two-factor approach** to assess risk:
1. **What type of cancer** is detected (dangerous vs benign)
2. **How confident** the AI model is (probability)

## Step-by-Step Process

### Step 1: AI Model Predicts Cancer Type

The Vision Transformer model analyzes the image and gives probabilities for all 7 cancer types:

```
Example Output:
- melanoma: 99.57%
- actinic_keratoses: 0.15%
- melanocytic_Nevi: 0.12%
- benign_keratosis: 0.09%
- dermatofibroma: 0.03%
- vascular_lesions: 0.03%
- basal_cell_carcinoma: 0.02%
```

### Step 2: Classify Cancer Types as Dangerous or Benign

The system categorizes each cancer type:

**DANGEROUS (Malignant) Types:**
- ❌ **Melanoma** - Most deadly skin cancer, can spread quickly
- ❌ **Basal Cell Carcinoma** - Common cancer, rarely spreads but needs treatment
- ❌ **Actinic Keratoses** - Pre-cancerous, can become cancer
- ❌ **Squamous Cell Carcinoma** - Can spread if untreated

**BENIGN (Non-dangerous) Types:**
- ✅ **Melanocytic Nevi** - Common moles, harmless
- ✅ **Dermatofibroma** - Benign skin nodule
- ✅ **Vascular Lesions** - Blood vessel abnormalities, usually harmless
- ✅ **Benign Keratosis** - Non-cancerous skin growth

### Step 3: Find Highest Dangerous Cancer Probability

The system looks for the highest probability among ONLY the dangerous types:

**Example 1: Benign Mole**
```
Predictions:
- melanocytic_Nevi: 99.90% ← BENIGN (ignore for risk)
- melanoma: 0.05% ← DANGEROUS (use this!)
- basal_cell_carcinoma: 0.01% ← DANGEROUS

Highest dangerous probability: 0.05%
```

**Example 2: Melanoma**
```
Predictions:
- melanoma: 99.57% ← DANGEROUS (use this!)
- actinic_keratoses: 0.15% ← DANGEROUS
- melanocytic_Nevi: 0.12% ← BENIGN (ignore)

Highest dangerous probability: 99.57%
```

### Step 4: Assign Risk Level Based on Dangerous Cancer Probability

The system uses these thresholds:

```python
if dangerous_cancer_probability > 85%:
    risk = "URGENT" 🚨
    # Very high confidence of dangerous cancer
    # Patient should see doctor IMMEDIATELY
    
elif dangerous_cancer_probability > 60%:
    risk = "HIGH" ⚠️
    # High confidence of dangerous cancer
    # Patient should see doctor SOON
    
elif dangerous_cancer_probability > 40%:
    risk = "MEDIUM" ⚡
    # Moderate confidence of dangerous cancer
    # Patient should monitor and consult doctor
    
else:
    risk = "LOW" ✓
    # Low confidence of dangerous cancer
    # Likely benign, but still monitor
```

## Real Examples

### Example 1: ISIC_0000198.jpg (Benign Mole)

**Step 1: AI Predictions**
```
melanocytic_Nevi: 99.90%
melanoma: 0.05%
basal_cell_carcinoma: 0.01%
```

**Step 2: Identify Dangerous Types**
- melanoma: 0.05% (dangerous)
- basal_cell_carcinoma: 0.01% (dangerous)

**Step 3: Highest Dangerous Probability**
- Max dangerous: 0.05%

**Step 4: Risk Assessment**
- 0.05% < 40% → **LOW RISK** ✓
- **Reason:** Very low chance of dangerous cancer, likely a harmless mole

---

### Example 2: ISIC_0000289.jpg (Melanoma)

**Step 1: AI Predictions**
```
melanoma: 99.57%
actinic_keratoses: 0.15%
melanocytic_Nevi: 0.12%
```

**Step 2: Identify Dangerous Types**
- melanoma: 99.57% (dangerous)
- actinic_keratoses: 0.15% (dangerous)

**Step 3: Highest Dangerous Probability**
- Max dangerous: 99.57%

**Step 4: Risk Assessment**
- 99.57% > 85% → **URGENT** 🚨
- **Reason:** Very high confidence of melanoma (deadly cancer)

---

### Example 3: Hypothetical Basal Cell Carcinoma

**Step 1: AI Predictions**
```
basal_cell_carcinoma: 75.0%
melanocytic_Nevi: 20.0%
melanoma: 3.0%
```

**Step 2: Identify Dangerous Types**
- basal_cell_carcinoma: 75.0% (dangerous)
- melanoma: 3.0% (dangerous)

**Step 3: Highest Dangerous Probability**
- Max dangerous: 75.0%

**Step 4: Risk Assessment**
- 75.0% > 60% → **HIGH** ⚠️
- **Reason:** High confidence of basal cell carcinoma (needs treatment)

## Why This Approach Works

### ❌ OLD APPROACH (Wrong)
```
If ANY prediction > 85% → URGENT
```
**Problem:** Marks benign moles as urgent just because the AI is confident!

### ✅ NEW APPROACH (Correct)
```
If DANGEROUS cancer > 85% → URGENT
```
**Benefit:** Only marks as urgent when there's high confidence of actual danger!

## Key Insights

1. **High confidence in benign = LOW risk**
   - 99% sure it's a harmless mole → LOW risk ✓

2. **High confidence in dangerous = URGENT**
   - 99% sure it's melanoma → URGENT 🚨

3. **Low confidence in dangerous = LOW risk**
   - 5% chance of melanoma → LOW risk ✓

4. **Moderate confidence in dangerous = MEDIUM/HIGH**
   - 50% chance of melanoma → MEDIUM ⚡
   - 70% chance of melanoma → HIGH ⚠️

## Medical Reasoning

This approach aligns with medical practice:

- **Benign lesions** (moles, skin tags) → Monitor, no urgency
- **Pre-cancerous lesions** (actinic keratoses) → Schedule appointment
- **Cancerous lesions** (melanoma, BCC) → Urgent medical attention

The AI helps triage patients by identifying which lesions need immediate attention vs routine monitoring.

## Summary

**Risk = How confident the AI is that it's a DANGEROUS cancer**

- Not just "how confident is the AI"
- But "how confident is the AI that this is DANGEROUS"

This prevents false alarms while catching real threats!
