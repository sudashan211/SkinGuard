"""
AI Model Infrastructure
Handles loading, caching, and management of AI models for medical analysis
Requirements: 4.1, 4.2
"""
import torch
import timm
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class ModelConfig:
    """Configuration for AI models"""
    
    # Model names from timm library
    SWIN_MODEL_NAME = "swin_base_patch4_window7_224"
    EFFICIENTNET_MODEL_NAME = "tf_efficientnet_b7"
    
    # Model storage paths
    MODEL_CACHE_DIR = Path("models/cache")
    
    # Device configuration
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Model input sizes
    SWIN_INPUT_SIZE = 224
    EFFICIENTNET_INPUT_SIZE = 600
    
    # Number of cancer classes
    NUM_CANCER_CLASSES = 7
    
    # Cancer type labels
    CANCER_TYPES = [
        "Melanoma",
        "Basal Cell Carcinoma",
        "Squamous Cell Carcinoma",
        "Actinic Keratosis",
        "Benign Keratosis",
        "Dermatofibroma",
        "Vascular Lesion"
    ]


class ModelLoadError(Exception):
    """Exception raised when model loading fails"""
    def __init__(self, model_name: str, reason: str):
        self.code = "MODEL_LOAD_ERROR"
        self.message = f"Failed to load model {model_name}: {reason}"
        self.status_code = 500
        super().__init__(self.message)


class ModelUnavailableError(Exception):
    """Exception raised when model service is unavailable"""
    def __init__(self, model_name: str):
        self.code = "MODEL_UNAVAILABLE"
        self.message = f"AI model {model_name} is currently unavailable"
        self.status_code = 503
        super().__init__(self.message)


class AIModelManager:
    """
    Manages AI model loading, caching, and lifecycle
    
    Implements singleton pattern with lazy loading for efficient resource usage.
    Models are loaded on first use and cached in memory.
    """
    
    _instance: Optional['AIModelManager'] = None
    _swin_model: Optional[torch.nn.Module] = None
    _efficientnet_model: Optional[torch.nn.Module] = None
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(AIModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize model manager"""
        if self._initialized:
            return
        
        self.config = ModelConfig()
        self.device = torch.device(self.config.DEVICE)
        
        # Create cache directory if it doesn't exist
        self.config.MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"AI Model Manager initialized on device: {self.device}")
        self._initialized = True
    
    def get_swin_model(self) -> torch.nn.Module:
        """
        Get Swin Transformer model for lesion detection
        
        Loads model on first call and caches for subsequent calls.
        
        Returns:
            Loaded Swin Transformer model
            
        Raises:
            ModelLoadError: If model loading fails
            ModelUnavailableError: If model service is unavailable
        """
        if self._swin_model is None:
            try:
                logger.info(f"Loading Swin Transformer model: {self.config.SWIN_MODEL_NAME}")
                
                # Load pre-trained Swin Transformer from timm
                # In production, this would load a fine-tuned model for skin lesion detection
                self._swin_model = timm.create_model(
                    self.config.SWIN_MODEL_NAME,
                    pretrained=True,
                    num_classes=self.config.NUM_CANCER_CLASSES
                )
                
                # Move model to appropriate device
                self._swin_model = self._swin_model.to(self.device)
                
                # Set to evaluation mode
                self._swin_model.eval()
                
                logger.info("Swin Transformer model loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to load Swin Transformer: {str(e)}")
                raise ModelLoadError(
                    model_name=self.config.SWIN_MODEL_NAME,
                    reason=str(e)
                )
        
        return self._swin_model
    
    def get_efficientnet_model(self) -> torch.nn.Module:
        """
        Get EfficientNet-B7 model for cancer classification
        
        Loads model on first call and caches for subsequent calls.
        
        Returns:
            Loaded EfficientNet-B7 model
            
        Raises:
            ModelLoadError: If model loading fails
            ModelUnavailableError: If model service is unavailable
        """
        if self._efficientnet_model is None:
            try:
                logger.info(f"Loading EfficientNet-B7 model: {self.config.EFFICIENTNET_MODEL_NAME}")
                
                # Load pre-trained EfficientNet-B7 from timm
                # In production, this would load a fine-tuned model for skin cancer classification
                self._efficientnet_model = timm.create_model(
                    self.config.EFFICIENTNET_MODEL_NAME,
                    pretrained=True,
                    num_classes=self.config.NUM_CANCER_CLASSES
                )
                
                # Move model to appropriate device
                self._efficientnet_model = self._efficientnet_model.to(self.device)
                
                # Set to evaluation mode
                self._efficientnet_model.eval()
                
                logger.info("EfficientNet-B7 model loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to load EfficientNet-B7: {str(e)}")
                raise ModelLoadError(
                    model_name=self.config.EFFICIENTNET_MODEL_NAME,
                    reason=str(e)
                )
        
        return self._efficientnet_model
    
    def unload_models(self):
        """
        Unload models from memory
        
        Useful for testing or when models need to be reloaded
        """
        if self._swin_model is not None:
            del self._swin_model
            self._swin_model = None
            logger.info("Swin Transformer model unloaded")
        
        if self._efficientnet_model is not None:
            del self._efficientnet_model
            self._efficientnet_model = None
            logger.info("EfficientNet-B7 model unloaded")
        
        # Clear CUDA cache if using GPU
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about loaded models
        
        Returns:
            Dictionary with model status and configuration
        """
        return {
            "device": str(self.device),
            "swin_loaded": self._swin_model is not None,
            "efficientnet_loaded": self._efficientnet_model is not None,
            "swin_model_name": self.config.SWIN_MODEL_NAME,
            "efficientnet_model_name": self.config.EFFICIENTNET_MODEL_NAME,
            "num_cancer_classes": self.config.NUM_CANCER_CLASSES,
            "cancer_types": self.config.CANCER_TYPES,
            "cuda_available": torch.cuda.is_available()
        }
    
    def warmup_models(self):
        """
        Pre-load both models to reduce first-request latency
        
        Call this during application startup for better performance
        """
        logger.info("Warming up AI models...")
        try:
            self.get_swin_model()
            self.get_efficientnet_model()
            logger.info("AI models warmed up successfully")
        except Exception as e:
            logger.error(f"Failed to warm up models: {str(e)}")
            raise


# Global model manager instance
model_manager = AIModelManager()


@lru_cache(maxsize=1)
def get_model_manager() -> AIModelManager:
    """
    Get the global model manager instance
    
    Uses LRU cache to ensure singleton behavior
    
    Returns:
        AIModelManager instance
    """
    return model_manager
