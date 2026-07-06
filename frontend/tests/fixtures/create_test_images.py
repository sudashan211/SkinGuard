#!/usr/bin/env python3
"""
Script to create placeholder test images for E2E tests
Uses PIL/Pillow to create simple test images
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("Error: Pillow is not installed.")
    print("Please install it: pip install Pillow")
    exit(1)

def create_test_lesion():
    """Create a valid skin lesion test image (512x512)"""
    print("Creating test-lesion.jpg...")
    
    # Create a white background
    img = Image.new('RGB', (512, 512), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a brown circular lesion
    draw.ellipse([156, 156, 356, 356], fill='#8B4513', outline='#654321', width=3)
    draw.ellipse([226, 226, 286, 286], fill='#A0522D')
    
    # Save the image
    img.save('test-lesion.jpg', 'JPEG', quality=85)
    print("✓ Created test-lesion.jpg (512x512)")

def create_low_res_image():
    """Create a low-resolution test image (256x256)"""
    print("Creating low-res-image.jpg...")
    
    # Create a white background
    img = Image.new('RGB', (256, 256), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple circle
    draw.ellipse([78, 78, 178, 178], fill='#8B4513', outline='#654321', width=2)
    
    # Save the image
    img.save('low-res-image.jpg', 'JPEG', quality=85)
    print("✓ Created low-res-image.jpg (256x256)")

def create_melanoma_info():
    """Create an educational content image (800x600)"""
    print("Creating melanoma-info.jpg...")
    
    # Create a white background
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font_large = ImageFont.truetype("arial.ttf", 40)
        font_medium = ImageFont.truetype("arial.ttf", 20)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # Draw text
    draw.text((200, 50), "Melanoma Information", fill='black', font=font_large)
    draw.text((100, 150), "Most serious type of skin cancer", fill='black', font=font_medium)
    draw.text((100, 200), "Early detection is crucial", fill='black', font=font_medium)
    draw.text((100, 250), "ABCDE warning signs:", fill='black', font=font_medium)
    draw.text((120, 290), "A - Asymmetry", fill='black', font=font_medium)
    draw.text((120, 320), "B - Border irregularity", fill='black', font=font_medium)
    draw.text((120, 350), "C - Color variation", fill='black', font=font_medium)
    draw.text((120, 380), "D - Diameter > 6mm", fill='black', font=font_medium)
    draw.text((120, 410), "E - Evolving", fill='black', font=font_medium)
    
    # Save the image
    img.save('melanoma-info.jpg', 'JPEG', quality=85)
    print("✓ Created melanoma-info.jpg (800x600)")

def create_nsfw_note():
    """Create a note about NSFW testing"""
    print("Creating nsfw-test-note.txt...")
    
    note = """NSFW Test Image Note
====================

For testing NSFW content filtering, you have two options:

1. Use a mock/stub for the NSFW detection service in tests
2. Create a synthetic test image that triggers the NSFW detector

DO NOT commit actual inappropriate images to the repository.

For option 2, you can create a simple test image:
- Create a plain colored image
- Add metadata or markers that the NSFW detector recognizes
- Or configure your test to mock the NSFW score response

Example mock in test:
  await page.route('**/api/analyze-skin', route => {
    route.fulfill({
      status: 403,
      body: JSON.stringify({ error: 'Inappropriate content detected' })
    })
  })
"""
    
    with open('nsfw-test-note.txt', 'w') as f:
        f.write(note)
    
    print("✓ Created nsfw-test-note.txt")

def main():
    print("Creating test image fixtures...\n")
    
    # Change to the fixtures directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Create test images
    create_test_lesion()
    create_low_res_image()
    create_melanoma_info()
    create_nsfw_note()
    
    print("\n✅ Test fixtures created successfully!")
    print("\nCreated files:")
    print("  - test-lesion.jpg (512x512, valid skin lesion)")
    print("  - low-res-image.jpg (256x256, low resolution)")
    print("  - melanoma-info.jpg (800x600, educational content)")
    print("  - nsfw-test-note.txt (instructions for NSFW testing)")
    print("\nNote: For NSFW testing, please read nsfw-test-note.txt\n")

if __name__ == '__main__':
    main()
