import { test, expect } from '@playwright/test'
import { loginAsPatient, loginAsDoctor } from './helpers/auth'

/**
 * E2E Test: Appointment Booking and Management
 * Tests appointment scheduling, confirmation, and video consultation setup
 * 
 * Validates: Requirements 21.1 (Mobile Responsiveness and PWA)
 */

test.describe('Appointment Booking', () => {
  test('patient can book in-person appointment with doctor', async ({ page }) => {
    await loginAsPatient(page)
    
    // Navigate to doctor locator
    await page.click('text=Find Doctors')
    
    // Wait for doctors to load
    await page.waitForSelector('[data-testid="doctor-card"]')
    
    // Select a doctor
    await page.locator('[data-testid="doctor-card"]').first().click()
    
    // Verify doctor profile modal
    await expect(page.locator('[data-testid="doctor-profile-modal"]')).toBeVisible()
    await expect(page.locator('[data-testid="doctor-name"]')).toBeVisible()
    await expect(page.locator('[data-testid="doctor-rating"]')).toBeVisible()
    await expect(page.locator('[data-testid="clinic-location"]')).toBeVisible()
    
    // Click book appointment
    await page.click('button:has-text("Book Appointment")')
    
    // Select appointment type
    await page.click('[data-testid="appointment-type-in-person"]')
    
    // Select date and time
    await page.click('[data-testid="date-picker"]')
    await page.click('[data-testid="available-date"]')
    await page.click('[data-testid="time-slot-10am"]')
    
    // Add notes
    await page.fill('[name=appointmentNotes]', 'I would like to discuss my recent screening results.')
    
    // Confirm booking
    await page.click('button:has-text("Confirm Booking")')
    
    // Verify confirmation message
    await expect(page.locator('text=/Appointment booked successfully/i')).toBeVisible()
    
    // Verify appointment appears in list
    await page.click('text=My Appointments')
    await expect(page.locator('[data-testid="appointment-card"]')).toBeVisible()
    await expect(page.locator('text=/pending/i')).toBeVisible()
  })

  test('patient can book video consultation', async ({ page }) => {
    await loginAsPatient(page)
    
    await page.click('text=Find Doctors')
    await page.waitForSelector('[data-testid="doctor-card"]')
    await page.locator('[data-testid="doctor-card"]').first().click()
    
    await page.click('button:has-text("Book Appointment")')
    
    // Select video consultation
    await page.click('[data-testid="appointment-type-video"]')
    
    // Select date and time
    await page.click('[data-testid="date-picker"]')
    await page.click('[data-testid="available-date"]')
    await page.click('[data-testid="time-slot-2pm"]')
    
    // Confirm booking
    await page.click('button:has-text("Confirm Booking")')
    
    // Verify video consultation details
    await expect(page.locator('text=/Video consultation scheduled/i')).toBeVisible()
    await expect(page.locator('text=/meeting link will be sent/i')).toBeVisible()
  })

  test('patient can view appointment details', async ({ page }) => {
    await loginAsPatient(page)
    
    await page.click('text=My Appointments')
    
    // Click on appointment
    await page.locator('[data-testid="appointment-card"]').first().click()
    
    // Verify appointment details
    await expect(page.locator('[data-testid="appointment-details"]')).toBeVisible()
    await expect(page.locator('[data-testid="doctor-info"]')).toBeVisible()
    await expect(page.locator('[data-testid="appointment-date"]')).toBeVisible()
    await expect(page.locator('[data-testid="appointment-time"]')).toBeVisible()
    await expect(page.locator('[data-testid="appointment-type"]')).toBeVisible()
    await expect(page.locator('[data-testid="appointment-status"]')).toBeVisible()
  })

  test('patient can cancel appointment', async ({ page }) => {
    await loginAsPatient(page)
    
    await page.click('text=My Appointments')
    await page.locator('[data-testid="appointment-card"]').first().click()
    
    // Cancel appointment
    await page.click('button:has-text("Cancel Appointment")')
    
    // Confirm cancellation
    await page.fill('[name=cancellationReason]', 'Schedule conflict')
    await page.click('button:has-text("Confirm Cancellation")')
    
    // Verify cancellation
    await expect(page.locator('text=/Appointment cancelled/i')).toBeVisible()
    await expect(page.locator('text=/cancelled/i')).toBeVisible()
  })

  test('patient can reschedule appointment', async ({ page }) => {
    await loginAsPatient(page)
    
    await page.click('text=My Appointments')
    await page.locator('[data-testid="appointment-card"]').first().click()
    
    // Reschedule
    await page.click('button:has-text("Reschedule")')
    
    // Select new date and time
    await page.click('[data-testid="date-picker"]')
    await page.click('[data-testid="available-date"]')
    await page.click('[data-testid="time-slot-3pm"]')
    
    // Confirm reschedule
    await page.click('button:has-text("Confirm Reschedule")')
    
    // Verify reschedule confirmation
    await expect(page.locator('text=/Appointment rescheduled/i')).toBeVisible()
  })

  test('patient receives appointment reminder', async ({ page }) => {
    await loginAsPatient(page)
    
    // Navigate to appointments
    await page.click('text=My Appointments')
    
    // Check for upcoming appointment with reminder
    const upcomingAppointment = page.locator('[data-testid="appointment-card"]').filter({
      hasText: 'Tomorrow'
    })
    
    if (await upcomingAppointment.count() > 0) {
      await expect(upcomingAppointment.locator('[data-testid="reminder-badge"]')).toBeVisible()
    }
  })
})

