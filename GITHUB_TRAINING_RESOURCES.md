# GitHub Resources for Skin Cancer ViT Training & EDA

Based on my search, here are the best GitHub repositories with training code and EDA notebooks for skin cancer classification using Vision Transformers and HAM10000 dataset.

## 🎯 **BEST MATCH: Vision Transformer on HAM10000**

### 1. **ckorgial/ViT-for-Cancer-Skin-Classification-TensorFlow** ⭐⭐⭐⭐⭐
- **URL:** https://github.com/ckorgial/ViT-for-Cancer-Skin-Classification-TensorFlow
- **Notebook:** `ViT_HAM10000.ipynb`
- **Description:** Cancer Skin Classification (HAM10000) using Vision Transformer (ViT)
- **Features:**
  - ✅ Complete ViT training notebook
  - ✅ Uses HAM10000 dataset (same as yours)
  - ✅ Tests different ViT architectures (ViT B-32 and ViT B-16)
  - ✅ Transfer learning with frozen layers
  - ✅ TensorFlow implementation
- **Stars:** 8 stars, 4 forks
- **License:** MIT

**Direct Notebook Link:**
https://github.com/ckorgial/ViT-for-Cancer-Skin-Classification-TensorFlow/blob/main/ViT_HAM10000.ipynb

---

## 📊 **Other Excellent Resources**

### 2. **h-ssiqueira/SkinLesionAI**
- **URL:** https://github.com/h-ssiqueira/SkinLesionAI
- **Description:** Notebooks of pre-trained models using the HAM10000 dataset
- **Features:**
  - ✅ Multiple CNN architectures
  - ✅ HAM10000 dataset (7 skin cancer classes)
  - ✅ Pre-trained models
  - ✅ Complete training notebooks

### 3. **charanhu/Skin_Cancer_Detection_MNIST**
- **URL:** https://github.com/charanhu/Skin_Cancer_Detection_MNIST
- **Description:** Deep learning model for 7 classes of skin cancer
- **Features:**
  - ✅ 10,015 dermatoscopic images
  - ✅ Training notebooks
  - ✅ Academic machine learning purposes

### 4. **Defcon27/Skin-Cancer-Classification-using-Transfer-Learning**
- **URL:** https://github.com/Defcon27/Skin-Cancer-Classification-using-Transfer-Learning
- **Notebook:** `Skin Cancer Prediction VGG16.ipynb`
- **Description:** Multi-class classification using transfer learning on HAM10000
- **Features:**
  - ✅ Transfer learning approach
  - ✅ VGG16 architecture
  - ✅ Complete training notebook
  - ✅ HAM10000 dataset

### 5. **PROxZIMA/Skin-Cancer-MNIST-HAM10000**
- **URL:** https://github.com/PROxZIMA/Skin-Cancer-MNIST-HAM10000
- **Description:** Comparison of multiple architectures
- **Features:**
  - ✅ ResNet50 vs Inception-V3 vs VGG-19 vs VGG-16 vs GoogLeNet
  - ✅ HAM10000 dataset
  - ✅ Model comparison notebooks

### 6. **NeerajNamani/Multi-Class-Skin-Cancer-Classification**
- **URL:** https://github.com/NeerajNamani/Multi-Class-Skin-Cancer-Classification
- **Description:** EfficientNet implementation for skin cancer classification
- **Features:**
  - ✅ EfficientNet architecture
  - ✅ Comprehensive code and documentation
  - ✅ Multi-class classification

### 7. **yaopengUSTC/mbit-skin-cancer**
- **URL:** https://github.com/yaopengUSTC/mbit-skin-cancer
- **Paper:** https://arxiv.org/abs/2102.01284
- **Description:** Official PyTorch implementation of research paper
- **Features:**
  - ✅ Research-grade implementation
  - ✅ Handles imbalanced datasets
  - ✅ Single model deep learning
  - ✅ Published paper with methodology

