# Quick Reference: 7 Skin Lesion Types

## At a Glance

### 🔴 MALIGNANT (Cancerous - Require Treatment)

#### 1. Melanoma ⚠️ MOST DANGEROUS
- **Risk**: Life-threatening if not treated early
- **Appearance**: Asymmetrical, irregular borders, multiple colors
- **Action**: URGENT medical attention
- **Survival**: 99% if caught early, 27% if advanced

#### 2. Basal Cell Carcinoma
- **Risk**: Locally destructive, rarely spreads
- **Appearance**: Pearly bump, flat scar-like lesion
- **Action**: Prompt treatment needed
- **Prognosis**: Excellent with treatment

#### 3. Squamous Cell Carcinoma
- **Risk**: Can spread if untreated
- **Appearance**: Firm red nodule, scaly crusted surface
- **Action**: Prompt treatment needed
- **Prognosis**: 95% survival if caught early

---

### 🟡 PRECANCEROUS (Monitor & Treat)

#### 4. Actinic Keratosis
- **Risk**: 5-10% chance of becoming cancer
- **Appearance**: Rough, dry, scaly patch
- **Action**: Treatment recommended
- **Prognosis**: Excellent with treatment

---

### 🟢 BENIGN (Non-Cancerous - Usually No Treatment)

#### 5. Benign Keratosis (Seborrheic Keratosis)
- **Risk**: None - completely benign
- **Appearance**: Waxy, scaly, "stuck-on" look
- **Action**: No treatment needed (cosmetic removal optional)
- **Prognosis**: Harmless

#### 6. Dermatofibroma
- **Risk**: None - completely benign
- **Appearance**: Firm bump, dimples when pinched
- **Action**: No treatment needed (removal optional)
- **Prognosis**: Harmless

#### 7. Vascular Lesion
- **Risk**: None - completely benign
- **Appearance**: Red/purple/blue, may blanch when pressed
- **Action**: No treatment needed (cosmetic removal optional)
- **Prognosis**: Harmless

---

## Risk Priority

```
URGENT:     Melanoma
HIGH:       Basal Cell Carcinoma, Squamous Cell Carcinoma
MODERATE:   Actinic Keratosis
LOW:        Benign Keratosis, Dermatofibroma, Vascular Lesion
```

---

## When to See a Doctor

### 🚨 IMMEDIATELY:
- AI predicts Melanoma
- Rapidly changing mole
- Bleeding lesion
- Asymmetrical with irregular borders

### 📅 WITHIN 1-2 WEEKS:
- AI predicts any malignant type
- New growth that doesn't heal
- Persistent scaly patch
- Actinic keratosis

### 👁️ ROUTINE MONITORING:
- Benign lesions
- Stable moles
- Annual skin checks

---

## ABCDE Rule (Melanoma Warning Signs)

- **A**symmetry - One half doesn't match
- **B**order - Irregular, scalloped edges
- **C**olor - Multiple colors (brown, black, red, white, blue)
- **D**iameter - Larger than 6mm (pencil eraser)
- **E**volving - Changing size, shape, or color

---

## Model Output Example

When you upload an image, the AI returns:

```json
{
  "predictions": [
    {"type": "Melanoma", "probability": 0.45, "confidence": 0.89},
    {"type": "Benign Keratosis", "probability": 0.28, "confidence": 0.82},
    {"type": "Basal Cell Carcinoma", "probability": 0.15, "confidence": 0.75},
    {"type": "Squamous Cell Carcinoma", "probability": 0.08, "confidence": 0.68},
    {"type": "Actinic Keratosis", "probability": 0.02, "confidence": 0.55},
    {"type": "Dermatofibroma", "probability": 0.01, "confidence": 0.50},
    {"type": "Vascular Lesion", "probability": 0.01, "confidence": 0.48}
  ],
  "risk_level": "medium",
  "hotspots": [...]
}
```

---

## Important Notes

⚠️ **This is a screening tool, NOT a diagnostic tool**

- AI predictions are estimates
- Always consult a dermatologist
- Early detection saves lives
- Regular skin checks are essential

✅ **Best Practices**

- Upload clear, well-lit images
- Close-up of lesion (not full body)
- Minimum 512x512 resolution
- Consult doctor for any concerns

---

For detailed information, see **SKIN_LESION_TYPES_GUIDE.md**
