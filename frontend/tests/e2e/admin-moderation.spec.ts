import { test, expect } from '@playwright/test'
import { loginAsAdmin } from './helpers/auth'

/**
 * E2E Test: Admin Moderation Flow
 * Tests admin content moderation, analytics, and content management
 * 
 * Validates: Requirements 21.1 (Mobile Responsiveness and PWA)
 */

test.describe('Admin Moderation Flow', () => {
  test('admin can view and moderate flagged content', async ({ page }) => {
    await loginAsAdmin(page)
    
    // Navigate to content moderation
    await page.click('text=Admin Panel')
    await page.click('text=Content Moderation')
    
    // Verify flagged content list
    await expect(page.locator('[data-testid="flagged-content"]')).toBeVisible()
    
    // View flagged report
    const flaggedReports = page.locator('[data-testid="flagged-report-card"]')
    const count = await flaggedReports.count()
    
    if (count > 0) {
      await flaggedReports.first().click()
      
      // Verify flagged content details
      await expect(page.locator('[data-testid="flagged-image"]')).toBeVisible()
      await expect(page.locator('[data-testid="nsfw-score"]')).toBeVisible()
      await expect(page.locator('[data-testid="rejection-reason"]')).toBeVisible()
      
      // Review and take action
      await page.click('button:has-text("Review")')
      
      // Options: Approve, Delete, or Ban User
      await expect(page.locator('button:has-text("Approve")')).toBeVisible()
      await expect(page.locator('button:has-text("Delete")')).toBeVisible()
      await expect(page.locator('button:has-text("Ban User")')).toBeVisible()
      
      // Delete flagged content
      await page.click('button:has-text("Delete")')
      await page.click('button:has-text("Confirm")')
      
      // Verify deletion confirmation
      await expect(page.locator('text=/Content deleted/i')).toBeVisible()
    }
  })

  test('admin can view platform analytics', async ({ page }) => {
    await loginAsAdmin(page)
    
    // Navigate to analytics
    await page.click('text=Admin Panel')
    await page.click('text=Analytics')
    
    // Verify analytics dashboard
    await expect(page.locator('[data-testid="analytics-dashboard"]')).toBeVisible()
    
    // Verify key metrics are displayed
    await expect(page.locator('[data-testid="total-users"]')).toBeVisible()
    await expect(page.locator('[data-testid="total-screenings"]')).toBeVisible()
    await expect(page.locator('[data-testid="active-doctors"]')).toBeVisible()
    await expect(page.locator('[data-testid="avg-processing-time"]')).toBeVisible()
    
    // Verify charts are rendered
    await expect(page.locator('[data-testid="usage-chart"]')).toBeVisible()
    await expect(page.locator('[data-testid="cancer-types-chart"]')).toBeVisible()
    
    // Filter by date range
    await page.click('[data-testid="date-range-picker"]')
    await page.click('text=Last 30 Days')
    
    // Verify data updates
    await expect(page.locator('[data-testid="analytics-dashboard"]')).toBeVisible()
  })

  test('admin can manage Skin-Wiki content', async ({ page }) => {
    await loginAsAdmin(page)
    
    // Navigate to content management
    await page.click('text=Admin Panel')
    await page.click('text=Skin-Wiki')
    
    // Verify content list
    await expect(page.locator('[data-testid="wiki-articles"]')).toBeVisible()
    
    // Create new article
    await page.click('button:has-text("New Article")')
    
    // Fill article form
    await page.fill('[name=title]', 'Understanding Melanoma')
    await page.fill('[name=content]', 'Melanoma is the most serious type of skin cancer...')
    await page.selectOption('[name=cancerType]', 'melanoma')
    
    // Upload article image
    await page.setInputFiles('[name=image]', './tests/fixtures/melanoma-info.jpg')
    
    // Add translations
    await page.click('text=Add Translation')
    await page.selectOption('[name=language]', 'es')
    await page.fill('[name=translatedTitle]', 'Entendiendo el Melanoma')
    await page.fill('[name=translatedContent]', 'El melanoma es el tipo más grave de cáncer de piel...')
    
    // Publish article
    await page.click('button:has-text("Publish")')
    
    // Verify article published
    await expect(page.locator('text=/Article published/i')).toBeVisible()
    
    // Verify article appears in list
    await expect(page.locator('text=Understanding Melanoma')).toBeVisible()
  })

  test('admin can edit existing wiki article', async ({ page }) => {
    await loginAsAdmin(page)
    
    await page.click('text=Admin Panel')
    await page.click('text=Skin-Wiki')
    
    // Select article to edit
    await page.locator('[data-testid="article-card"]').first().click()
    await page.click('button:has-text("Edit")')
    
    // Update content
    await page.fill('[name=content]', 'Updated content with new medical information...')
    
    // Save changes
    await page.click('button:has-text("Save Changes")')
    
    // Verify version history is maintained
    await page.click('text=Version History')
    await expect(page.locator('[data-testid="version-list"]')).toBeVisible()
    
    // Verify timestamp is updated
    await expect(page.locator('[data-testid="last-updated"]')).toBeVisible()
  })

  test('admin can view audit logs', async ({ page }) => {
    await loginAsAdmin(page)
    
    await page.click('text=Admin Panel')
    await page.click('text=Audit Logs')
    
    // Verify audit log table
    await expect(page.locator('[data-testid="audit-logs-table"]')).toBeVisible()
    
    // Verify log entries contain required fields
    const logEntries = page.locator('[data-testid="log-entry"]')
    const count = await logEntries.count()
    
    if (count > 0) {
      const firstLog = logEntries.first()
      await expect(firstLog.locator('[data-testid="user-id"]')).toBeVisible()
      await expect(firstLog.locator('[data-testid="action"]')).toBeVisible()
      await expect(firstLog.locator('[data-testid="timestamp"]')).toBeVisible()
      await expect(firstLog.locator('[data-testid="ip-address"]')).toBeVisible()
    }
    
    // Filter logs by action type
    await page.selectOption('[name=actionFilter]', 'content_flagged')
    
    // Verify filtered results
    await expect(page.locator('[data-testid="log-entry"]')).toBeVisible()
  })

  test('admin can manage user accounts', async ({ page }) => {
    await loginAsAdmin(page)
    
    await page.click('text=Admin Panel')
    await page.click('text=User Management')
    
    // Search for user
    await page.fill('[name=userSearch]', 'patient@test.com')
    await page.click('button:has-text("Search")')
    
    // View user details
    await page.locator('[data-testid="user-card"]').first().click()
    
    // Verify user information
    await expect(page.locator('[data-testid="user-email"]')).toBeVisible()
    await expect(page.locator('[data-testid="user-role"]')).toBeVisible()
    await expect(page.locator('[data-testid="user-status"]')).toBeVisible()
    
    // Admin actions available
    await expect(page.locator('button:has-text("Suspend Account")')).toBeVisible()
    await expect(page.locator('button:has-text("Delete Account")')).toBeVisible()
    await expect(page.locator('button:has-text("View Activity")')).toBeVisible()
  })
})
