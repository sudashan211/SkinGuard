import { test, expect, devices } from '@playwright/test'
import { loginAsPatient } from './helpers/auth'

/**
 * E2E Test: Mobile Responsiveness
 * Tests mobile-specific features including camera integration, touch gestures, and PWA functionality
 * 
 * Validates: Requirements 21.1 (Mobile Responsiveness and PWA)
 */

test.describe('Mobile Responsiveness', () => {
  test.use({ ...devices['iPhone 12'] })

  test('mobile navigation menu works correctly', async ({ page }) => {
    await page.goto('/')
    
    // Verify mobile menu button is visible
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible()
    
    // Open mobile menu
    await page.click('[data-testid="mobile-menu-button"]')
    
    // Verify menu items
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible()
    await expect(page.locator('text=Home')).toBeVisible()
    await expect(page.locator('text=Features')).toBeVisible()
    await expect(page.locator('text=About')).toBeVisible()
    await expect(page.locator('text=Login')).toBeVisible()
    
    // Close menu
    await page.click('[data-testid="mobile-menu-close"]')
    await expect(page.locator('[data-testid="mobile-menu"]')).not.toBeVisible()
  })

  test('mobile camera integration for image upload', async ({ page }) => {
    await loginAsPatient(page)
    
    await page.click('text=Upload Image')
    
    // Verify camera capture option is available on mobile
    const fileInput = page.locator('input[type=file]')
    const acceptAttr = await fileInput.getAttribute('accept')
    
    // Mobile should allow camera capture
    expect(acceptAttr).toContain('image/*')
    
    // Verify capture attribute for direct camera access
    const captureAttr = await fileInput.getAttribute('capture')
    expect(captureAttr).toBeTruthy()
  })

  test('touch gestures for image zoom and pan', async ({ page }) => {
    await loginAsPatient(page)
    
    // Navigate to a report with an image
    await page.click('text=My Reports')
    await page.locator('[data-testid="report-card"]').first().click()
    
    // Verify image is displayed
    const image = page.locator('[data-testid="report-image"]')
    await expect(image).toBeVisible()
    
    // Test pinch-to-zoom (simulated)
    await image.tap()
    await image.tap({ clickCount: 2 }) // Double tap to zoom
    
    // Verify zoom controls are available
    await expect(page.locator('[data-testid="zoom-controls"]')).toBeVisible()
    
    // Test pan gesture
    await image.dragTo(image, {
      sourcePosition: { x: 100, y: 100 },
      targetPosition: { x: 200, y: 200 }
    })
  })

  test('mobile-optimized forms and inputs', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Sign Up')
    
    // Verify input types are mobile-optimized
    const emailInput = page.locator('[name=email]')
    const emailType = await emailInput.getAttribute('type')
    expect(emailType).toBe('email') // Triggers email keyboard on mobile
    
    // Verify password input
    const passwordInput = page.locator('[name=password]')
    const passwordType = await passwordInput.getAttribute('type')
    expect(passwordType).toBe('password')
    
    // Verify inputs are properly sized for mobile
    const emailBox = await emailInput.boundingBox()
    expect(emailBox?.height).toBeGreaterThan(40) // Minimum touch target size
  })

  test('mobile GPS integration for doctor locator', async ({ page, context }) => {
    // Grant geolocation permission
    await context.grantPermissions(['geolocation'])
    await context.setGeolocation({ latitude: 40.7128, longitude: -74.0060 })
    
    await loginAsPatient(page)
    
    await page.click('text=Find Doctors')
    
    // Verify "Use My Location" button
    await expect(page.locator('button:has-text("Use My Location")')).toBeVisible()
    
    // Click to center map on user location
    await page.click('button:has-text("Use My Location")')
    
    // Wait for map to center
    await page.waitForTimeout(1000)
    
    // Verify map is centered on user location
    await expect(page.locator('[data-testid="user-location-marker"]')).toBeVisible()
  })

  test('mobile-friendly doctor cards and contact buttons', async ({ page }) => {
    await loginAsPatient(page)
    
    await page.click('text=Find Doctors')
    
    // Wait for doctors to load
    await page.waitForSelector('[data-testid="doctor-card"]')
    
    // Verify doctor cards are mobile-optimized
    const doctorCard = page.locator('[data-testid="doctor-card"]').first()
    await expect(doctorCard).toBeVisible()
    
    // Verify WhatsApp button is prominent
    const whatsappButton = doctorCard.locator('button:has-text("WhatsApp")')
    await expect(whatsappButton).toBeVisible()
    
    // Verify button is large enough for touch
    const buttonBox = await whatsappButton.boundingBox()
    expect(buttonBox?.height).toBeGreaterThan(40)
  })

  test('mobile swipe gestures for carousel', async ({ page }) => {
    await page.goto('/')
    
    const carousel = page.locator('[data-testid="carousel"]')
    await expect(carousel).toBeVisible()
    
    // Get initial slide
    const initialSlide = await page.locator('[data-testid="carousel-slide"].active').textContent()
    
    // Swipe left to next slide
    await carousel.swipe({ direction: 'left' })
    await page.waitForTimeout(500)
    
    // Verify slide changed
    const newSlide = await page.locator('[data-testid="carousel-slide"].active').textContent()
    expect(newSlide).not.toBe(initialSlide)
  })

  test('mobile viewport scaling and zoom prevention', async ({ page }) => {
    await page.goto('/')
    
    // Verify viewport meta tag prevents unwanted zoom
    const viewportMeta = await page.locator('meta[name="viewport"]').getAttribute('content')
    expect(viewportMeta).toContain('width=device-width')
    expect(viewportMeta).toContain('initial-scale=1')
  })

  test('mobile-optimized symptom wizard', async ({ page }) => {
    await loginAsPatient(page)
    
    await page.click('text=Upload Image')
    
    // Upload test image
    await page.setInputFiles('input[type=file]', './tests/fixtures/test-lesion.jpg')
    
    // Navigate through symptom wizard
    await page.click('text=Next')
    
    // Verify body location selector is mobile-friendly
    await expect(page.locator('[data-testid="body-diagram"]')).toBeVisible()
    
    // Tap on body location
    await page.locator('[data-testid="body-location-arm"]').tap()
    
    // Verify selection feedback
    await expect(page.locator('[data-testid="body-location-arm"].selected')).toBeVisible()
    
    // Continue to next step
    await page.click('text=Next')
    
    // Verify checkboxes are large enough for touch
    const checkbox = page.locator('[name="sensation-itching"]')
    const checkboxBox = await checkbox.boundingBox()
    expect(checkboxBox?.height).toBeGreaterThan(40)
  })

  test('mobile bottom navigation bar', async ({ page }) => {
    await loginAsPatient(page)
    
    // Verify bottom nav is visible on mobile
    await expect(page.locator('[data-testid="bottom-nav"]')).toBeVisible()
    
    // Verify nav items
    await expect(page.locator('[data-testid="nav-home"]')).toBeVisible()
    await expect(page.locator('[data-testid="nav-upload"]')).toBeVisible()
    await expect(page.locator('[data-testid="nav-reports"]')).toBeVisible()
    await expect(page.locator('[data-testid="nav-doctors"]')).toBeVisible()
    await expect(page.locator('[data-testid="nav-profile"]')).toBeVisible()
    
    // Test navigation
    await page.click('[data-testid="nav-reports"]')
    await expect(page).toHaveURL(/.*reports/)
  })

  test('mobile pull-to-refresh functionality', async ({ page }) => {
    await loginAsPatient(page)
    
    await page.click('text=My Reports')
    
    // Simulate pull-to-refresh gesture
    await page.touchscreen.tap(100, 100)
    await page.touchscreen.move(100, 300)
    
    // Verify refresh indicator appears
    await expect(page.locator('[data-testid="refresh-indicator"]')).toBeVisible()
    
    // Wait for refresh to complete
    await page.waitForTimeout(1000)
  })

  test('mobile landscape orientation support', async ({ page }) => {
    await page.goto('/')
    
    // Switch to landscape
    await page.setViewportSize({ width: 812, height: 375 })
    
    // Verify layout adapts to landscape
    await expect(page.locator('[data-testid="hero-section"]')).toBeVisible()
    
    // Verify navigation is still accessible
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible()
  })
})

