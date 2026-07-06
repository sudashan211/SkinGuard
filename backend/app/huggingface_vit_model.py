"""
Hugging Face Vision Transformer Model Integration
Model: Anwarkh1/Skin_Cancer-Image_Classification
Accuracy: 96.95% (validation)

This module provides integration with a pre-trained ViT model
that achieves 96.95% accuracy on skin cancer classification.
"""
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import torch
import io
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class HuggingFaceViTClassifier:
    """
    Skin cancer classifier using Hugging Face Vision Transformer
    
    Model: Anwarkh1/Skin_Cancer-Image_Classification
    Architecture: Vision Transformer (ViT)
    Accuracy: 96.95% on validation set
    
    Classes:
    1. Melanoma
    2. Basal Cell Carcinoma
    3. Actinic Keratoses
    4. Benign Keratosis-like lesions
    5. Vascular Lesions
    6. Melanocytic Nevi
    7. Dermatofibroma
    """
    
    def __init__(self):
        """Initialize the Hugging Face ViT model"""
        self.model_name = "Anwarkh1/Skin_Cancer-Image_Classification"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        logger.info(f"Loading Hugging Face ViT model: {self.model_name}")
        logger.info(f"Device: {self.device}")
        
        try:
            # Load image processor and model
            logger.info("Downloading model from Hugging Face Hub...")
            self.processor = ViTImageProcessor.from_pretrained(self.model_name)
            self.model = ViTForImageClassification.from_pretrained(self.model_name)
            
            # Move to device and set to eval mode
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # Get class labels
            self.id2label = self.model.config.id2label
            self.label2id = self.model.config.label2id
            
            logger.info(f"✓ Model loaded successfully!")
            logger.info(f"✓ Model accuracy: 96.95% (validation)")
            logger.info(f"✓ Number of classes: {len(self.id2label)}")
            logger.info(f"✓ Classes: {list(self.id2label.values())}")
            
        except Exception as e:
            logger.error(f"Failed to load Hugging Face model: {e}")
            logger.error("Make sure you have internet connection and transformers installed:")
            logger.error("  pip install transformers torch pillow")
            raise
    
    def predict(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Predict skin cancer type from image bytes
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            List of predictions with probabilities, sorted by confidence
            Format: [{'cancer_type': str, 'probability': float, 'confidence': float}, ...]
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Preprocess image
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)[0]
            
            # Format predictions
            predictions = []
            for idx, prob in enumerate(probs):
                cancer_type = self.id2label[idx]
                predictions.append({
                    'cancer_type': cancer_type,
                    'probability': float(prob),
                    'confidence': float(prob)
                })
            
            # Sort by probability (highest first)
            predictions.sort(key=lambda x: x['probability'], reverse=True)
            
            logger.info(f"✓ Prediction complete: {predictions[0]['cancer_type']} ({predictions[0]['probability']:.2%})")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "architecture": "Vision Transformer (ViT)",
            "accuracy": "96.95%",
            "num_classes": len(self.id2label),
            "classes": list(self.id2label.values()),
            "device": str(self.device),
            "source": "Hugging Face Hub",
            "url": f"https://huggingface.co/{self.model_name}"
        }


# Singleton instance
_classifier_instance = None


def get_huggingface_classifier() -> HuggingFaceViTClassifier:
    """
    Get singleton instance of Hugging Face classifier
    
    Returns:
        HuggingFaceViTClassifier instance
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = HuggingFaceViTClassifier()
    return _classifier_instance
