# Image Optimization Guide for SkinGuard

This guide covers image optimization strategies to improve performance and reduce load times.

## Current Optimizations

### 1. Lazy Loading

All images use native lazy loading:

```tsx
<img 
  src={imageUrl} 
  alt="Description"
  loading="lazy"  // Native lazy loading
  className="..."
/>
```

**Benefits:**
- Images load only when they enter the viewport
- Reduces initial page load time
- Saves bandwidth for users

### 2. Responsive Images

Use `srcset` for different screen sizes:

```tsx
<img
  src="image-800w.jpg"
  srcSet="
    image-400w.jpg 400w,
    image-800w.jpg 800w,
    image-1200w.jpg 1200w
  "
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  alt="Description"
  loading="lazy"
/>
```

### 3. Modern Image Formats

Support WebP with fallback:

```tsx
<picture>
  <source srcSet="image.webp" type="image/webp" />
  <source srcSet="image.jpg" type="image/jpeg" />
  <img src="image.jpg" alt="Description" loading="lazy" />
</picture>
```

**WebP Benefits:**
- 25-35% smaller than JPEG
- Better compression
- Supports transparency

### 4. Image Component

Create a reusable optimized image component:

```tsx
// src/components/OptimizedImage.tsx
import React from 'react'

interface OptimizedImageProps {
  src: string
  alt: string
  width?: number
  height?: number
  className?: string
  priority?: boolean
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width,
  height,
  className,
  priority = false
}) => {
  // Generate WebP URL
  const webpSrc = src.replace(/\.(jpg|jpeg|png)$/i, '.webp')
  
  return (
    <picture>
      <source srcSet={webpSrc} type="image/webp" />
      <img
        src={src}
        alt={alt}
        width={width}
        height={height}
        className={className}
        loading={priority ? 'eager' : 'lazy'}
        decoding="async"
      />
    </picture>
  )
}
```

**Usage:**
```tsx
<OptimizedImage
  src="/images/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  priority={true}  // For above-the-fold images
/>
```

## Medical Image Optimization

### Upload Optimization

When users upload medical images:

```tsx
// src/utils/imageOptimization.ts
export async function optimizeImage(file: File): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    img.onload = () => {
      // Maintain aspect ratio, max 2048px
      const maxSize = 2048
      let width = img.width
      let height = img.height
      
      if (width > height && width > maxSize) {
        height = (height * maxSize) / width
        width = maxSize
      } else if (height > maxSize) {
        width = (width * maxSize) / height
        height = maxSize
      }
      
      canvas.width = width
      canvas.height = height
      
      ctx?.drawImage(img, 0, 0, width, height)
      
      canvas.toBlob(
        (blob) => {
          if (blob) resolve(blob)
          else reject(new Error('Failed to optimize image'))
        },
        'image/jpeg',
        0.85  // 85% quality
      )
    }
    
    img.onerror = reject
    img.src = URL.createObjectURL(file)
  })
}
```

**Usage in upload component:**
```tsx
const handleImageUpload = async (file: File) => {
  // Optimize before upload
  const optimizedBlob = await optimizeImage(file)
  const optimizedFile = new File([optimizedBlob], file.name, {
    type: 'image/jpeg'
  })
  
  // Upload optimized image
  await uploadImage(optimizedFile)
}
```

### Thumbnail Generation

Generate thumbnails for report history:

```tsx
export async function generateThumbnail(
  file: File,
  maxSize: number = 200
): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    img.onload = () => {
      const scale = Math.min(maxSize / img.width, maxSize / img.height)
      canvas.width = img.width * scale
      canvas.height = img.height * scale
      
      ctx?.drawImage(img, 0, 0, canvas.width, canvas.height)
      
      canvas.toBlob(
        (blob) => {
          if (blob) resolve(blob)
          else reject(new Error('Failed to generate thumbnail'))
        },
        'image/jpeg',
        0.7  // Lower quality for thumbnails
      )
    }
    
    img.onerror = reject
    img.src = URL.createObjectURL(file)
  })
}
```

## Progressive Image Loading

Show blur placeholder while loading:

```tsx
// src/components/ProgressiveImage.tsx
import React, { useState, useEffect } from 'react'

interface ProgressiveImageProps {
  src: string
  placeholder: string
  alt: string
  className?: string
}

export const ProgressiveImage: React.FC<ProgressiveImageProps> = ({
  src,
  placeholder,
  alt,
  className
}) => {
  const [imgSrc, setImgSrc] = useState(placeholder)
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    const img = new Image()
    img.src = src
    img.onload = () => {
      setImgSrc(src)
      setIsLoading(false)
    }
  }, [src])
  
  return (
    <img
      src={imgSrc}
      alt={alt}
      className={`${className} ${isLoading ? 'blur-sm' : 'blur-0'} transition-all duration-300`}
    />
  )
}
```

