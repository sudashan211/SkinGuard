# End-to-End Tests for SkinGuard

This directory contains comprehensive E2E tests for the SkinGuard AI Skin Cancer Screening Platform using Playwright.

## Test Coverage

### 1. Patient Upload Flow (`patient-upload.spec.ts`)
- Complete patient journey from login to AI analysis
- Image upload with drag-and-drop
- Symptom wizard (3 steps)
- AI results display with hotspot overlays
- Report history and comparison
- Image quality validation
- NSFW content filtering

### 2. Doctor Verification Flow (`doctor-verification.spec.ts`)
- Doctor registration process
- Admin verification workflow
- Access control for unverified doctors
- Patient report access for verified doctors
- Consultation notes management
- Appointment management

### 3. Admin Moderation Flow (`admin-moderation.spec.ts`)
- Flagged content moderation
- Platform analytics dashboard
- Skin-Wiki content management
- Audit logs
- User account management

### 4. Cross-Browser Compatibility (`cross-browser.spec.ts`)
- Landing page rendering
- Authentication across browsers
- Image upload functionality
- Google Maps integration
- Framer Motion animations
- Responsive layouts
- Form validation
- Session management
- CSS Grid and Flexbox layouts

### 5. Mobile Responsiveness (`mobile-responsiveness.spec.ts`)
- Mobile navigation menu
- Camera integration for image capture
- Touch gestures (zoom, pan, swipe)
- Mobile-optimized forms
- GPS integration for doctor locator
- Mobile-friendly UI components
- Bottom navigation bar
- Pull-to-refresh
- Landscape orientation support
- PWA functionality (manifest, service worker, offline mode)

### 6. Authentication (`authentication.spec.ts`)
- User signup (patient, doctor, admin)
- Login with valid/invalid credentials
- Logout functionality
- Protected route guards
- Session persistence
- Password reset flow
- Email verification
- Role-based access control

### 7. Appointments (`appointments.spec.ts`)
- Appointment booking (in-person and video)
- Appointment details and management
- Cancellation and rescheduling
- Doctor appointment management
- Appointment calendar view
- Video consultation setup and controls
- Screen sharing during consultations

### 8. Multi-Language Support (`multi-language.spec.ts`)
- Browser language detection
- Language switching (EN, ES, FR, DE, ZH)
- Language preference persistence
- Translated medical disclaimers
- Translated cancer type names
- Translated educational content
- Localized form validation messages
- Localized date/time formats
- Translated notifications and errors

## Running Tests

### Install Dependencies
```bash
npm install
npx playwright install
```

### Run All Tests
```bash
npm run test:e2e
```

### Run Specific Test File
```bash
npx playwright test patient-upload.spec.ts
```

### Run Tests in Headed Mode (See Browser)
```bash
npx playwright test --headed
```

### Run Tests on Specific Browser
```bash
# Chrome only
npx playwright test --project=chromium

# Firefox only
npx playwright test --project=firefox

# Safari only
npx playwright test --project=webkit

# Mobile Chrome
npx playwright test --project="Mobile Chrome"

# Mobile Safari
npx playwright test --project="Mobile Safari"
```

### Run Tests in Debug Mode
```bash
npx playwright test --debug
```

### Generate Test Report
```bash
npx playwright show-report
```

## Test Configuration

The Playwright configuration is in `playwright.config.ts`:

- **Base URL**: `http://localhost:3000`
- **Browsers**: Chrome, Firefox, Safari, Mobile Chrome, Mobile Safari
- **Retries**: 2 retries in CI, 0 locally
- **Timeout**: 30 seconds per test
- **Screenshots**: On failure
- **Videos**: On failure
- **Traces**: On first retry

## Prerequisites

### 1. Backend Server Running
The backend API must be running at `http://localhost:8000`:
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Frontend Dev Server Running
The frontend must be running at `http://localhost:3000`:
```bash
cd frontend
npm run dev
```

**Note**: The Playwright config includes a `webServer` option that automatically starts the dev server if it's not running.

### 3. Test Database
Tests should run against a test database, not production:
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/skinguard_test"
```

### 4. Test Users
The following test users should exist in the database:
- `patient@test.com` (role: patient, password: Test123456!)
- `doctor@test.com` (role: doctor, verified: true, password: Test123456!)
- `unverified-doctor@test.com` (role: doctor, verified: false, password: Test123456!)
- `admin@test.com` (role: admin, password: Test123456!)

### 5. Test Fixtures
Place test images in `tests/fixtures/` directory. See `tests/fixtures/README.md` for details.

## CI/CD Integration

### GitHub Actions
```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps
      - name: Run E2E tests
        run: |
          cd frontend
          npx playwright test
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## Best Practices

### 1. Use Data Test IDs
Always use `data-testid` attributes for selecting elements:
```typescript
await page.click('[data-testid="upload-button"]')
```

### 2. Wait for Elements
Use Playwright's auto-waiting, but add explicit waits when needed:
```typescript
await page.waitForSelector('[data-testid="results"]', { timeout: 30000 })
```

### 3. Clean Up After Tests
Ensure tests clean up any created data:
```typescript
test.afterEach(async () => {
  // Delete test data
  await cleanupTestData()
})
```

### 4. Use Helper Functions
Reuse common actions through helper functions:
```typescript
import { loginAsPatient } from './helpers/auth'
await loginAsPatient(page)
```

### 5. Test Isolation
Each test should be independent and not rely on other tests:
```typescript
test('should work independently', async ({ page }) => {
  // Setup
  // Test
  // Cleanup
})
```

## Debugging Tests

### 1. Use Playwright Inspector
```bash
npx playwright test --debug
```

### 2. Add Console Logs
```typescript
console.log('Current URL:', page.url())
```

### 3. Take Screenshots
```typescript
await page.screenshot({ path: 'debug.png' })
```

### 4. Pause Execution
```typescript
await page.pause()
```

### 5. View Trace
```bash
npx playwright show-trace trace.zip
```

## Common Issues

### Issue: Tests Timeout
**Solution**: Increase timeout or check if backend is running
```typescript
test.setTimeout(60000) // 60 seconds
```

### Issue: Element Not Found
**Solution**: Check if element exists and is visible
```typescript
await expect(page.locator('[data-testid="element"]')).toBeVisible()
```

### Issue: Flaky Tests
**Solution**: Add proper waits and use stable selectors
```typescript
await page.waitForLoadState('networkidle')
```

### Issue: Authentication Fails
**Solution**: Verify test users exist in database
```bash
psql -d skinguard_test -c "SELECT email, role FROM profiles;"
```

## Performance Optimization

### 1. Run Tests in Parallel
```bash
npx playwright test --workers=4
```

### 2. Use Shared Context
```typescript
test.use({ storageState: 'auth.json' })
```

### 3. Skip Unnecessary Tests
```typescript
test.skip('slow test', async ({ page }) => {
  // ...
})
```

## Maintenance

- Update tests when UI changes
- Keep test data fixtures up to date
- Review and update selectors regularly
- Monitor test execution times
- Fix flaky tests immediately

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [API Reference](https://playwright.dev/docs/api/class-playwright)
- [Debugging Guide](https://playwright.dev/docs/debug)

## Support

For issues or questions about E2E tests:
1. Check this README
2. Review test logs and screenshots
3. Consult Playwright documentation
4. Contact the development team
