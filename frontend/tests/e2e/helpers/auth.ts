import { Page } from '@playwright/test'

/**
 * Authentication helper functions for E2E tests
 */

export async function loginAsPatient(page: Page) {
  await page.goto('/')
  await page.click('text=Login')
  await page.fill('[name=email]', 'patient@test.com')
  await page.fill('[name=password]', 'Test123456!')
  await page.click('button[type=submit]')
  await page.waitForURL('**/dashboard')
}

export async function loginAsDoctor(page: Page) {
  await page.goto('/')
  await page.click('text=Login')
  await page.fill('[name=email]', 'doctor@test.com')
  await page.fill('[name=password]', 'Test123456!')
  await page.click('button[type=submit]')
  await page.waitForURL('**/doctor-dashboard')
}

export async function loginAsAdmin(page: Page) {
  await page.goto('/')
  await page.click('text=Login')
  await page.fill('[name=email]', 'admin@test.com')
  await page.fill('[name=password]', 'Test123456!')
  await page.click('button[type=submit]')
  await page.waitForURL('**/admin')
}

export async function signup(
  page: Page,
  email: string,
  password: string,
  fullName: string,
  role: 'patient' | 'doctor' | 'admin'
) {
  await page.goto('/')
  await page.click('text=Sign Up')
  await page.fill('[name=email]', email)
  await page.fill('[name=password]', password)
  await page.fill('[name=fullName]', fullName)
  await page.selectOption('[name=role]', role)
  await page.click('button[type=submit]')
}

export async function logout(page: Page) {
  await page.click('[aria-label="User menu"]')
  await page.click('text=Logout')
  await page.waitForURL('/')
}
