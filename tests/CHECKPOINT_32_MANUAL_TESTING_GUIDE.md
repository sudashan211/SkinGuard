# Checkpoint 32: Manual Testing Guide

## Overview
This guide helps you manually verify the advanced features implemented in Phase 15:
- PWA offline functionality
- Multi-language switching
- Mobile responsiveness

## Prerequisites
- Frontend development server running (`npm run dev` in frontend directory)
- Backend API server running (optional for full testing)
- Modern browser (Chrome, Firefox, Safari, or Edge)
- Mobile device or browser DevTools for mobile testing

---

## Test 1: PWA Offline Functionality

### 1.1 PWA Installation
**Steps:**
1. Open the application in Chrome/Edge
2. Look for the install prompt banner at the bottom of the page
3. Click "Install" button
4. Verify the app installs and opens in standalone mode

**Expected Result:**
- Install prompt appears automatically
- App installs successfully
- App opens without browser UI (standalone mode)

### 1.2 Offline Mode - View Historical Reports
**Steps:**
1. Log in as a patient
2. Navigate to "Report History" page
3. View several past reports (this caches them)
4. Open browser DevTools (F12)
5. Go to Network tab → Select "Offline" mode
6. Refresh the page or navigate to different reports

**Expected Result:**
- Previously viewed reports load successfully
- Images display correctly from cache
- Offline indicator appears at top of page: "You're offline. Some features may be limited."

### 1.3 Offline Upload Queue
**Steps:**
1. While still offline, try to upload a new image
2. The upload should be queued
3. Go back online (disable offline mode in DevTools)
4. Wait a few seconds

**Expected Result:**
- Upload is queued with message "Syncing X pending upload(s)..."
- When online, sync notification appears
- Upload completes automatically
- Success message: "Successfully synced X upload(s)"

### 1.4 Service Worker Caching
**Steps:**
1. Open DevTools → Application tab → Service Workers
2. Verify service worker is registered and active
3. Check Cache Storage → Verify caches exist:
   - `api-cache`
   - `medical-images-cache`
   - `images-cache`
   - `fonts-cache`

**Expected Result:**
- Service worker shows as "activated and running"
- Multiple caches present with cached resources

---

## Test 2: Multi-Language Support

### 2.1 Language Detection
**Steps:**
1. Clear browser localStorage
2. Change browser language to Spanish (Settings → Languages)
3. Open the application
4. Check the interface language

**Expected Result:**
- Interface automatically displays in Spanish
- Language preference saved to localStorage

### 2.2 Language Switcher
**Steps:**
1. Click the globe icon (🌐) in the navigation bar
2. Verify dropdown shows all 5 languages:
   - English
   - Español
   - Français
   - Deutsch
   - 中文
3. Select "Français"
4. Verify interface updates immediately

**Expected Result:**
- All 5 languages listed
- Current language has checkmark (✓)
- Interface updates without page reload
- Language preference persists after refresh

### 2.3 Medical Disclaimer Translation
**Steps:**
1. Upload an image and view AI results
2. Check the medical disclaimer text
3. Switch to different languages
4. Verify disclaimer is translated

**Expected Result:**
- Disclaimer appears in selected language
- Translation maintains medical accuracy
- All UI elements update consistently

### 2.4 Educational Content Translation
**Steps:**
1. Navigate to Skin-Wiki section
2. View cancer type articles
3. Switch languages
4. Verify article content is translated

**Expected Result:**
- Article titles translated
- Article content translated
- Cancer type names properly localized

---

## Test 3: Mobile Responsiveness

### 3.1 Responsive Layout (Desktop Browser)
**Steps:**
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test different screen sizes:
   - Mobile (375px)
   - Tablet (768px)
   - Desktop (1920px)
4. Navigate through all pages

**Expected Result:**
- Layout adapts smoothly to all screen sizes
- No horizontal scrolling
- Touch targets are appropriately sized (min 44x44px)
- Navigation menu collapses on mobile

### 3.2 Touch Gestures - Image Zoom/Pan
**Steps:**
1. Switch to mobile view in DevTools
2. Navigate to a medical report with an image
3. Use touch simulation:
   - Pinch to zoom (Ctrl+Scroll or pinch gesture)
   - Drag to pan when zoomed in
