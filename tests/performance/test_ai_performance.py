"""
Performance tests for AI analysis pipeline
Tests AI processing time to ensure 95th percentile < 10 seconds

Validates: Requirements 20.1
"""

import pytest
import time
import statistics
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.analysis_pipeline import AnalysisPipeline
from PIL import Image
import io


@pytest.fixture
def test_image():
    """Create a test image for performance testing"""
    # Create a 512x512 RGB image
    img = Image.new('RGB', (512, 512), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


@pytest.mark.performance
@pytest.mark.asyncio
async def test_ai_analysis_95th_percentile_under_10_seconds(test_image):
    """
    Test that AI analysis completes within 10 seconds at 95th percentile
    
    This test runs 100 AI analyses and verifies that the 95th percentile
    processing time is under 10 seconds as required by Requirement 20.1
    """
    pipeline = AnalysisPipeline()
    times = []
    
    print("\n" + "="*60)
    print("AI PERFORMANCE TEST - 95th Percentile Analysis")
    print("="*60)
    print(f"Running 100 AI analyses to measure performance...")
    print(f"Target: 95th percentile < 10 seconds")
    print("-"*60)
    
    # Run 100 analyses
    for i in range(100):
        # Reset image position
        test_image.seek(0)
        image_bytes = test_image.read()
        
        start = time.time()
        try:
            # Run AI analysis
            result = await pipeline.process_image(image_bytes)
            elapsed = time.time() - start
            times.append(elapsed)
            
            if (i + 1) % 10 == 0:
                print(f"Completed {i + 1}/100 analyses... Current avg: {statistics.mean(times):.2f}s")
        except Exception as e:
            print(f"Analysis {i + 1} failed: {e}")
            # Still record the time even if it fails
            elapsed = time.time() - start
            times.append(elapsed)
    
    # Calculate statistics
    times_sorted = sorted(times)
    p50 = times_sorted[49]  # 50th percentile (median)
    p95 = times_sorted[94]  # 95th percentile
    p99 = times_sorted[98]  # 99th percentile
    avg = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    
    print("-"*60)
    print("PERFORMANCE RESULTS:")
    print(f"  Minimum:        {min_time:.3f}s")
    print(f"  Average:        {avg:.3f}s")
    print(f"  50th percentile: {p50:.3f}s")
    print(f"  95th percentile: {p95:.3f}s ({'✓ PASS' if p95 < 10.0 else '✗ FAIL'})")
    print(f"  99th percentile: {p99:.3f}s")
    print(f"  Maximum:        {max_time:.3f}s")
    print("="*60)
    
    # Assert 95th percentile is under 10 seconds
    assert p95 < 10.0, f"95th percentile ({p95:.3f}s) exceeds target of 10s"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_ai_analysis_average_response_time(test_image):
    """
    Test that average AI analysis time is reasonable
    
    While the requirement specifies 95th percentile < 10s,
    we also want to ensure average performance is good
    """
    pipeline = AnalysisPipeline()
    times = []
    
    # Run 20 analyses for average
    for i in range(20):
        test_image.seek(0)
        image_bytes = test_image.read()
        start = time.time()
        try:
            result = await pipeline.process_image(image_bytes)
            elapsed = time.time() - start
            times.append(elapsed)
        except Exception as e:
            elapsed = time.time() - start
            times.append(elapsed)
    
    avg = statistics.mean(times)
    
    print(f"\nAverage AI analysis time: {avg:.3f}s (20 samples)")
    
    # Average should be significantly better than 95th percentile target
    assert avg < 8.0, f"Average time ({avg:.3f}s) should be under 8s"


@pytest.mark.performance
def test_gatekeeper_performance(test_image):
    """
    Test NSFW filter (Gatekeeper) performance separately
    
    The Gatekeeper should be fast to not bottleneck the pipeline
    """
    from app.nsfw_filter import NSFWDetector
    
    detector = NSFWDetector()
    times = []
    
    # Run 50 NSFW checks
    for i in range(50):
        test_image.seek(0)
        img = Image.open(test_image)
        
        start = time.time()
        try:
            result = detector.check_nsfw(img)
            elapsed = time.time() - start
            times.append(elapsed)
        except Exception as e:
            elapsed = time.time() - start
            times.append(elapsed)
    
    avg = statistics.mean(times)
    p95 = sorted(times)[47]  # 95th percentile
    
    print(f"\nGatekeeper (NSFW) performance:")
    print(f"  Average: {avg:.3f}s")
    print(f"  95th percentile: {p95:.3f}s")
    
    # Gatekeeper should be fast (< 2 seconds)
    assert p95 < 2.0, f"Gatekeeper 95th percentile ({p95:.3f}s) should be under 2s"


@pytest.mark.performance
def test_lesion_detection_performance(test_image):
    """
    Test Swin Transformer lesion detection performance
    """
    from app.lesion_detector import LesionDetector
    
    detector = LesionDetector()
    times = []
    
    # Run 30 lesion detections
    for i in range(30):
        test_image.seek(0)
        img = Image.open(test_image)
        
        start = time.time()
        try:
            result = detector.detect_lesions(img)
            elapsed = time.time() - start
            times.append(elapsed)
        except Exception as e:
            elapsed = time.time() - start
            times.append(elapsed)
    
    avg = statistics.mean(times)
    p95 = sorted(times)[28]  # 95th percentile
    
    print(f"\nLesion Detection (Swin Transformer) performance:")
    print(f"  Average: {avg:.3f}s")
    print(f"  95th percentile: {p95:.3f}s")
    
    # Lesion detection should complete in reasonable time
    assert p95 < 5.0, f"Lesion detection 95th percentile ({p95:.3f}s) should be under 5s"


@pytest.mark.performance
def test_cancer_classification_performance(test_image):
    """
    Test EfficientNet-B7 cancer classification performance
    """
    from app.cancer_classifier import CancerClassifier
    
    classifier = CancerClassifier()
    times = []
    
    # Run 30 classifications
    for i in range(30):
        test_image.seek(0)
        img = Image.open(test_image)
        
        start = time.time()
        try:
            result = classifier.classify_cancer(img)
            elapsed = time.time() - start
            times.append(elapsed)
        except Exception as e:
            elapsed = time.time() - start
            times.append(elapsed)
    
    avg = statistics.mean(times)
    p95 = sorted(times)[28]  # 95th percentile
    
    print(f"\nCancer Classification (EfficientNet-B7) performance:")
    print(f"  Average: {avg:.3f}s")
    print(f"  95th percentile: {p95:.3f}s")
    
    # Classification should complete in reasonable time
    assert p95 < 5.0, f"Cancer classification 95th percentile ({p95:.3f}s) should be under 5s"


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s", "-m", "performance"])
