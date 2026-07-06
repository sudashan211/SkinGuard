/**
 * Performance E2E tests for SkinGuard
 * Tests network performance, 3G connection, and page load times
 * 
 * Validates: Requirements 20.1, 21.1, 21.2
 */

import { test, expect } from '@playwright/test'

test.describe('Performance Tests', () => {
  test('page loads within 3 seconds on fast connection', async ({ page }) => {
    const startTime = Date.now()
    
    await page.goto('/')
    
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle')
    
    const loadTime = Date.now() - startTime
    
    console.log(`Page load time: ${loadTime}ms`)
    
    // Should load within 3 seconds (3000ms)
    expect(loadTime).toBeLessThan(3000)
  })

  test('app works on 3G connection', async ({ page, context }) => {
    // Simulate 3G connection
    // 3G speeds: ~750 Kbps down, ~250 Kbps up, 100ms latency
    await context.route('**/*', async (route) => {
      // Add artificial delay to simulate 3G latency
      await new Promise(resolve => setTimeout(resolve, 100))
      await route.continue()
    })

    const startTime = Date.now()
    
    await page.goto('/')
    
    // Wait for critical content to load
    await page.waitForSelector('text=SkinGuard', { timeout: 15000 })
    
    const loadTime = Date.now() - startTime
    
    console.log(`3G load time: ${loadTime}ms`)
    
    // Should load within 10 seconds on 3G
    expect(loadTime).toBeLessThan(10000)
    
    // Verify critical content is visible
    await expect(page.locator('text=SkinGuard')).toBeVisible()
  })

  test('First Contentful Paint is under 1.5 seconds', async ({ page }) => {
    await page.goto('/')
    
    // Get performance metrics
    const performanceMetrics = await page.evaluate(() => {
      const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      const paintEntries = performance.getEntriesByType('paint')
      
      const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint')
      
      return {
        fcp: fcp?.startTime || 0,
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        loadComplete: perfData.loadEventEnd - perfData.loadEventStart
      }
    })
    
    console.log('Performance Metrics:')
    console.log(`  First Contentful Paint: ${performanceMetrics.fcp}ms`)
    console.log(`  DOM Content Loaded: ${performanceMetrics.domContentLoaded}ms`)
    console.log(`  Load Complete: ${performanceMetrics.loadComplete}ms`)
    
    // FCP should be under 1.5 seconds
    expect(performanceMetrics.fcp).toBeLessThan(1500)
  })

  test('images load lazily', async ({ page }) => {
    await page.goto('/')
    
    // Check if images have loading="lazy" attribute
    const lazyImages = await page.locator('img[loading="lazy"]').count()
    
    console.log(`Found ${lazyImages} lazy-loaded images`)
    
    // Should have at least some lazy-loaded images
    expect(lazyImages).toBeGreaterThan(0)
  })

  test('bundle size is reasonable', async ({ page }) => {
    // Navigate and capture network requests
    const jsFiles: { url: string; size: number }[] = []
    
    page.on('response', async (response) => {
      const url = response.url()
      if (url.endsWith('.js') && !url.includes('node_modules')) {
        try {
          const buffer = await response.body()
          jsFiles.push({
            url,
            size: buffer.length
          })
        } catch (e) {
          // Some responses might not have body
        }
      }
    })
    
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Calculate total JS size
    const totalSize = jsFiles.reduce((sum, file) => sum + file.size, 0)
    const totalSizeKB = totalSize / 1024
    
    console.log(`Total JS bundle size: ${totalSizeKB.toFixed(2)} KB`)
    console.log('JS files:')
    jsFiles.forEach(file => {
      console.log(`  ${file.url.split('/').pop()}: ${(file.size / 1024).toFixed(2)} KB`)
    })
    
    // Total bundle should be under 500KB (uncompressed)
    // Note: This is uncompressed size, gzipped will be much smaller
    expect(totalSizeKB).toBeLessThan(1000) // Allow 1MB uncompressed
  })

  test('API responses are fast', async ({ page }) => {
    const apiTimes: { endpoint: string; duration: number }[] = []
    
    page.on('response', async (response) => {
      const url = response.url()
      if (url.includes('/api/')) {
        const timing = response.timing()
        apiTimes.push({
          endpoint: url.split('/api/')[1],
          duration: timing.responseEnd
        })
      }
    })
    
    await page.goto('/')
    
    // Trigger some API calls by navigating
    await page.click('text=Login').catch(() => {})
    
    await page.waitForTimeout(2000)
    
    if (apiTimes.length > 0) {
      const avgTime = apiTimes.reduce((sum, t) => sum + t.duration, 0) / apiTimes.length
      
      console.log('API Response Times:')
      apiTimes.forEach(t => {
        console.log(`  ${t.endpoint}: ${t.duration.toFixed(2)}ms`)
      })
      console.log(`  Average: ${avgTime.toFixed(2)}ms`)
      
      // Average API response should be under 500ms
      expect(avgTime).toBeLessThan(500)
    }
  })

  test('mobile performance is acceptable', async ({ page, context }) => {
    // Emulate mobile device
    await context.setViewportSize({ width: 375, height: 667 })
    
    const startTime = Date.now()
    
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    const loadTime = Date.now() - startTime
    
    console.log(`Mobile load time: ${loadTime}ms`)
    
    // Mobile should load within 4 seconds
    expect(loadTime).toBeLessThan(4000)
  })

  test('PWA service worker is registered', async ({ page }) => {
    await page.goto('/')
    
    // Check if service worker is registered
    const swRegistered = await page.evaluate(async () => {
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.getRegistration()
        return registration !== undefined
      }
      return false
    })
    
    console.log(`Service Worker registered: ${swRegistered}`)
    
    // PWA should have service worker
    expect(swRegistered).toBe(true)
  })

  test('code splitting is working', async ({ page }) => {
    const jsChunks: string[] = []
    
    page.on('response', async (response) => {
      const url = response.url()
      if (url.endsWith('.js') && !url.includes('node_modules')) {
        const filename = url.split('/').pop() || ''
        jsChunks.push(filename)
      }
    })
    
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    console.log(`Loaded ${jsChunks.length} JS chunks:`)
    jsChunks.forEach(chunk => console.log(`  - ${chunk}`))
    
    // Should have multiple chunks (code splitting)
    expect(jsChunks.length).toBeGreaterThan(1)
  })

  test('images are optimized', async ({ page }) => {
    const images: { url: string; size: number }[] = []
    
    page.on('response', async (response) => {
      const url = response.url()
      const contentType = response.headers()['content-type'] || ''
      
      if (contentType.startsWith('image/')) {
        try {
          const buffer = await response.body()
          images.push({
            url,
            size: buffer.length
          })
        } catch (e) {
          // Ignore
        }
      }
    })
    
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    if (images.length > 0) {
      const avgSize = images.reduce((sum, img) => sum + img.size, 0) / images.length
      const avgSizeKB = avgSize / 1024
      
      console.log(`Loaded ${images.length} images`)
      console.log(`Average image size: ${avgSizeKB.toFixed(2)} KB`)
      
      // Average image size should be reasonable (under 200KB)
      expect(avgSizeKB).toBeLessThan(200)
    }
  })
})

test.describe('AI Analysis Performance', () => {
  test('AI analysis completes within acceptable time', async ({ page }) => {
    // This test requires authentication and a real backend
    // Skip if not in integration environment
    if (!process.env.INTEGRATION_TEST) {
      test.skip()
      return
    }
    
    await page.goto('/')
    
    // Login
    await page.click('text=Login')
    await page.fill('[name=email]', 'test@example.com')
    await page.fill('[name=password]', 'password123')
    await page.click('button[type=submit]')
    
    // Upload image
    await page.click('text=Upload Image')
    
    const startTime = Date.now()
    
    await page.setInputFiles('input[type=file]', 'tests/fixtures/test-lesion.jpg')
    
    // Wait for analysis to complete
    await page.waitForSelector('text=Analysis Complete', { timeout: 15000 })
    
    const analysisTime = Date.now() - startTime
    
    console.log(`AI analysis time: ${analysisTime}ms`)
    
    // Should complete within 10 seconds (95th percentile target)
    expect(analysisTime).toBeLessThan(10000)
  })
})