4. Tap reset button to return to normal view

**Expected Result:**
- Pinch gesture zooms image smoothly
- Zoom level indicator shows percentage (e.g., "150%")
- Pan works when zoomed in
- Reset button appears when zoomed
- Instructions show: "Pinch to zoom • Drag to pan"

### 3.3 Mobile Camera Capture
**Steps:**
1. On mobile view, go to diagnostic uploader
2. Click the upload area
3. Verify camera option appears

**Expected Result:**
- File picker shows "Take Photo" or "Camera" option
- Camera can be accessed directly (on real mobile device)
- Captured photo can be uploaded

### 3.4 Map Interactions (Mobile)
**Steps:**
1. Navigate to Doctor Locator page
2. Verify map loads and centers on user location
3. Test touch interactions:
   - Pinch to zoom map
   - Drag to pan map
   - Tap markers to view doctor info

**Expected Result:**
- Map centers on GPS location (if permission granted)
- Touch gestures work smoothly
- Doctor cards display properly on mobile
- WhatsApp button is easily tappable

---

## Test 4: Cross-Browser Compatibility

### 4.1 Test in Multiple Browsers
**Browsers to test:**
- Chrome/Edge (Chromium)
- Firefox
- Safari (if on Mac/iOS)

**Steps:**
1. Open application in each browser
2. Test PWA installation
3. Test language switching
4. Test mobile view (DevTools)

**Expected Result:**
- All features work consistently across browsers
- PWA installs in supported browsers
- No console errors

---

## Test 5: Network Reconnection

### 5.1 Sync on Reconnection
**Steps:**
1. Go offline (DevTools Network → Offline)
2. Try to perform actions (upload, book appointment)
3. Actions are queued
4. Go back online
5. Observe automatic sync

**Expected Result:**
- Offline indicator appears immediately
- Actions are queued with notification
- Sync starts automatically when online
- Success/failure notifications appear
- Pending count decreases as items sync

---

## Verification Checklist

Use this checklist to track your testing:

### PWA Features
- [ ] PWA install prompt appears
- [ ] App installs successfully
- [ ] Offline mode works for cached content
- [ ] Upload queue works offline
- [ ] Sync works on reconnection
- [ ] Service worker is active
- [ ] Caches are populated

### Multi-Language
- [ ] Browser language detected automatically
- [ ] All 5 languages available
- [ ] Language switcher works
- [ ] Preference persists
- [ ] Disclaimers translated
- [ ] Educational content translated

### Mobile Features
- [ ] Responsive layout on all screen sizes
- [ ] Touch gestures work (zoom/pan)
- [ ] Camera capture available
- [ ] Map interactions work on mobile
- [ ] Navigation menu adapts
- [ ] Touch targets are appropriately sized

### Cross-Browser
- [ ] Works in Chrome/Edge
- [ ] Works in Firefox
- [ ] Works in Safari (if available)
- [ ] No console errors

---

## Troubleshooting

### PWA Not Installing
- Check if HTTPS is enabled (required for PWA)
- Clear browser cache and reload
- Check DevTools Console for errors

### Offline Mode Not Working
- Verify service worker is registered (DevTools → Application)
- Check if caches are populated
- Try hard refresh (Ctrl+Shift+R)

### Language Not Switching
- Check browser console for errors
- Verify translation files exist in `frontend/src/i18n/locales/`
- Clear localStorage and try again

### Touch Gestures Not Working
- Ensure touch simulation is enabled in DevTools
- Test on actual mobile device for best results
- Check if `touchAction: 'none'` is set on elements

---

## Success Criteria

✅ **Checkpoint 32 passes if:**
1. PWA installs and works offline for cached content
2. All 5 languages switch correctly and persist
3. Mobile layout is responsive on all screen sizes
4. Touch gestures work for image zoom/pan
5. Network reconnection triggers automatic sync
6. No critical errors in browser console

---

## Next Steps

After completing this checkpoint:
1. Document any issues found
2. Proceed to Phase 16: Privacy, Security, and Performance
3. Begin Task 33: Privacy and Security Features

---

## Notes

- Some features require HTTPS in production (PWA, camera access)
- Test on real mobile devices for best accuracy
- Service worker updates may require hard refresh during development
- Translation quality should be reviewed by native speakers
