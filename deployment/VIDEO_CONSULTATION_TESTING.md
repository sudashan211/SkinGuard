# Video Consultation Service Testing Procedures

## Overview

This document provides comprehensive testing procedures for the video consultation service in SkinGuard production environment. Video consultations must be HIPAA-compliant with end-to-end encryption.

---

## 1. Video Service Configuration

### 1.1 Twilio Configuration

#### Account Setup
```bash
# Set environment variables
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_API_KEY="SKxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_API_SECRET="xxxxxxxxxxxxxxxxxxxxxxxx"

# Test API credentials
curl -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID.json" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"
```

**Expected Response**: HTTP 200 with account details

#### Create Video Room
```bash
# Create test room
curl -X POST "https://video.twilio.com/v1/Rooms" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
  -d "UniqueName=test-room-$(date +%s)" \
  -d "Type=group" \
  -d "MaxParticipants=2"
```

**Verification**:
- [ ] Room created successfully
- [ ] Room SID returned
- [ ] Room status: "in-progress"

### 1.2 Agora Configuration (Alternative)

#### Account Setup
```bash
# Set environment variables
export AGORA_APP_ID="xxxxxxxxxxxxxxxxxxxxxxxx"
export AGORA_APP_CERTIFICATE="xxxxxxxxxxxxxxxxxxxxxxxx"

# Test API
curl -X GET "https://api.agora.io/dev/v1/projects" \
  -H "Authorization: Basic $(echo -n $AGORA_APP_ID:$AGORA_APP_CERTIFICATE | base64)"
```

#### Generate Token
```python
# Python script to generate Agora token
from agora_token_builder import RtcTokenBuilder
import time

app_id = "YOUR_APP_ID"
app_certificate = "YOUR_APP_CERTIFICATE"
channel_name = "test-channel"
uid = 0
expiration_time_in_seconds = 3600

current_timestamp = int(time.time())
privilege_expired_ts = current_timestamp + expiration_time_in_seconds

token = RtcTokenBuilder.buildTokenWithUid(
    app_id, app_certificate, channel_name, uid, 1, privilege_expired_ts
)
print(token)
```

---

## 2. Video Room Creation Testing

### 2.1 Room Generation

#### Test Room Creation API
```bash
# Create appointment with video consultation
curl -X POST https://api.skinguard.com/api/appointments \
  -H "Authorization: Bearer $PATIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": "DOCTOR_UUID",
    "scheduled_at": "2024-12-20T14:00:00Z",
    "consultation_type": "video"
  }'

# Generate video room
curl -X POST https://api.skinguard.com/api/appointments/APPOINTMENT_ID/video-room \
  -H "Authorization: Bearer $PATIENT_TOKEN"
```

**Expected Response**:
```json
{
  "appointment_id": "uuid",
  "video_room_url": "https://skinguard.com/video/room-token-xyz",
  "room_name": "appointment-uuid",
  "expires_at": "2024-12-20T15:00:00Z"
}
```

**Verification**:
- [ ] Video room URL generated
- [ ] URL is unique per appointment
- [ ] URL contains access token
- [ ] Expiration time set correctly (1 hour after scheduled time)

### 2.2 Room Access Control

#### Test Patient Access
```bash
# Patient accesses video room
curl -X GET "https://api.skinguard.com/api/video/room/ROOM_TOKEN" \
  -H "Authorization: Bearer $PATIENT_TOKEN"
```

**Verification**:
- [ ] Patient can access their own appointment room
- [ ] Patient cannot access other patients' rooms
- [ ] Access denied before scheduled time (>15 minutes early)
- [ ] Access granted 15 minutes before scheduled time
- [ ] Access denied after expiration

#### Test Doctor Access
```bash
# Doctor accesses video room
curl -X GET "https://api.skinguard.com/api/video/room/ROOM_TOKEN" \
  -H "Authorization: Bearer $DOCTOR_TOKEN"
```

**Verification**:
- [ ] Doctor can access their appointment rooms
- [ ] Doctor cannot access other doctors' rooms
- [ ] Access granted 15 minutes before scheduled time

---

## 3. Video Call Quality Testing

### 3.1 Basic Video Call Test