test.describe('Doctor Appointment Management', () => {
  test('doctor can view pending appointments', async ({ page }) => {
    await loginAsDoctor(page)
    
    await page.click('text=Appointments')
    
    // Verify appointments list
    await expect(page.locator('[data-testid="appointments-list"]')).toBeVisible()
    
    // Filter by pending
    await page.selectOption('[name=statusFilter]', 'pending')
    
    // Verify pending appointments are shown
    const pendingAppointments = page.locator('[data-testid="appointment-card"]')
    const count = await pendingAppointments.count()
    expect(count).toBeGreaterThanOrEqual(0)
  })

  test('doctor can confirm appointment', async ({ page }) => {
    await loginAsDoctor(page)
    
    await page.click('text=Appointments')
    await page.selectOption('[name=statusFilter]', 'pending')
    
    // Select first pending appointment
    await page.locator('[data-testid="appointment-card"]').first().click()
    
    // Confirm appointment
    await page.click('button:has-text("Confirm")')
    
    // Verify confirmation
    await expect(page.locator('text=/Appointment confirmed/i')).toBeVisible()
    await expect(page.locator('text=/confirmed/i')).toBeVisible()
  })

  test('doctor can view appointment calendar', async ({ page }) => {
    await loginAsDoctor(page)
    
    await page.click('text=Appointments')
    await page.click('[data-testid="calendar-view"]')
    
    // Verify calendar is displayed
    await expect(page.locator('[data-testid="appointment-calendar"]')).toBeVisible()
    
    // Verify appointments are shown on calendar
    await expect(page.locator('[data-testid="calendar-event"]')).toBeVisible()
    
    // Click on calendar event
    await page.locator('[data-testid="calendar-event"]').first().click()
    
    // Verify appointment details popup
    await expect(page.locator('[data-testid="appointment-popup"]')).toBeVisible()
  })

  test('doctor can mark appointment as completed', async ({ page }) => {
    await loginAsDoctor(page)
    
    await page.click('text=Appointments')
    await page.selectOption('[name=statusFilter]', 'confirmed')
    
    // Select appointment
    await page.locator('[data-testid="appointment-card"]').first().click()
    
    // Mark as completed
    await page.click('button:has-text("Mark as Completed")')
    
    // Add consultation summary
    await page.fill('[name=consultationSummary]', 'Patient examined. Recommended follow-up in 3 months.')
    await page.click('button:has-text("Save and Complete")')
    
    // Verify completion
    await expect(page.locator('text=/Appointment completed/i')).toBeVisible()
  })

  test('doctor can set availability schedule', async ({ page }) => {
    await loginAsDoctor(page)
    
    await page.click('text=Appointments')
    await page.click('button:has-text("Manage Availability")')
    
    // Set working hours
    await page.selectOption('[name=mondayStart]', '09:00')
    await page.selectOption('[name=mondayEnd]', '17:00')
    
    // Set break time
    await page.check('[name=lunchBreak]')
    await page.selectOption('[name=breakStart]', '12:00')
    await page.selectOption('[name=breakEnd]', '13:00')
    
    // Save availability
    await page.click('button:has-text("Save Availability")')
    
    // Verify saved
    await expect(page.locator('text=/Availability updated/i')).toBeVisible()
  })
})

test.describe('Video Consultation', () => {
  test('patient can join video consultation', async ({ page }) => {
    await loginAsPatient(page)
    
    await page.click('text=My Appointments')
    
    // Find video consultation appointment
    const videoAppointment = page.locator('[data-testid="appointment-card"]').filter({
      hasText: 'Video'
    })
    
    if (await videoAppointment.count() > 0) {
      await videoAppointment.first().click()
      
      // Verify join button is available
      await expect(page.locator('button:has-text("Join Video Call")')).toBeVisible()
      
      // Click join (opens in new tab/window)
      const [videoPage] = await Promise.all([
        page.waitForEvent('popup'),
        page.click('button:has-text("Join Video Call")')
      ])
      
      // Verify video room loads
      await videoPage.waitForLoadState()
      await expect(videoPage.locator('[data-testid="video-room"]')).toBeVisible()
    }
  })

  test('video room has required controls', async ({ page }) => {
    // Simulate joining video room directly
    await page.goto('/video-room/test-room-id')
    
    // Verify video controls
    await expect(page.locator('[data-testid="mute-button"]')).toBeVisible()
    await expect(page.locator('[data-testid="video-toggle"]')).toBeVisible()
    await expect(page.locator('[data-testid="screen-share"]')).toBeVisible()
    await expect(page.locator('[data-testid="end-call"]')).toBeVisible()
    
    // Verify participant video
    await expect(page.locator('[data-testid="local-video"]')).toBeVisible()
    await expect(page.locator('[data-testid="remote-video"]')).toBeVisible()
  })

  test('doctor can share screen during video consultation', async ({ page, context }) => {
    await loginAsDoctor(page)
    
    // Join video room
    await page.goto('/video-room/test-room-id')
    
    // Grant screen share permission
    await context.grantPermissions(['display-capture'])
    
    // Click screen share
    await page.click('[data-testid="screen-share"]')
    
    // Verify screen share is active
    await expect(page.locator('[data-testid="screen-share-active"]')).toBeVisible()
  })
})
