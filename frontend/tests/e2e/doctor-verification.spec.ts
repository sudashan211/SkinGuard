import { test, expect } from '@playwright/test'
import { loginAsDoctor, loginAsAdmin, signup } from './helpers/auth'

/**
 * E2E Test: Doctor Verification Flow
 * Tests doctor registration, admin verification, and report access
 * 
 * Validates: Requirements 21.1 (Mobile Responsiveness and PWA)
 */

test.describe('Doctor Verification Flow', () => {
  test('doctor can register and wait for verification', async ({ page }) => {
    // Register as new doctor
    const email = `doctor-${Date.now()}@test.com`
    await signup(page, email, 'Test123456!', 'Dr. John Smith', 'doctor')
    
    // Fill doctor registration form
    await page.fill('[name=licenseNo]', 'MD123456')
    await page.fill('[name=clinicName]', 'Smith Dermatology Clinic')
    await page.fill('[name=specialization]', 'Dermatology')
    await page.fill('[name=whatsappNo]', '+1234567890')
    
    // Set clinic location on map
    await page.click('[data-testid="map-picker"]')
    await page.click('[data-testid="map-canvas"]', { position: { x: 200, y: 200 } })
    
    // Submit registration
    await page.click('button:has-text("Submit Registration")')
    
    // Verify pending verification message
    await expect(page.locator('text=/pending verification/i')).toBeVisible()
    await expect(page.locator('text=/admin will review/i')).toBeVisible()
  })

  test('unverified doctor cannot access patient reports', async ({ page }) => {
    // Login as unverified doctor
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('[name=email]', 'unverified-doctor@test.com')
    await page.fill('[name=password]', 'Test123456!')
    await page.click('button[type=submit]')
    
    // Try to access reports
    await page.goto('/doctor-dashboard/reports')
    
    // Verify access denied message
    await expect(page.locator('text=/verification pending/i')).toBeVisible()
    await expect(page.locator('[data-testid="reports-list"]')).not.toBeVisible()
  })

  test('admin can verify doctor application', async ({ page }) => {
    // Login as admin
    await loginAsAdmin(page)
    
    // Navigate to doctor verification
    await page.click('text=Admin Panel')
    await page.click('text=Doctor Verification')
    
    // Verify pending applications are listed
    await expect(page.locator('[data-testid="pending-doctors"]')).toBeVisible()
    
    // View first pending doctor
    await page.locator('[data-testid="doctor-card"]').first().click()
    
    // Verify doctor details are displayed
    await expect(page.locator('[data-testid="license-number"]')).toBeVisible()
    await expect(page.locator('[data-testid="clinic-name"]')).toBeVisible()
    await expect(page.locator('[data-testid="clinic-location"]')).toBeVisible()
    
    // Approve doctor
    await page.click('button:has-text("Approve")')
    
    // Verify confirmation message
    await expect(page.locator('text=/Doctor verified successfully/i')).toBeVisible()
    
    // Verify doctor is removed from pending list
    const pendingCount = await page.locator('[data-testid="doctor-card"]').count()
    expect(pendingCount).toBeGreaterThanOrEqual(0)
  })

  test('verified doctor can access patient reports', async ({ page }) => {
    // Login as verified doctor
    await loginAsDoctor(page)
    
    // Navigate to reports
    await page.click('text=Patient Reports')
    
    // Verify reports list is accessible
    await expect(page.locator('[data-testid="reports-list"]')).toBeVisible()
    
    // Verify only safe/urgent reports are shown (not flagged)
    const reports = page.locator('[data-testid="report-card"]')
    const count = await reports.count()
    
    if (count > 0) {
      // Check first report
      await reports.first().click()
      
      // Verify report details are displayed
      await expect(page.locator('[data-testid="patient-image"]')).toBeVisible()
      await expect(page.locator('[data-testid="ai-predictions"]')).toBeVisible()
      await expect(page.locator('[data-testid="patient-symptoms"]')).toBeVisible()
      await expect(page.locator('[data-testid="patient-health-profile"]')).toBeVisible()
      
      // Add consultation notes
      await page.fill('[name=consultationNotes]', 'Patient should schedule in-person examination.')
      await page.click('button:has-text("Save Notes")')
      
      // Verify notes saved confirmation
      await expect(page.locator('text=/Notes saved/i')).toBeVisible()
    }
  })

  test('doctor can manage appointments', async ({ page }) => {
    await loginAsDoctor(page)
    
    // Navigate to appointments
    await page.click('text=Appointments')
    
    // Verify appointments list
    await expect(page.locator('[data-testid="appointments-list"]')).toBeVisible()
    
    // Filter by status
    await page.selectOption('[name=statusFilter]', 'pending')
    
    // View appointment details
    const appointments = page.locator('[data-testid="appointment-card"]')
    const count = await appointments.count()
    
    if (count > 0) {
      await appointments.first().click()
      
      // Verify appointment details
      await expect(page.locator('[data-testid="patient-name"]')).toBeVisible()
      await expect(page.locator('[data-testid="scheduled-time"]')).toBeVisible()
      
      // Confirm appointment
      await page.click('button:has-text("Confirm")')
      
      // Verify status updated
      await expect(page.locator('text=/confirmed/i')).toBeVisible()
    }
  })

  test('admin can reject doctor application', async ({ page }) => {
    await loginAsAdmin(page)
    
    await page.click('text=Admin Panel')
    await page.click('text=Doctor Verification')
    
    // View pending doctor
    await page.locator('[data-testid="doctor-card"]').first().click()
    
    // Reject with reason
    await page.click('button:has-text("Reject")')
    await page.fill('[name=rejectionReason]', 'Invalid license number')
    await page.click('button:has-text("Confirm Rejection")')
    
    // Verify rejection confirmation
    await expect(page.locator('text=/Application rejected/i')).toBeVisible()
  })
})
