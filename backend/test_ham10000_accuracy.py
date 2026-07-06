"""
Test Hugging Face ViT Model on HAM10000 Dataset
Validates model accuracy on real medical images
"""
import sys
import os
from pathlib import Path
import random
import csv
from typing import List, Dict, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.huggingface_vit_model import HuggingFaceViTClassifier


def load_metadata(metadata_path: str = "../dataverse_files/HAM10000_metadata") -> Dict[str, str]:
    """
    Load HAM10000 metadata file
    
    Returns:
        Dictionary mapping image_id to diagnosis (dx)
    """
    # Try multiple possible paths
    possible_paths = [
        metadata_path,
        "dataverse_files/HAM10000_metadata",
        "../dataverse_files/HAM10000_metadata"
    ]
    
    metadata = {}
    found_path = None
    
    for path in possible_paths:
        if os.path.exists(path):
            found_path = path
            break
    
    if not found_path:
        print(f"⚠️  Metadata file not found in any of these locations:")
        for path in possible_paths:
            print(f"    - {path}")
        return metadata
    
    try:
        with open(found_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                image_id = row['image_id']
                dx = row['dx']  # Diagnosis
                metadata[image_id] = dx
        
        print(f"✓ Loaded metadata for {len(metadata)} images")
        return metadata
    
    except Exception as e:
        print(f"⚠️  Error loading metadata: {e}")
        return {}


def get_ham10000_images(num_samples: int = 20) -> List[str]:
    """Get random sample of HAM10000 images"""
    # Check both relative paths (from backend folder and from root)
    possible_paths = [
        (Path("HAM10000_images_part_1"), Path("HAM10000_images_part_2")),
        (Path("../HAM10000_images_part_1"), Path("../HAM10000_images_part_2"))
    ]
    
    part1_dir = None
    part2_dir = None
    
    for p1, p2 in possible_paths:
        if p1.exists():
            part1_dir = p1
            part2_dir = p2
            break
    
    images = []
    
    # Get images from part 1
    if part1_dir and part1_dir.exists():
        images.extend([str(f) for f in part1_dir.glob("*.jpg")])
    
    # Get images from part 2
    if part2_dir and part2_dir.exists():
        images.extend([str(f) for f in part2_dir.glob("*.jpg")])
    
    if not images:
        print("❌ No HAM10000 images found!")
        print("Make sure HAM10000_images_part_1 and HAM10000_images_part_2 folders exist")
        return []
    
    # Random sample
    if len(images) > num_samples:
        images = random.sample(images, num_samples)
    
    return images


def map_ham_to_model_labels(ham_label: str) -> str:
    """
    Map HAM10000 labels to model labels
    
    HAM10000 uses these labels:
    - nv: Melanocytic nevi (moles)
    - mel: Melanoma
    - bkl: Benign keratosis-like lesions
    - bcc: Basal cell carcinoma
    - akiec: Actinic keratoses
    - vasc: Vascular lesions
    - df: Dermatofibroma
    """
    mapping = {
        'nv': 'melanocytic_Nevi',
        'mel': 'melanoma',
        'bkl': 'benign_keratosis-like_lesions',
        'bcc': 'basal_cell_carcinoma',
        'akiec': 'actinic_keratoses',
        'vasc': 'vascular_lesions',
        'df': 'dermatofibroma'
    }
    return mapping.get(ham_label, ham_label)


def test_single_image(classifier: HuggingFaceViTClassifier, image_path: str, metadata: Dict[str, str]) -> Dict:
    """Test model on a single image"""
    try:
        # Load image
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # Get predictions
        predictions = classifier.predict(image_bytes)
        
        # Get top prediction
        top_pred = predictions[0]
        
        # Get ground truth from metadata
        image_id = Path(image_path).stem  # e.g., "ISIC_0027419"
        actual_dx = metadata.get(image_id, None)
        actual_label = map_ham_to_model_labels(actual_dx) if actual_dx else None
        
        # Check if prediction is correct
        is_correct = None
        if actual_label:
            is_correct = (top_pred['cancer_type'].lower() == actual_label.lower())
        
        return {
            'image': Path(image_path).name,
            'image_id': image_id,
            'predicted': top_pred['cancer_type'],
            'actual': actual_label,
            'actual_dx': actual_dx,
            'confidence': top_pred['probability'],
            'correct': is_correct,
            'success': True
        }
    
    except Exception as e:
        return {
            'image': Path(image_path).name,
            'predicted': None,
            'actual': None,
            'confidence': 0.0,
            'correct': None,
            'success': False,
            'error': str(e)
        }


def test_batch(classifier: HuggingFaceViTClassifier, images: List[str], metadata: Dict[str, str]) -> List[Dict]:
    """Test model on batch of images"""
    results = []
    
    print(f"\n🔬 Testing model on {len(images)} HAM10000 images...")
    print("=" * 80)
    
    for i, image_path in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] Testing: {Path(image_path).name}")
        
        result = test_single_image(classifier, image_path, metadata)
        results.append(result)
        
        if result['success']:
            print(f"  ✓ Predicted: {result['predicted']} ({result['confidence']:.2%})")
            if result['actual']:
                if result['correct']:
                    print(f"  ✓ Actual: {result['actual']} - CORRECT ✓")
                else:
                    print(f"  ✗ Actual: {result['actual']} - WRONG ✗")
        else:
            print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
    
    return results