#### Test Setup
**Participants**: 1 patient, 1 doctor  
**Devices**: 2 computers with webcam/microphone  
**Network**: Stable broadband connection (10+ Mbps)

#### Test Procedure
1. Patient joins video room
2. Doctor joins video room
3. Conduct 5-minute test call
4. Test all features

**Verification Checklist**:
- [ ] Both participants can see each other
- [ ] Video quality: 720p or higher
- [ ] Frame rate: 24+ fps
- [ ] Audio quality: clear, no echo
- [ ] Audio sync: no lip-sync issues
- [ ] Latency: <300ms
- [ ] Connection stable: no drops

#### Measure Video Quality
```javascript
// In browser console during call
const stats = await pc.getStats();
stats.forEach(report => {
  if (report.type === 'inbound-rtp' && report.mediaType === 'video') {
    console.log('Video Resolution:', report.frameWidth, 'x', report.frameHeight);
    console.log('Frame Rate:', report.framesPerSecond);
    console.log('Packets Lost:', report.packetsLost);
    console.log('Jitter:', report.jitter);
  }
});
```

**Target Metrics**:
- Resolution: 640x480 minimum, 1280x720 preferred
- Frame rate: 24+ fps
- Packet loss: <1%
- Jitter: <30ms

### 3.2 Audio Quality Test

#### Test Procedure
1. Patient speaks for 30 seconds
2. Doctor confirms audio clarity
3. Doctor speaks for 30 seconds
4. Patient confirms audio clarity
5. Both speak simultaneously (test echo cancellation)

**Verification**:
- [ ] Audio clear and intelligible
- [ ] No background noise
- [ ] No echo or feedback
- [ ] No audio cutting out
- [ ] Echo cancellation working
- [ ] Automatic gain control working

#### Measure Audio Quality
```javascript
// In browser console
const stats = await pc.getStats();
stats.forEach(report => {
  if (report.type === 'inbound-rtp' && report.mediaType === 'audio') {
    console.log('Audio Level:', report.audioLevel);
    console.log('Packets Lost:', report.packetsLost);
    console.log('Jitter:', report.jitter);
  }
});
```

**Target Metrics**:
- Packet loss: <1%
- Jitter: <30ms
- Audio level: consistent

### 3.3 Screen Sharing Test

#### Test Procedure
1. Doctor clicks "Share Screen" button
2. Doctor selects medical report window
3. Patient views shared screen
4. Doctor annotates on shared screen (if feature available)
5. Doctor stops screen sharing

**Verification**:
- [ ] Screen sharing button visible
- [ ] Window/screen selection works
- [ ] Shared content visible to patient
- [ ] Shared content clear and readable
- [ ] Frame rate acceptable (10+ fps)
- [ ] Can switch between camera and screen share
- [ ] Screen sharing stops correctly

### 3.4 Network Resilience Test

#### Test Procedure
1. Start video call with good connection
2. Throttle network to 1 Mbps
3. Observe call quality
4. Restore network
5. Observe recovery

**Network Throttling** (Chrome DevTools):
1. Open DevTools (F12)
2. Go to Network tab
3. Select "Slow 3G" or custom throttling