## Image CDN Configuration

### Supabase Storage Transformations

Use Supabase image transformations:

```tsx
// src/utils/imageUrl.ts
export function getOptimizedImageUrl(
  url: string,
  options: {
    width?: number
    height?: number
    quality?: number
    format?: 'webp' | 'jpeg' | 'png'
  } = {}
): string {
  const { width, height, quality = 80, format = 'webp' } = options
  
  // Supabase storage transformation
  const params = new URLSearchParams()
  if (width) params.append('width', width.toString())
  if (height) params.append('height', height.toString())
  params.append('quality', quality.toString())
  params.append('format', format)
  
  return `${url}?${params.toString()}`
}
```

**Usage:**
```tsx
<img
  src={getOptimizedImageUrl(imageUrl, {
    width: 800,
    quality: 85,
    format: 'webp'
  })}
  alt="Medical image"
  loading="lazy"
/>
```

## Performance Checklist

### Before Upload
- [ ] Validate image size (< 10MB)
- [ ] Check image dimensions (min 512x512)
- [ ] Optimize quality (85% JPEG)
- [ ] Generate thumbnail (200x200)
- [ ] Convert to WebP if supported

### Display Optimization
- [ ] Use lazy loading for all images
- [ ] Implement progressive loading
- [ ] Use responsive images (srcset)
- [ ] Serve WebP with fallback
- [ ] Set explicit width/height
- [ ] Use blur placeholder

### Caching
- [ ] Set cache headers (30 days)
- [ ] Use CDN for static images
- [ ] Implement service worker caching
- [ ] Cache thumbnails locally

## Tools

### Image Compression

**Online Tools:**
- [TinyPNG](https://tinypng.com/) - PNG/JPEG compression
- [Squoosh](https://squoosh.app/) - Advanced image optimization
- [ImageOptim](https://imageoptim.com/) - Mac app

**CLI Tools:**
```bash
# Install imagemagick
brew install imagemagick  # Mac
sudo apt install imagemagick  # Linux

# Convert to WebP
convert input.jpg -quality 85 output.webp

# Resize image
convert input.jpg -resize 800x600 output.jpg

# Batch convert
for img in *.jpg; do
  convert "$img" -quality 85 "${img%.jpg}.webp"
done
```

### Build-time Optimization

Add to `package.json`:
```json
{
  "scripts": {
    "optimize-images": "node scripts/optimize-images.js"
  }
}
```

Create `scripts/optimize-images.js`:
```javascript
const sharp = require('sharp')
const fs = require('fs')
const path = require('path')

const inputDir = './public/images'
const outputDir = './public/images/optimized'

fs.readdirSync(inputDir).forEach(file => {
  if (file.match(/\.(jpg|jpeg|png)$/i)) {
    const input = path.join(inputDir, file)
    const output = path.join(outputDir, file.replace(/\.(jpg|jpeg|png)$/i, '.webp'))
    
    sharp(input)
      .webp({ quality: 85 })
      .toFile(output)
      .then(() => console.log(`Optimized: ${file}`))
      .catch(err => console.error(`Error: ${file}`, err))
  }
})
```

## Monitoring

### Performance Metrics

Track image loading performance:

```tsx
// src/utils/imagePerformance.ts
export function trackImageLoad(imageUrl: string) {
  const startTime = performance.now()
  
  const img = new Image()
  img.onload = () => {
    const loadTime = performance.now() - startTime
    
    // Send to analytics
    console.log(`Image loaded in ${loadTime}ms: ${imageUrl}`)
    
    // Alert if slow
    if (loadTime > 3000) {
      console.warn(`Slow image load: ${imageUrl}`)
    }
  }
  
  img.src = imageUrl
}
```

### Lighthouse Audit

Run Lighthouse to check image optimization:

```bash
npm run lighthouse
```

Check for:
- Properly sized images
- Efficient image formats
- Lazy loading
- Image compression

## Best Practices

1. **Always use lazy loading** for below-the-fold images
2. **Optimize before upload** - don't rely on server-side optimization
3. **Use WebP** with JPEG/PNG fallback
4. **Set explicit dimensions** to prevent layout shift
5. **Compress images** to 85% quality (good balance)
6. **Generate thumbnails** for lists and previews
7. **Use CDN** for static images
8. **Cache aggressively** (30+ days)
9. **Monitor performance** with Lighthouse
10. **Test on 3G** to ensure good mobile experience

## Resources

- [Web.dev Image Optimization](https://web.dev/fast/#optimize-your-images)
- [MDN Responsive Images](https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Responsive_images)
- [WebP Documentation](https://developers.google.com/speed/webp)
- [Lighthouse Image Optimization](https://web.dev/uses-optimized-images/)

---

**Last Updated:** 2024
**Maintained By:** SkinGuard Development Team