### 8. **skrantidatta/Attention-based-Skin-Cancer-Classification**
- **URL:** https://github.com/skrantidatta/Attention-based-Skin-Cancer-Classification
- **Description:** Attention mechanism for skin cancer classification
- **Features:**
  - ✅ Soft-Attention mechanism
  - ✅ Focus on important image regions
  - ✅ Clinical application focus

---

## 🔍 **How to Use These Resources**

### **For ViT Training (Recommended):**
1. Clone the repository:
   ```bash
   git clone https://github.com/ckorgial/ViT-for-Cancer-Skin-Classification-TensorFlow.git
   ```

2. Open the notebook:
   ```bash
   cd ViT-for-Cancer-Skin-Classification-TensorFlow
   jupyter notebook ViT_HAM10000.ipynb
   ```

3. Adapt to your HAM10000 dataset location:
   - Update dataset paths to point to your `HAM10000_images_part_1/` and `HAM10000_images_part_2/`
   - Modify preprocessing if needed
   - Adjust hyperparameters

### **For EDA and Preprocessing:**
Most repositories include:
- Data loading and exploration
- Class distribution analysis
- Image preprocessing pipelines
- Data augmentation techniques
- Train/validation/test splits

---

## 📚 **Additional Resources**

### **Hugging Face Models (Similar to Anwarkh1):**
1. **mramjad/skin_disease** - https://huggingface.co/mramjad/skin_disease
2. **syaha/skin_cancer_detection_model** - https://huggingface.co/syaha/skin_cancer_detection_model
3. **jamus0702/skin-disease-classification** - https://huggingface.co/jamus0702/skin-disease-classification

### **Datasets on Hugging Face:**
1. **Falah/skin-cancer** - https://huggingface.co/datasets/Falah/skin-cancer
2. **marmal88/skin_cancer** - https://huggingface.co/datasets/marmal88/skin_cancer (used by Anwarkh1)

---

## 🎓 **Learning Path**

### **Step 1: Understand the Data (EDA)**
- Use notebooks from `h-ssiqueira/SkinLesionAI` or `charanhu/Skin_Cancer_Detection_MNIST`
- Explore class distributions
- Analyze image properties
- Identify data imbalances

### **Step 2: Learn Preprocessing**
- Study preprocessing pipelines in the ViT notebook
- Understand data augmentation techniques
- Learn normalization strategies

### **Step 3: Train Your Own Model**
- Start with `ckorgial/ViT-for-Cancer-Skin-Classification-TensorFlow`
- Experiment with different ViT architectures
- Fine-tune hyperparameters
- Compare with your current model (Anwarkh1)

### **Step 4: Evaluate and Compare**
- Use metrics from multiple repositories
- Compare accuracy, precision, recall, F1-score
- Analyze confusion matrices
- Test on your own images

---

## 💡 **Key Takeaways**

1. **Best ViT Resource:** `ckorgial/ViT-for-Cancer-Skin-Classification-TensorFlow` - Direct ViT implementation on HAM10000
2. **Most Comprehensive:** `h-ssiqueira/SkinLesionAI` - Multiple models and notebooks
3. **Research Quality:** `yaopengUSTC/mbit-skin-cancer` - Published paper implementation
4. **Model Comparison:** `PROxZIMA/Skin-Cancer-MNIST-HAM10000` - Compare multiple architectures

---

## 🚀 **Next Steps for Your Project**

1. **Clone the ViT repository** and study the training notebook
2. **Adapt the code** to your HAM10000 dataset location
3. **Run EDA** to understand your data distribution
4. **Train a custom model** and compare with Anwarkh1's model
5. **Integrate** the best-performing model into your SkinGuard application

---

## 📝 **Note**

The original Anwarkh1 model training code is **NOT publicly available**. However, these repositories provide similar or better implementations that you can use to:
- Understand how ViT models are trained on skin cancer data
- Reproduce similar results
- Create your own custom model
- Improve upon the existing model

All repositories are open-source and available for academic and research purposes.
