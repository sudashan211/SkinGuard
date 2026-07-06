import { test, expect } from '@playwright/test'
import { signup, logout } from './helpers/auth'

/**
 * E2E Test: Authentication and Authorization
 * Tests login, signup, logout, and role-based access control
 * 
 * Validates: Requirements 21.1 (Mobile Responsiveness and PWA)
 */

test.describe('Authentication Flow', () => {
  test('user can sign up as patient', async ({ page }) => {
    const email = `patient-${Date.now()}@test.com`
    await signup(page, email, 'Test123456!', 'John Doe', 'patient')
    
    // Verify redirect to patient onboarding
    await expect(page).toHaveURL(/.*onboarding/)
    
    // Complete patient profile
    await page.fill('[name=age]', '35')
    await page.selectOption('[name=skinType]', 'III')
    await page.fill('[name=familyHistory]', 'No family history of skin cancer')
    await page.click('button:has-text("Complete Profile")')
    
    // Verify redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/)
    await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible()
  })

  test('user can sign up as doctor', async ({ page }) => {
    const email = `doctor-${Date.now()}@test.com`
    await signup(page, email, 'Test123456!', 'Dr. Jane Smith', 'doctor')
    
    // Verify redirect to doctor registration
    await expect(page).toHaveURL(/.*doctor-registration/)
    
    // Verify pending verification message
    await expect(page.locator('text=/verification pending/i')).toBeVisible()
  })

  test('user can login with valid credentials', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Login')
    
    // Fill login form
    await page.fill('[name=email]', 'patient@test.com')
    await page.fill('[name=password]', 'Test123456!')
    await page.click('button[type=submit]')
    
    // Verify successful login
    await expect(page).toHaveURL(/.*dashboard/)
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
  })

  test('login fails with invalid credentials', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Login')
    
    // Fill with invalid credentials
    await page.fill('[name=email]', 'invalid@test.com')
    await page.fill('[name=password]', 'wrongpassword')
    await page.click('button[type=submit]')
    
    // Verify error message
    await expect(page.locator('text=/Invalid credentials/i')).toBeVisible()
    
    // Verify still on login page
    await expect(page).toHaveURL(/.*login/)
  })

  test('user can logout', async ({ page }) => {
    // Login first
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('[name=email]', 'patient@test.com')
    await page.fill('[name=password]', 'Test123456!')
    await page.click('button[type=submit]')
    
    // Logout
    await logout(page)
    
    // Verify redirect to home
    await expect(page).toHaveURL('/')
    
    // Verify auth token is cleared
    const token = await page.evaluate(() => localStorage.getItem('auth_token'))
    expect(token).toBeNull()
  })

  test('protected routes redirect to login', async ({ page }) => {
    // Try to access protected route without authentication
    await page.goto('/dashboard')
    
    // Verify redirect to login
    await expect(page).toHaveURL(/.*login/)
    await expect(page.locator('text=/Please login/i')).toBeVisible()
  })

  test('session persists after page refresh', async ({ page }) => {
    // Login
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('[name=email]', 'patient@test.com')
    await page.fill('[name=password]', 'Test123456!')
    await page.click('button[type=submit]')
    
    // Verify logged in
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
    
    // Refresh page
    await page.reload()
    
    // Verify still logged in
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
    await expect(page).toHaveURL(/.*dashboard/)
  })

  test('password reset flow works', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Login')
    await page.click('text=Forgot Password?')
    
    // Verify on password reset page
    await expect(page).toHaveURL(/.*reset-password/)
    
    // Enter email
    await page.fill('[name=email]', 'patient@test.com')
    await page.click('button:has-text("Send Reset Link")')
    
    // Verify confirmation message
    await expect(page.locator('text=/reset link sent/i')).toBeVisible()
  })

  test('email verification required for new accounts', async ({ page }) => {
    const email = `unverified-${Date.now()}@test.com`
    await signup(page, email, 'Test123456!', 'Test User', 'patient')
    
    // Verify email verification banner
    await expect(page.locator('[data-testid="email-verification-banner"]')).toBeVisible()
    await expect(page.locator('text=/verify your email/i')).toBeVisible()
    
    // Verify resend verification button
    await expect(page.locator('button:has-text("Resend Verification")')).toBeVisible()
  })

  test('role-based access control for patient', async ({ page }) => {
    // Login as patient
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('[name=email]', 'patient@test.com')
    await page.fill('[name=password]', 'Test123456!')
    await page.click('button[type=submit]')
    
    // Patient can access patient features
    await expect(page.locator('text=Upload Image')).toBeVisible()
    await expect(page.locator('text=My Reports')).toBeVisible()
    await expect(page.locator('text=Find Doctors')).toBeVisible()
    
    // Patient cannot access admin features
    await page.goto('/admin')
    await expect(page.locator('text=/Access Denied/i')).toBeVisible()
  })

  test('role-based access control for doctor', async ({ page }) => {
    // Login as verified doctor
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('[name=email]', 'doctor@test.com')
    await page.fill('[name=password]', 'Test123456!')
    await page.click('button[type=submit]')
    
    // Doctor can access doctor features
    await expect(page.locator('text=Patient Reports')).toBeVisible()
    await expect(page.locator('text=Appointments')).toBeVisible()
    
    // Doctor cannot access patient upload
    await page.goto('/upload')
    await expect(page.locator('text=/Access Denied/i')).toBeVisible()
  })

  test('role-based access control for admin', async ({ page }) => {
    // Login as admin
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('[name=email]', 'admin@test.com')
    await page.fill('[name=password]', 'Test123456!')
    await page.click('button[type=submit]')
    
    // Admin can access admin features
    await expect(page.locator('text=Admin Panel')).toBeVisible()
    await page.click('text=Admin Panel')
    
    await expect(page.locator('text=Doctor Verification')).toBeVisible()
    await expect(page.locator('text=Content Moderation')).toBeVisible()
    await expect(page.locator('text=Analytics')).toBeVisible()
  })
})