def analyze_results(results: List[Dict], has_metadata: bool):
    """Analyze and display test results"""
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    # Count successes
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\nTotal Images Tested: {len(results)}")
    print(f"Successful Predictions: {len(successful)}")
    print(f"Failed Predictions: {len(failed)}")
    
    if not successful:
        print("\n❌ No successful predictions to analyze")
        return
    
    # Calculate accuracy if we have ground truth
    if has_metadata:
        with_labels = [r for r in successful if r['actual'] is not None]
        if with_labels:
            correct = [r for r in with_labels if r['correct']]
            accuracy = len(correct) / len(with_labels) * 100
            
            print("\n" + "=" * 80)
            print("🎯 ACCURACY RESULTS")
            print("=" * 80)
            print(f"\nImages with ground truth: {len(with_labels)}")
            print(f"Correct predictions: {len(correct)}")
            print(f"Incorrect predictions: {len(with_labels) - len(correct)}")
            print(f"\n📈 ACCURACY: {accuracy:.2f}%")
            
            if accuracy >= 90:
                print("   🎉 Excellent! Model performing as expected!")
            elif accuracy >= 75:
                print("   ✓ Good accuracy for medical AI")
            elif accuracy >= 60:
                print("   ⚠️  Moderate accuracy, may need improvement")
            else:
                print("   ❌ Low accuracy, investigation needed")
    
    # Analyze predictions by type
    print("\n" + "-" * 80)
    print("PREDICTIONS BY CANCER TYPE")
    print("-" * 80)
    
    pred_counts = {}
    for result in successful:
        pred_type = result['predicted']
        pred_counts[pred_type] = pred_counts.get(pred_type, 0) + 1
    
    for cancer_type, count in sorted(pred_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(successful)) * 100
        bar = "█" * int(percentage / 2)
        print(f"{cancer_type:<35} {bar} {count:3d} ({percentage:5.1f}%)")
    
    # Show confusion matrix if we have ground truth
    if has_metadata:
        with_labels = [r for r in successful if r['actual'] is not None]
        if with_labels:
            print("\n" + "-" * 80)
            print("CONFUSION MATRIX (Top Errors)")
            print("-" * 80)
            
            errors = [r for r in with_labels if not r['correct']]
            error_pairs = {}
            for r in errors:
                pair = (r['actual'], r['predicted'])
                error_pairs[pair] = error_pairs.get(pair, 0) + 1
            
            if error_pairs:
                sorted_errors = sorted(error_pairs.items(), key=lambda x: x[1], reverse=True)[:5]
                for (actual, predicted), count in sorted_errors:
                    print(f"  {actual:<30} → {predicted:<30} ({count} times)")
            else:
                print("  No errors! Perfect predictions! 🎉")
    
    # Average confidence
    avg_confidence = sum(r['confidence'] for r in successful) / len(successful)
    print(f"\n📈 Average Confidence: {avg_confidence:.2%}")
    
    # Confidence distribution
    print("\n" + "-" * 80)
    print("CONFIDENCE DISTRIBUTION")
    print("-" * 80)
    
    high_conf = len([r for r in successful if r['confidence'] > 0.85])
    med_conf = len([r for r in successful if 0.60 < r['confidence'] <= 0.85])
    low_conf = len([r for r in successful if r['confidence'] <= 0.60])
    
    print(f"High Confidence (>85%): {high_conf} ({high_conf/len(successful)*100:.1f}%)")
    print(f"Medium Confidence (60-85%): {med_conf} ({med_conf/len(successful)*100:.1f}%)")
    print(f"Low Confidence (<60%): {low_conf} ({low_conf/len(successful)*100:.1f}%)")
    
    # Risk assessment
    print("\n" + "-" * 80)
    print("RISK ASSESSMENT DISTRIBUTION")
    print("-" * 80)
    
    malignant_types = ['melanoma', 'basal_cell_carcinoma', 'actinic_keratoses']
    
    urgent = 0
    high = 0
    medium = 0
    low = 0
    
    for result in successful:
        pred_type = result['predicted'].lower()
        confidence = result['confidence']
        
        is_malignant = any(mal in pred_type for mal in malignant_types)
        
        if is_malignant and confidence > 0.85:
            urgent += 1
        elif is_malignant and confidence > 0.60:
            high += 1
        elif is_malignant and confidence > 0.40:
            medium += 1
        else:
            low += 1
    
    print(f"🚨 URGENT: {urgent} ({urgent/len(successful)*100:.1f}%)")
    print(f"⚠️  HIGH: {high} ({high/len(successful)*100:.1f}%)")
    print(f"⚡ MEDIUM: {medium} ({medium/len(successful)*100:.1f}%)")
    print(f"✓  LOW: {low} ({low/len(successful)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ Testing Complete!")
    print("=" * 80)


