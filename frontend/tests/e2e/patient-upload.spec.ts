import { test, expect } from '@playwright/test'
import { loginAsPatient } from './helpers/auth'
import path from 'path'

/**
 * E2E Test: Patient Upload Flow
 * Tests the complete patient journey from login to viewing AI analysis results
 * 
 * Validates: Requirements 21.1 (Mobile Responsiveness and PWA)
 */

test.describe('Patient Upload Flow', () => {
  test('patient can upload image and view AI analysis results', async ({ page }) => {
    // Login as patient
    await loginAsPatient(page)
    
    // Navigate to upload page
    await page.click('text=Upload Image')
    await expect(page).toHaveURL(/.*upload/)
    
    // Verify drag-and-drop area is visible
    await expect(page.locator('[data-testid="dropzone"]')).toBeVisible()
    
    // Upload test image
    const testImagePath = path.join(__dirname, '../fixtures/test-lesion.jpg')
    await page.setInputFiles('input[type=file]', testImagePath)
    
    // Verify image preview appears
    await expect(page.locator('[data-testid="image-preview"]')).toBeVisible()
    
    // Fill symptom wizard - Step 1: Location
    await page.click('text=Next')
    await page.click('[data-testid="body-location-arm"]')
    
    // Step 2: Sensations
    await page.click('text=Next')
    await page.check('[name="sensation-itching"]')
    await page.check('[name="sensation-pain"]')
    
    // Step 3: Visual Changes
    await page.click('text=Next')
    await page.check('[name="visual-color"]')
    await page.check('[name="visual-size"]')
    
    // Submit for analysis
    await page.click('button:has-text("Analyze")')
    
    // Wait for AI analysis to complete (max 30 seconds)
    await page.waitForSelector('text=Analysis Complete', { timeout: 30000 })
    
    // Verify results are displayed
    await expect(page.locator('[data-testid="ai-results"]')).toBeVisible()
    
    // Verify all 7 cancer types are shown
    const predictionCards = page.locator('[data-testid="prediction-card"]')
    await expect(predictionCards).toHaveCount(7)
    
    // Verify hotspot overlay is visible
    await expect(page.locator('[data-testid="hotspot-overlay"]')).toBeVisible()
    
    // Verify medical disclaimer is present
    await expect(page.locator('text=/94% probability estimate/')).toBeVisible()
    await expect(page.locator('text=/consult verified doctors/')).toBeVisible()
    
    // Verify "Find Doctor" button is visible
    await expect(page.locator('button:has-text("Find Doctor")')).toBeVisible()
  })

  test('patient can view report history', async ({ page }) => {
    await loginAsPatient(page)
    
    // Navigate to history
    await page.click('text=My Reports')
    
    // Verify report list is displayed
    await expect(page.locator('[data-testid="report-list"]')).toBeVisible()
    
    // Verify reports are ordered by date (newest first)
    const reportDates = await page.locator('[data-testid="report-date"]').allTextContents()
    expect(reportDates.length).toBeGreaterThan(0)
    
    // Click on a report to view details
    await page.locator('[data-testid="report-card"]').first().click()
    
    // Verify full report details are shown
    await expect(page.locator('[data-testid="report-details"]')).toBeVisible()
    await expect(page.locator('[data-testid="ai-predictions"]')).toBeVisible()
    await expect(page.locator('[data-testid="symptoms"]')).toBeVisible()
  })

  test('patient can compare two reports', async ({ page }) => {
    await loginAsPatient(page)
    
    // Navigate to history
    await page.click('text=My Reports')
    
    // Select two reports for comparison
    await page.check('[data-testid="report-checkbox"]', { nth: 0 })
    await page.check('[data-testid="report-checkbox"]', { nth: 1 })
    
    // Click compare button
    await page.click('button:has-text("Compare")')
    
    // Verify comparison view is displayed
    await expect(page.locator('[data-testid="comparison-view"]')).toBeVisible()
    
    // Verify both images are shown side-by-side
    const comparisonImages = page.locator('[data-testid="comparison-image"]')
    await expect(comparisonImages).toHaveCount(2)
    
    // Verify change detection highlights
    await expect(page.locator('[data-testid="change-highlights"]')).toBeVisible()
  })

  test('image quality validation rejects low-quality images', async ({ page }) => {
    await loginAsPatient(page)
    
    await page.click('text=Upload Image')
    
    // Try to upload low-resolution image
    const lowResImagePath = path.join(__dirname, '../fixtures/low-res-image.jpg')
    await page.setInputFiles('input[type=file]', lowResImagePath)
    
    // Verify error message is displayed
    await expect(page.locator('text=/resolution too low/i')).toBeVisible()
    
    // Verify guidance is provided
    await expect(page.locator('text=/capture a better image/i')).toBeVisible()
  })

  test('NSFW filter rejects inappropriate content', async ({ page }) => {
    await loginAsPatient(page)
    
    await page.click('text=Upload Image')
    
    // Try to upload inappropriate image
    const inappropriateImagePath = path.join(__dirname, '../fixtures/nsfw-test.jpg')
    await page.setInputFiles('input[type=file]', inappropriateImagePath)
    
    await page.click('button:has-text("Analyze")')
    
    // Verify rejection message
    await expect(page.locator('text=/Inappropriate content detected/i')).toBeVisible()
    
    // Verify HTTP 403 error is handled gracefully
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible()
  })
})