test.describe('Progressive Web App (PWA)', () => {
  test('PWA manifest is properly configured', async ({ page }) => {
    await page.goto('/')
    
    // Verify manifest link
    const manifestLink = page.locator('link[rel="manifest"]')
    await expect(manifestLink).toBeAttached()
    
    // Fetch and verify manifest content
    const manifestHref = await manifestLink.getAttribute('href')
    const manifestResponse = await page.goto(manifestHref!)
    expect(manifestResponse?.status()).toBe(200)
    
    const manifest = await manifestResponse?.json()
    expect(manifest.name).toBeTruthy()
    expect(manifest.short_name).toBeTruthy()
    expect(manifest.icons).toBeTruthy()
    expect(manifest.start_url).toBeTruthy()
    expect(manifest.display).toBe('standalone')
  })

  test('service worker is registered', async ({ page }) => {
    await page.goto('/')
    
    // Wait for service worker registration
    await page.waitForTimeout(2000)
    
    // Check if service worker is registered
    const swRegistered = await page.evaluate(() => {
      return navigator.serviceWorker.getRegistration().then(reg => !!reg)
    })
    
    expect(swRegistered).toBe(true)
  })

  test('offline functionality for viewing reports', async ({ page, context }) => {
    await loginAsPatient(page)
    
    // Navigate to reports and wait for data to load
    await page.click('text=My Reports')
    await page.waitForSelector('[data-testid="report-card"]')
    
    // Go offline
    await context.setOffline(true)
    
    // Refresh page
    await page.reload()
    
    // Verify cached reports are still accessible
    await expect(page.locator('[data-testid="report-list"]')).toBeVisible()
    await expect(page.locator('[data-testid="offline-indicator"]')).toBeVisible()
    
    // Go back online
    await context.setOffline(false)
  })

  test('install prompt appears on mobile', async ({ page }) => {
    await page.goto('/')
    
    // Simulate beforeinstallprompt event
    await page.evaluate(() => {
      const event = new Event('beforeinstallprompt')
      window.dispatchEvent(event)
    })
    
    // Verify install banner appears
    await expect(page.locator('[data-testid="install-banner"]')).toBeVisible()
    await expect(page.locator('button:has-text("Install App")')).toBeVisible()
  })
})