def main():
    """Main test function"""
    print("\n" + "=" * 80)
    print("HAM10000 MODEL ACCURACY TEST")
    print("Model: Anwarkh1/Skin_Cancer-Image_Classification (96.95% accuracy)")
    print("=" * 80)
    
    # Get number of samples from command line
    num_samples = 20
    if len(sys.argv) > 1:
        try:
            num_samples = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number: {sys.argv[1]}, using default: 20")
    
    # Load model
    print("\n📦 Loading model...")
    try:
        classifier = HuggingFaceViTClassifier()
        print("✓ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return
    
    # Get HAM10000 images
    print(f"\n🔍 Finding HAM10000 images (sample size: {num_samples})...")
    images = get_ham10000_images(num_samples)
    
    if not images:
        return
    
    print(f"✓ Found {len(images)} images to test")
    
    # Load metadata
    print("\n📋 Loading metadata...")
    metadata = load_metadata()
    has_metadata = len(metadata) > 0
    
    if has_metadata:
        print(f"✓ Metadata loaded - will calculate accuracy!")
    else:
        print("⚠️  No metadata found - will show predictions only")
    
    # Test images
    results = test_batch(classifier, images, metadata)
    
    # Analyze results
    analyze_results(results, has_metadata)
    
    if not has_metadata:
        print("\n💡 To calculate accuracy:")
        print("   Metadata file should be at: dataverse_files/HAM10000_metadata")


if __name__ == "__main__":
    main()
