# PWA App Icons

This directory contains the app icons for the SkinGuard PWA.

## Required Icon Sizes

The following icon sizes are required for PWA functionality:

- 72x72 - icon-72x72.png
- 96x96 - icon-96x96.png
- 128x128 - icon-128x128.png
- 144x144 - icon-144x144.png
- 152x152 - icon-152x152.png
- 192x192 - icon-192x192.png
- 384x384 - icon-384x384.png
- 512x512 - icon-512x512.png

## Icon Generation

To generate these icons from a source image:

1. Create a high-resolution source image (at least 512x512px)
2. Use an online tool like https://realfavicongenerator.net/ or https://www.pwabuilder.com/imageGenerator
3. Or use ImageMagick:

```bash
# Install ImageMagick first
# Then run:
convert source.png -resize 72x72 icon-72x72.png
convert source.png -resize 96x96 icon-96x96.png
convert source.png -resize 128x128 icon-128x128.png
convert source.png -resize 144x144 icon-144x144.png
convert source.png -resize 152x152 icon-152x152.png
convert source.png -resize 192x192 icon-192x192.png
convert source.png -resize 384x384 icon-384x384.png
convert source.png -resize 512x512 icon-512x512.png
```

## Design Guidelines

- Use a simple, recognizable design
- Ensure the icon works well at small sizes
- Use the brand colors (primary: #2563eb)
- Consider using a medical/health-related symbol
- Make sure the icon is clear on both light and dark backgrounds

## Shortcut Icons

Additional icons for PWA shortcuts:

- upload-icon.png (96x96) - For "Upload Image" shortcut
- doctor-icon.png (96x96) - For "Find Doctor" shortcut
- history-icon.png (96x96) - For "Report History" shortcut

## Screenshots

For app store listings and PWA install prompts:

- screenshot-1.png (540x720) - Main dashboard view
- screenshot-2.png (540x720) - Analysis results view

## Note

Currently, placeholder icons need to be created. The manifest.json is configured to use these icons once they are generated.
