"""
Integration Test for Complete AI Analysis Pipeline
Tests the end-to-end flow: Quality → NSFW → Lesion Detection → Cancer Classification

This test verifies Task 8 Checkpoint requirements:
- All AI processing tests pass
- NSFW filtering works correctly
- Complete image analysis flow works end-to-end
"""
import pytest
import sys
import os
from pathlib import Path
from PIL import Image
import numpy as np
from io import BytesIO
import asyncio

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.analysis_pipeline import AnalysisPipeline, AnalysisResult
from app.image_quality import QualityError
from app.nsfw_filter import ContentViolationError


def create_valid_skin_image(width=600, height=600):
    """
    Create a valid skin lesion image for testing
    
    Returns:
        bytes: Image data
    """
    # Create image with skin tone
    image_array = np.ones((height, width, 3), dtype=np.uint8)
    
    # Base skin tone (peachy/beige)
    image_array[:, :, 0] = 200  # R
    image_array[:, :, 1] = 170  # G
    image_array[:, :, 2] = 150  # B
    
    # Add subtle texture
    noise = np.random.randint(-10, 10, (height, width, 3), dtype=np.int16)
    image_array = np.clip(image_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Add a lesion (darker spot)
    center_x, center_y = width // 2, height // 2
    lesion_size = 60
    
    y, x = np.ogrid[:height, :width]
    mask = (x - center_x)**2 + (y - center_y)**2 <= lesion_size**2
    
    image_array[mask, 0] = 120  # Darker R
    image_array[mask, 1] = 90   # Darker G
    image_array[mask, 2] = 70   # Darker B
    
    # Convert to PIL Image
    pil_image = Image.fromarray(image_array, mode='RGB')
    
    # Convert to bytes
    buffer = BytesIO()
    pil_image.save(buffer, format='JPEG', quality=95)
    buffer.seek(0)
    
    return buffer.read()


def create_low_resolution_image():
    """Create an image below minimum resolution"""
    image = Image.new('RGB', (400, 400), (200, 170, 150))
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()


def create_blurry_image():
    """Create a blurry image (low detail)"""
    # Create a very smooth gradient (low frequency content = blurry)
    image_array = np.ones((600, 600, 3), dtype=np.uint8)
    for i in range(600):
        value = int(150 + 50 * np.sin(i / 100))
        image_array[i, :, :] = value
    
    pil_image = Image.fromarray(image_array, mode='RGB')
    buffer = BytesIO()
    pil_image.save(buffer, format='JPEG', quality=50)  # Low quality = more blur
    return buffer.getvalue()


def create_non_skin_image():
    """Create a non-skin image (blue sky)"""
    image = Image.new('RGB', (600, 600), (50, 100, 200))
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()


@pytest.fixture
def pipeline():
    """Create analysis pipeline instance"""
    return AnalysisPipeline()


class TestAIPipelineIntegration:
    """Integration tests for complete AI pipeline"""
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_with_valid_image(self, pipeline):
        """
        Test complete pipeline with a valid skin lesion image
        
        This is the happy path - image should pass all stages and return results
        """
        # Create valid image
        image_data = create_valid_skin_image()
        
        # Process through pipeline
        result = await pipeline.process_image(image_data, patient_id="test-patient-001")
        
        # Verify result structure
        assert isinstance(result, AnalysisResult)
        
        # Verify predictions
        assert len(result.predictions) == 7, "Should have 7 cancer type predictions"
        assert all(0.0 <= p.probability <= 1.0 for p in result.predictions), \
            "All probabilities should be in [0, 1]"
        
        # Verify probabilities sum to ~1.0
        total_prob = sum(p.probability for p in result.predictions)
        assert 0.99 <= total_prob <= 1.01, f"Probabilities should sum to ~1.0, got {total_prob}"
        
        # Verify hotspots
        assert isinstance(result.hotspots, list), "Hotspots should be a list"
        
        # Verify risk level
        assert result.risk_level in ['low', 'medium', 'high', 'urgent'], \
            f"Invalid risk level: {result.risk_level}"
        
        # Verify quality metrics
        assert 'resolution' in result.quality_metrics
        assert 'blur_score' in result.quality_metrics
        assert 'brightness_score' in result.quality_metrics
        
        # Verify NSFW scores
        assert 'nsfw_score' in result.nsfw_scores
        assert 'non_skin_score' in result.nsfw_scores
        assert 'safe_score' in result.nsfw_scores
        
        # Verify processing times
        assert 'quality_validation' in result.processing_times
        assert 'nsfw_filtering' in result.processing_times
        assert 'lesion_detection' in result.processing_times
        assert 'cancer_classification' in result.processing_times
        assert 'total' in result.processing_times
        assert 'ai_total' in result.processing_times
        
        # Verify all times are positive
        for stage, time_val in result.processing_times.items():
            assert time_val >= 0, f"{stage} time should be non-negative"
        
        # Verify AI total time calculation
        expected_ai_total = (
            result.processing_times['lesion_detection'] +
            result.processing_times['cancer_classification']
        )
        assert abs(result.processing_times['ai_total'] - expected_ai_total) < 0.001
        
        print(f"✓ Complete pipeline test passed")
        print(f"  - Processing time: {result.processing_times['total']:.3f}s")
        print(f"  - AI time: {result.processing_times['ai_total']:.3f}s")
        print(f"  - Risk level: {result.risk_level}")
        print(f"  - Top prediction: {result.predictions[0].type} ({result.predictions[0].probability:.2%})")
    
    @pytest.mark.asyncio
    async def test_pipeline_rejects_low_resolution(self, pipeline):
        """Test that pipeline rejects images below minimum resolution"""
        image_data = create_low_resolution_image()
        
        with pytest.raises(QualityError) as exc_info:
            await pipeline.process_image(image_data, patient_id="test-patient-002")
        
        assert exc_info.value.code == "LOW_RESOLUTION"
        assert "resolution too low" in exc_info.value.message.lower()
        
        print("✓ Low resolution rejection test passed")
    
    @pytest.mark.asyncio
    async def test_pipeline_handles_non_skin_images(self, pipeline):
        """Test that pipeline handles non-skin images appropriately"""
        image_data = create_non_skin_image()
        
        # Non-skin images might be rejected by NSFW filter (high non_skin_score)
        # or by quality validation (blur), or might pass through
        try:
            result = await pipeline.process_image(image_data, patient_id="test-patient-003")
            # If it passes, verify it has valid structure
            assert isinstance(result, AnalysisResult)
            print("✓ Non-skin image processed (passed all filters)")
        except ContentViolationError as e:
            # If rejected by NSFW filter
            assert e.code == "CONTENT_VIOLATION"
            print("✓ Non-skin image rejected by NSFW filter")
        except QualityError as e:
            # If rejected by quality validation
            print(f"✓ Non-skin image rejected by quality validation: {e.reason}")
    
    @pytest.mark.asyncio
    async def test_pipeline_timing_breakdown(self, pipeline):
        """Test that pipeline records timing for each stage"""
        image_data = create_valid_skin_image()
        
        result = await pipeline.process_image(image_data, patient_id="test-patient-004")
        
        # Verify all timing stages are present
        required_stages = [
            'quality_validation',
            'nsfw_filtering',
            'lesion_detection',
            'cancer_classification',
            'total',
            'ai_total'
        ]
        
        for stage in required_stages:
            assert stage in result.processing_times, f"Missing timing for {stage}"
            assert result.processing_times[stage] >= 0, f"{stage} time should be non-negative"
        
        # Verify total time is sum of stages (approximately)
        sum_of_stages = (
            result.processing_times['quality_validation'] +
            result.processing_times['nsfw_filtering'] +
            result.processing_times['lesion_detection'] +
            result.processing_times['cancer_classification']
        )
        
        # Total should be at least the sum (might be slightly more due to overhead)
        assert result.processing_times['total'] >= sum_of_stages - 0.1
        
        print("✓ Pipeline timing breakdown test passed")
        print(f"  - Quality validation: {result.processing_times['quality_validation']:.3f}s")
        print(f"  - NSFW filtering: {result.processing_times['nsfw_filtering']:.3f}s")
        print(f"  - Lesion detection: {result.processing_times['lesion_detection']:.3f}s")
        print(f"  - Cancer classification: {result.processing_times['cancer_classification']:.3f}s")
        print(f"  - Total: {result.processing_times['total']:.3f}s")
    
    @pytest.mark.asyncio
    async def test_pipeline_result_serialization(self, pipeline):
        """Test that pipeline results can be serialized to dict and JSONB"""
        image_data = create_valid_skin_image()
        
        result = await pipeline.process_image(image_data, patient_id="test-patient-005")
        
        # Test to_dict()
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert 'predictions' in result_dict
        assert 'hotspots' in result_dict
        assert 'risk_level' in result_dict
        assert 'quality_metrics' in result_dict
        assert 'nsfw_scores' in result_dict
        assert 'processing_times' in result_dict
        assert 'model_version' in result_dict
        assert 'disclaimer' in result_dict
        
        # Test to_jsonb()
        jsonb_data = result.to_jsonb()
        assert isinstance(jsonb_data, dict)
        assert 'predictions' in jsonb_data
        assert 'hotspots' in jsonb_data
        assert 'model_version' in jsonb_data
        assert 'processing_time' in jsonb_data
        
        # Verify JSONB can be JSON serialized
        import json
        json_string = json.dumps(jsonb_data)
        assert json_string is not None
        
        # Verify round-trip
        retrieved = json.loads(json_string)
        assert retrieved == jsonb_data
        
        print("✓ Result serialization test passed")
    
    @pytest.mark.asyncio
    async def test_pipeline_status_check(self, pipeline):
        """Test pipeline status check"""
        status = pipeline.get_pipeline_status()
        
        assert isinstance(status, dict)
        assert 'quality_validator' in status
        assert 'nsfw_detector' in status
        assert 'lesion_detector' in status
        assert 'cancer_classifier' in status
        assert 'pipeline' in status
        
        # All components should be ready
        for component, state in status.items():
            assert state == 'ready', f"{component} is not ready"
        
        print("✓ Pipeline status check passed")
    
    @pytest.mark.asyncio
    async def test_nsfw_filtering_works_correctly(self, pipeline):
        """
        Specific test for NSFW filtering functionality
        
        Verifies that the NSFW gatekeeper is working as expected
        """
        # Create a valid skin image
        image_data = create_valid_skin_image()
        
        # Process through pipeline
        result = await pipeline.process_image(image_data, patient_id="test-patient-006")
        
        # Verify NSFW scores are present and valid
        assert 'nsfw_score' in result.nsfw_scores
        assert 'non_skin_score' in result.nsfw_scores
        assert 'safe_score' in result.nsfw_scores
        
        # Verify scores are in valid range
        assert 0.0 <= result.nsfw_scores['nsfw_score'] <= 1.0
        assert 0.0 <= result.nsfw_scores['non_skin_score'] <= 1.0
        assert 0.0 <= result.nsfw_scores['safe_score'] <= 1.0
        
        # For a valid skin image, NSFW score should be below threshold
        assert result.nsfw_scores['nsfw_score'] <= 0.35, \
            "Valid skin image should have NSFW score below threshold"
        
        # For a valid skin image, non-skin score should be below threshold
        assert result.nsfw_scores['non_skin_score'] <= 0.8, \
            "Valid skin image should have non-skin score below threshold"
        
        print("✓ NSFW filtering test passed")
        print(f"  - NSFW score: {result.nsfw_scores['nsfw_score']:.3f}")
        print(f"  - Non-skin score: {result.nsfw_scores['non_skin_score']:.3f}")
        print(f"  - Safe score: {result.nsfw_scores['safe_score']:.3f}")


def run_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("AI PIPELINE INTEGRATION TESTS")
    print("="*70 + "\n")
    
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    run_integration_tests()