**Verification**:
- [ ] Call continues (doesn't drop)
- [ ] Video quality degrades gracefully
- [ ] Audio remains clear (prioritized)
- [ ] Reconnects automatically if dropped
- [ ] Quality improves when network restored
- [ ] No permanent degradation

#### Test Packet Loss
```bash
# Simulate packet loss (Linux)
sudo tc qdisc add dev eth0 root netem loss 5%

# Run video call and observe

# Remove packet loss
sudo tc qdisc del dev eth0 root
```

**Verification**:
- [ ] Call continues with 5% packet loss
- [ ] Video may freeze briefly
- [ ] Audio remains mostly clear
- [ ] Automatic recovery when packet loss stops

---

## 4. Mobile Device Testing

### 4.1 iOS Testing

#### Devices to Test
- [ ] iPhone 12 or newer (iOS 15+)
- [ ] iPad Pro (iOS 15+)

#### Test Procedure
1. Open Safari on iOS device
2. Navigate to video room URL
3. Grant camera/microphone permissions
4. Join video call

**Verification**:
- [ ] Video works in Safari
- [ ] Camera permission requested
- [ ] Microphone permission requested
- [ ] Can switch front/back camera
- [ ] Portrait mode works
- [ ] Landscape mode works
- [ ] Video quality acceptable
- [ ] Audio quality acceptable
- [ ] No excessive battery drain
- [ ] No overheating

#### iOS-Specific Tests
- [ ] Call continues when app backgrounded
- [ ] Call continues when screen locked
- [ ] Notifications work during call
- [ ] Can use other apps during call (picture-in-picture)

### 4.2 Android Testing

#### Devices to Test
- [ ] Samsung Galaxy S21 or newer (Android 11+)
- [ ] Google Pixel 5 or newer (Android 11+)

#### Test Procedure
1. Open Chrome on Android device
2. Navigate to video room URL
3. Grant camera/microphone permissions
4. Join video call

**Verification**:
- [ ] Video works in Chrome
- [ ] Camera permission requested
- [ ] Microphone permission requested
- [ ] Can switch front/back camera
- [ ] Portrait mode works
- [ ] Landscape mode works
- [ ] Video quality acceptable
- [ ] Audio quality acceptable
- [ ] No excessive battery drain
- [ ] No overheating

#### Android-Specific Tests
- [ ] Call continues when app backgrounded
- [ ] Call continues when screen locked
- [ ] Notifications work during call
- [ ] Can use other apps during call (picture-in-picture)

---

## 5. Browser Compatibility Testing

### 5.1 Desktop Browsers

#### Chrome (Latest)
```bash
# Test on Chrome
# Open: chrome://webrtc-internals/ to view stats
```

**Verification**:
- [ ] Video/audio works
- [ ] Screen sharing works
- [ ] All features functional
- [ ] No console errors
- [ ] WebRTC stats available

#### Firefox (Latest)
```bash
# Test on Firefox
# Open: about:webrtc to view stats
```

**Verification**:
- [ ] Video/audio works
- [ ] Screen sharing works
- [ ] All features functional
- [ ] No console errors
- [ ] WebRTC stats available

#### Safari (Latest)
**Verification**:
- [ ] Video/audio works
- [ ] Screen sharing works (macOS 13+)
- [ ] All features functional
- [ ] No console errors

#### Edge (Latest)
**Verification**:
- [ ] Video/audio works
- [ ] Screen sharing works
- [ ] All features functional
- [ ] No console errors

### 5.2 Browser Permissions

#### Test Permission Prompts
1. First visit to video room
2. Browser requests camera permission
3. Browser requests microphone permission

**Verification**:
- [ ] Permission prompts appear
- [ ] Permissions can be granted
- [ ] Permissions can be denied
- [ ] Appropriate error shown if denied
- [ ] Permissions remembered for future visits
- [ ] Can revoke and re-grant permissions

---

## 6. Video Consultation Features

### 6.1 Mute/Unmute Audio

#### Test Procedure
1. Join video call
2. Click "Mute" button
3. Speak (other participant shouldn't hear)
4. Click "Unmute" button
5. Speak (other participant should hear)

**Verification**:
- [ ] Mute button visible
- [ ] Mute button toggles state
- [ ] Audio muted when button clicked
- [ ] Visual indicator shows muted state
- [ ] Audio unmuted when button clicked again
- [ ] Keyboard shortcut works (if implemented)

### 6.2 Enable/Disable Video

#### Test Procedure
1. Join video call
2. Click "Stop Video" button
3. Observe (other participant sees black screen or avatar)
4. Click "Start Video" button
5. Observe (other participant sees video again)

**Verification**:
- [ ] Video button visible
- [ ] Video button toggles state
- [ ] Video disabled when button clicked
- [ ] Visual indicator shows video off
- [ ] Video enabled when button clicked again
- [ ] Keyboard shortcut works (if implemented)

### 6.3 Chat Functionality (if implemented)

#### Test Procedure
1. Join video call
2. Open chat panel
3. Send text message
4. Other participant receives message
5. Other participant replies

**Verification**:
- [ ] Chat panel accessible
- [ ] Can send messages
- [ ] Messages received in real-time
- [ ] Message history preserved
- [ ] Timestamps shown
- [ ] Sender name shown

### 6.4 Medical Report Viewing

#### Test Procedure
1. Doctor joins video call
2. Doctor opens patient's medical report
3. Report displayed alongside video
4. Doctor can zoom/pan image
5. Patient can see what doctor is viewing (if screen shared)

**Verification**:
- [ ] Report accessible during call
- [ ] Report displays correctly
- [ ] Image quality sufficient for diagnosis
- [ ] Can zoom in on lesion
- [ ] AI predictions visible
- [ ] Patient symptoms visible

### 6.5 Consultation Notes

#### Test Procedure
1. Doctor joins video call
2. Doctor opens notes panel
3. Doctor types consultation notes during call
4. Notes auto-saved
5. Call ends
6. Notes persisted to medical report

**Verification**:
- [ ] Notes panel accessible
- [ ] Can type notes during call
- [ ] Notes auto-save (every 30 seconds)
- [ ] Notes persist after call ends
- [ ] Notes associated with correct report
- [ ] Timestamps recorded

### 6.6 End Call

#### Test Procedure
1. Join video call
2. Click "End Call" button
3. Confirm end call
4. Observe cleanup

**Verification**:
- [ ] End call button visible
- [ ] Confirmation prompt shown
- [ ] Call ends for both participants
- [ ] Video/audio streams stopped
- [ ] Resources cleaned up
- [ ] Redirect to appropriate page
- [ ] Call duration recorded

---

## 7. Video Encryption and Security

### 7.1 DTLS-SRTP Encryption

#### Verify Encryption
```javascript
// In browser console during call
const stats = await pc.getStats();
stats.forEach(report => {
  if (report.type === 'transport') {
    console.log('DTLS State:', report.dtlsState);
    console.log('SRTP Cipher:', report.srtpCipher);
    console.log('DTLS Cipher:', report.dtlsCipher);
  }
});
```

**Expected Output**:
```
DTLS State: connected
SRTP Cipher: AES_CM_128_HMAC_SHA1_80
DTLS Cipher: TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
```

**Verification**:
- [ ] DTLS state: connected
- [ ] SRTP cipher: AES-based
- [ ] DTLS cipher: strong (ECDHE, AES-GCM)
- [ ] No unencrypted fallback

### 7.2 HIPAA Compliance

**Checklist**:
- [ ] End-to-end encryption enabled
- [ ] No recording without consent
- [ ] Access logs maintained
- [ ] Session timeout configured (1 hour)
- [ ] Automatic disconnect after timeout
- [ ] No data stored on client devices
- [ ] Secure token generation
- [ ] Token expiration enforced

#### Verify No Recording
```bash
# Check Twilio room settings
curl -X GET "https://video.twilio.com/v1/Rooms/ROOM_SID" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"
```

**Expected**: `RecordParticipantsOnConnect: false`

### 7.3 Access Control

#### Test Unauthorized Access
```bash
# Try to access room without token
curl -X GET "https://skinguard.com/video/room-invalid-token"

# Try to access expired room
curl -X GET "https://skinguard.com/video/room-expired-token"

# Try to access another user's room
curl -X GET "https://skinguard.com/video/room-other-user-token" \
  -H "Authorization: Bearer $WRONG_USER_TOKEN"
```

**Verification**:
- [ ] Invalid token: HTTP 401 Unauthorized
- [ ] Expired token: HTTP 403 Forbidden
- [ ] Wrong user: HTTP 403 Forbidden
- [ ] Appropriate error messages shown

---

## 8. Performance and Load Testing

### 8.1 Concurrent Calls Test

#### Test Procedure
```bash
# Create 10 concurrent video rooms
for i in {1..10}; do
  curl -X POST https://api.skinguard.com/api/appointments \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"doctor_id\": \"DOCTOR_UUID\",
      \"scheduled_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
      \"consultation_type\": \"video\"
    }" &
done

wait

# Join all rooms simultaneously (manual test with multiple browsers)
```

**Verification**:
- [ ] All rooms created successfully
- [ ] All calls connect successfully
- [ ] No degradation in quality
- [ ] Server handles load
- [ ] No errors in logs

### 8.2 Long Duration Test

#### Test Procedure
1. Start video call
2. Let call run for 1 hour
3. Monitor quality throughout
4. End call

**Verification**:
- [ ] Call remains stable for 1 hour
- [ ] No quality degradation over time
- [ ] No memory leaks
- [ ] No connection drops
- [ ] Bandwidth usage consistent

### 8.3 Bandwidth Usage

#### Measure Bandwidth
```javascript
// In browser console
const stats = await pc.getStats();
stats.forEach(report => {
  if (report.type === 'candidate-pair' && report.state === 'succeeded') {
    console.log('Bytes Sent:', report.bytesSent);
    console.log('Bytes Received:', report.bytesReceived);
  }
});
```

**Expected Bandwidth**:
- Video (720p): 1-2 Mbps
- Audio: 50-100 Kbps
- Total: ~2 Mbps per participant

**Verification**:
- [ ] Bandwidth usage within expected range
- [ ] No excessive bandwidth consumption
- [ ] Adapts to available bandwidth

---

## 9. Error Handling and Recovery

### 9.1 Connection Failure

#### Test Procedure
1. Start video call
2. Disconnect network
3. Wait 10 seconds
4. Reconnect network

**Verification**:
- [ ] "Connection lost" message shown
- [ ] Automatic reconnection attempted
- [ ] Call resumes after reconnection
- [ ] No data loss
- [ ] User notified of reconnection

### 9.2 Camera/Microphone Failure

#### Test Procedure
1. Start video call
2. Disconnect camera (unplug USB)
3. Observe error handling
4. Reconnect camera

**Verification**:
- [ ] Error message shown
- [ ] Call continues (audio only)
- [ ] Can reconnect camera
- [ ] Video resumes when camera reconnected

### 9.3 Browser Crash Recovery

#### Test Procedure
1. Start video call
2. Force close browser
3. Reopen browser
4. Navigate back to video room

**Verification**:
- [ ] Can rejoin call
- [ ] Call state recovered
- [ ] Other participant notified of disconnect/reconnect

---

## 10. Monitoring and Logging

### 10.1 Call Quality Metrics

**Metrics to Collect**:
- [ ] Call duration
- [ ] Video resolution
- [ ] Frame rate
- [ ] Packet loss
- [ ] Jitter
- [ ] Round-trip time (RTT)
- [ ] Bandwidth usage

**Access Metrics**:
```bash
# Get call statistics
curl https://api.skinguard.com/api/admin/video-stats/APPOINTMENT_ID \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 10.2 Call Logs

```bash
# View recent video calls
curl https://api.skinguard.com/api/admin/video-logs?limit=100 \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Search call logs
curl "https://api.skinguard.com/api/admin/video-logs?appointment_id=APPOINTMENT_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Log Fields**:
- Appointment ID
- Participants (patient, doctor)
- Start time
- End time
- Duration
- Quality metrics
- Errors/issues

### 10.3 Alerts

**Configure Alerts**:
- [ ] Failed call attempts
- [ ] Poor call quality (packet loss >5%)
- [ ] Call duration >2 hours (unusual)
- [ ] High error rate

---

## 11. Production Testing Checklist

### 11.1 Pre-Launch
- [ ] Video service configured (Twilio/Agora)
- [ ] Room creation tested
- [ ] Access control working
- [ ] Video quality acceptable (720p, 24fps)
- [ ] Audio quality acceptable
- [ ] Screen sharing working
- [ ] Mobile devices tested (iOS, Android)
- [ ] All browsers tested (Chrome, Firefox, Safari, Edge)
- [ ] Encryption verified (DTLS-SRTP)
- [ ] HIPAA compliance verified
- [ ] Error handling tested
- [ ] Monitoring configured

### 11.2 Post-Launch (First Week)
- [ ] Monitor call success rate
- [ ] Monitor call quality metrics
- [ ] Review user feedback
- [ ] Check for errors in logs
- [ ] Verify encryption on all calls
- [ ] Test on new devices/browsers as needed

---

**Tested By**: _________________  
**Date**: _________________  
**Call Success Rate**: _________________  
**Average Call Quality**: _________________  
**Issues Found**: _________________
