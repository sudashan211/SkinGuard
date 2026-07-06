import { test, expect } from '@playwright/test'
import { loginAsPatient } from './helpers/auth'

/**
 * E2E Test: Multi-Language Support
 * Tests internationalization (i18n) and language switching functionality
 * 
 * Validates: Requirements 21.1 (Mobile Responsiveness and PWA)
 */

test.describe('Multi-Language Support', () => {
  test('app detects browser language on first visit', async ({ page, context }) => {
    // Set browser language to Spanish
    await context.addInitScript(() => {
      Object.defineProperty(navigator, 'language', {
        get: () => 'es-ES'
      })
    })
    
    await page.goto('/')
    
    // Verify Spanish content is displayed
    await expect(page.locator('text=Iniciar sesión')).toBeVisible() // "Login" in Spanish
  })

  test('user can switch language from English to Spanish', async ({ page }) => {
    await page.goto('/')
    
    // Open language selector
    await page.click('[data-testid="language-selector"]')
    
    // Select Spanish
    await page.click('[data-testid="language-option-es"]')
    
    // Verify language changed
    await expect(page.locator('text=Iniciar sesión')).toBeVisible()
    await expect(page.locator('text=Registrarse')).toBeVisible()
    
    // Verify language preference is saved
    const savedLang = await page.evaluate(() => localStorage.getItem('language'))
    expect(savedLang).toBe('es')
  })

  test('user can switch language from English to French', async ({ page }) => {
    await page.goto('/')
    
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-fr"]')
    
    // Verify French content
    await expect(page.locator('text=Connexion')).toBeVisible() // "Login" in French
    await expect(page.locator("text=S'inscrire")).toBeVisible() // "Sign Up" in French
  })

  test('user can switch language from English to German', async ({ page }) => {
    await page.goto('/')
    
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-de"]')
    
    // Verify German content
    await expect(page.locator('text=Anmelden')).toBeVisible() // "Login" in German
    await expect(page.locator('text=Registrieren')).toBeVisible() // "Sign Up" in German
  })

  test('user can switch language from English to Mandarin Chinese', async ({ page }) => {
    await page.goto('/')
    
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-zh"]')
    
    // Verify Chinese content
    await expect(page.locator('text=登录')).toBeVisible() // "Login" in Chinese
    await expect(page.locator('text=注册')).toBeVisible() // "Sign Up" in Chinese
  })

  test('language preference persists after page refresh', async ({ page }) => {
    await page.goto('/')
    
    // Switch to Spanish
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-es"]')
    
    // Refresh page
    await page.reload()
    
    // Verify Spanish is still active
    await expect(page.locator('text=Iniciar sesión')).toBeVisible()
  })

  test('medical disclaimers are translated', async ({ page }) => {
    await loginAsPatient(page)
    
    // Switch to Spanish
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-es"]')
    
    // Upload image and view results
    await page.click('text=Subir imagen') // "Upload Image" in Spanish
    await page.setInputFiles('input[type=file]', './tests/fixtures/test-lesion.jpg')
    await page.click('button:has-text("Analizar")')
    
    // Wait for results
    await page.waitForSelector('[data-testid="ai-results"]', { timeout: 30000 })
    
    // Verify disclaimer is in Spanish
    await expect(page.locator('text=/estimación de probabilidad del 94%/i')).toBeVisible()
    await expect(page.locator('text=/consulte a médicos verificados/i')).toBeVisible()
  })

  test('cancer type names are translated', async ({ page }) => {
    await loginAsPatient(page)
    
    // Switch to French
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-fr"]')
    
    // Navigate to results
    await page.click('text=Mes rapports') // "My Reports" in French
    await page.locator('[data-testid="report-card"]').first().click()
    
    // Verify cancer types are in French
    await expect(page.locator('text=Mélanome')).toBeVisible() // "Melanoma" in French
    await expect(page.locator('text=Carcinome basocellulaire')).toBeVisible() // "Basal Cell Carcinoma" in French
  })

  test('educational content is translated', async ({ page }) => {
    await page.goto('/')
    
    // Switch to German
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-de"]')
    
    // Navigate to Skin-Wiki
    await page.click('text=Haut-Wiki') // "Skin-Wiki" in German
    
    // Verify article titles are in German
    await expect(page.locator('text=Hautkrebs verstehen')).toBeVisible() // "Understanding Skin Cancer" in German
    
    // Click on article
    await page.locator('[data-testid="article-card"]').first().click()
    
    // Verify article content is in German
    await expect(page.locator('[data-testid="article-content"]')).toContainText('Hautkrebs')
  })

  test('form validation messages are translated', async ({ page }) => {
    await page.goto('/')
    
    // Switch to Spanish
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-es"]')
    
    // Try to submit empty login form
    await page.click('text=Iniciar sesión')
    await page.click('button[type=submit]')
    
    // Verify validation messages are in Spanish
    await expect(page.locator('text=/correo electrónico es obligatorio/i')).toBeVisible()
    await expect(page.locator('text=/contraseña es obligatoria/i')).toBeVisible()
  })

  test('date and time formats are localized', async ({ page }) => {
    await loginAsPatient(page)
    
    // Switch to French
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-fr"]')
    
    // Navigate to appointments
    await page.click('text=Mes rendez-vous') // "My Appointments" in French
    
    // Verify date format is French (DD/MM/YYYY)
    const dateText = await page.locator('[data-testid="appointment-date"]').first().textContent()
    expect(dateText).toMatch(/\d{2}\/\d{2}\/\d{4}/)
  })

  test('notification messages are translated', async ({ page }) => {
    await loginAsPatient(page)
    
    // Switch to German
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-de"]')
    
    // Trigger a notification (e.g., update profile)
    await page.click('[data-testid="user-menu"]')
    await page.click('text=Profil') // "Profile" in German
    await page.fill('[name=fullName]', 'Updated Name')
    await page.click('button:has-text("Speichern")') // "Save" in German
    
    // Verify success notification is in German
    await expect(page.locator('text=/Profil erfolgreich aktualisiert/i')).toBeVisible()
  })

  test('error messages are translated', async ({ page }) => {
    await page.goto('/')
    
    // Switch to Spanish
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-es"]')
    
    // Try to login with invalid credentials
    await page.click('text=Iniciar sesión')
    await page.fill('[name=email]', 'invalid@test.com')
    await page.fill('[name=password]', 'wrongpassword')
    await page.click('button[type=submit]')
    
    // Verify error message is in Spanish
    await expect(page.locator('text=/Credenciales inválidas/i')).toBeVisible()
  })

  test('all supported languages are available in selector', async ({ page }) => {
    await page.goto('/')
    
    await page.click('[data-testid="language-selector"]')
    
    // Verify all 5 supported languages
    await expect(page.locator('[data-testid="language-option-en"]')).toBeVisible() // English
    await expect(page.locator('[data-testid="language-option-es"]')).toBeVisible() // Spanish
    await expect(page.locator('[data-testid="language-option-fr"]')).toBeVisible() // French
    await expect(page.locator('[data-testid="language-option-de"]')).toBeVisible() // German
    await expect(page.locator('[data-testid="language-option-zh"]')).toBeVisible() // Chinese
  })

  test('RTL layout for Arabic (if supported)', async ({ page }) => {
    await page.goto('/')
    
    // Check if Arabic is supported
    await page.click('[data-testid="language-selector"]')
    const arabicOption = page.locator('[data-testid="language-option-ar"]')
    
    if (await arabicOption.count() > 0) {
      await arabicOption.click()
      
      // Verify RTL direction
      const htmlDir = await page.locator('html').getAttribute('dir')
      expect(htmlDir).toBe('rtl')
      
      // Verify text alignment
      const bodyAlign = await page.locator('body').evaluate(el => 
        window.getComputedStyle(el).textAlign
      )
      expect(bodyAlign).toBe('right')
    }
  })

  test('language switch updates URL parameters', async ({ page }) => {
    await page.goto('/')
    
    // Switch to Spanish
    await page.click('[data-testid="language-selector"]')
    await page.click('[data-testid="language-option-es"]')
    
    // Verify URL contains language parameter
    await expect(page).toHaveURL(/[?&]lang=es/)
  })
})
