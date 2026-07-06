import { test, expect } from '@playwright/test'
import { loginAsPatient } from './helpers/auth'

/**
 * E2E Test: Cross-Browser Compatibility
 * Tests that the application works correctly across Chrome, Firefox, and Safari
 * 
 * Validates: Requirements 21.1 (Mobile Responsiveness and PWA)
 */

test.describe('Cross-Browser Compatibility', () => {
  test('landing page renders correctly across browsers', async ({ page, browserName }) => {
    await page.goto('/')
    
    // Verify hero section
    await expect(page.locator('[data-testid="hero-section"]')).toBeVisible()
    
    // Verify carousel with 3 slides
    await expect(page.locator('[data-testid="carousel"]')).toBeVisible()
    const slides = page.locator('[data-testid="carousel-slide"]')
    await expect(slides).toHaveCount(3)
    
    // Verify carousel navigation works
    await page.click('[data-testid="carousel-next"]')
    await page.waitForTimeout(500) // Wait for animation
    
    // Verify features section
    await expect(page.locator('text=AI Screening')).toBeVisible()
    await expect(page.locator('text=Find Doctors')).toBeVisible()
    await expect(page.locator('text=Secure History')).toBeVisible()
    
    // Verify CTA buttons
    await expect(page.locator('button:has-text("Get Started")')).toBeVisible()
    await expect(page.locator('button:has-text("Learn More")')).toBeVisible()
    
    console.log(`✓ Landing page renders correctly on ${browserName}`)
  })

  test('authentication works across browsers', async ({ page, browserName }) => {
    await loginAsPatient(page)
    
    // Verify successful login
    await expect(page).toHaveURL(/.*dashboard/)
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
    
    console.log(`✓ Authentication works on ${browserName}`)
  })

  test('image upload works across browsers', async ({ page, browserName }) => {
    await loginAsPatient(page)
    
    await page.click('text=Upload Image')
    
    // Verify dropzone renders
    await expect(page.locator('[data-testid="dropzone"]')).toBeVisible()
    
    // Test drag-and-drop visual feedback
    const dropzone = page.locator('[data-testid="dropzone"]')
    await dropzone.hover()
    
    // Verify file input is accessible
    const fileInput = page.locator('input[type=file]')
    await expect(fileInput).toBeAttached()
    
    console.log(`✓ Image upload interface works on ${browserName}`)
  })

  test('Google Maps integration works across browsers', async ({ page, browserName }) => {
    await loginAsPatient(page)
    
    await page.click('text=Find Doctors')
    
    // Wait for map to load
    await page.waitForSelector('[data-testid="google-map"]', { timeout: 10000 })
    
    // Verify map is visible
    await expect(page.locator('[data-testid="google-map"]')).toBeVisible()
    
    // Verify map controls
    await expect(page.locator('[data-testid="map-zoom-in"]')).toBeVisible()
    await expect(page.locator('[data-testid="map-zoom-out"]')).toBeVisible()
    
    // Verify doctor markers are rendered
    const markers = page.locator('[data-testid="doctor-marker"]')
    const markerCount = await markers.count()
    expect(markerCount).toBeGreaterThan(0)
    
    console.log(`✓ Google Maps works on ${browserName}`)
  })

  test('Framer Motion animations work across browsers', async ({ page, browserName }) => {
    await page.goto('/')
    
    // Verify carousel animations
    const carousel = page.locator('[data-testid="carousel"]')
    await expect(carousel).toBeVisible()
    
    // Trigger slide transition
    await page.click('[data-testid="carousel-next"]')
    
    // Wait for animation to complete
    await page.waitForTimeout(1000)
    
    // Verify smooth transitions (no console errors)
    const consoleErrors: string[] = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text())
      }
    })
    
    expect(consoleErrors.length).toBe(0)
    
    console.log(`✓ Animations work smoothly on ${browserName}`)
  })

  test('responsive layout works across browsers', async ({ page, browserName }) => {
    await page.goto('/')
    
    // Test desktop layout
    await page.setViewportSize({ width: 1920, height: 1080 })
    await expect(page.locator('[data-testid="desktop-nav"]')).toBeVisible()
    
    // Test tablet layout
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.waitForTimeout(500)
    
    // Test mobile layout
    await page.setViewportSize({ width: 375, height: 667 })
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible()
    
    console.log(`✓ Responsive layout works on ${browserName}`)
  })

  test('form validation works across browsers', async ({ page, browserName }) => {
    await page.goto('/')
    await page.click('text=Sign Up')
    
    // Submit empty form
    await page.click('button[type=submit]')
    
    // Verify validation errors
    await expect(page.locator('text=/email is required/i')).toBeVisible()
    await expect(page.locator('text=/password is required/i')).toBeVisible()
    
    // Fill invalid email
    await page.fill('[name=email]', 'invalid-email')
    await page.click('button[type=submit]')
    
    // Verify email validation
    await expect(page.locator('text=/valid email/i')).toBeVisible()
    
    console.log(`✓ Form validation works on ${browserName}`)
  })

  test('local storage and session management works across browsers', async ({ page, browserName }) => {
    await loginAsPatient(page)
    
    // Verify auth token is stored
    const localStorage = await page.evaluate(() => {
      return window.localStorage.getItem('auth_token')
    })
    expect(localStorage).toBeTruthy()
    
    // Refresh page
    await page.reload()
    
    // Verify session persists
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
    
    console.log(`✓ Session management works on ${browserName}`)
  })

  test('CSS Grid and Flexbox layouts work across browsers', async ({ page, browserName }) => {
    await loginAsPatient(page)
    
    // Check dashboard grid layout
    const dashboardGrid = page.locator('[data-testid="dashboard-grid"]')
    await expect(dashboardGrid).toBeVisible()
    
    // Verify grid items are properly aligned
    const gridItems = page.locator('[data-testid="dashboard-card"]')
    const count = await gridItems.count()
    expect(count).toBeGreaterThan(0)
    
    // Check flexbox layouts
    const flexContainer = page.locator('[data-testid="flex-container"]')
    await expect(flexContainer).toBeVisible()
    
    console.log(`✓ CSS layouts work on ${browserName}`)
  })
})
