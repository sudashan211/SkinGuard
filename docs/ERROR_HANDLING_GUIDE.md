# Error Handling and User Experience Guide

## Overview

This document describes the comprehensive error handling and user experience improvements implemented in Task 35 of the SkinGuard platform.

**Requirements Addressed:**
- **13.4**: Comprehensive error handling with appropriate HTTP status codes
- **13.5**: JSON response format for structured data
- **11.4**: Loading states and visual feedback

## Components Implemented

### 1. Backend Error Handling

#### Custom Exception Classes (`backend/app/exceptions.py`)

Structured exception hierarchy for consistent error handling:

- `SkinGuardException` - Base exception class
- `ValidationError` - HTTP 400 for invalid input
- `AuthenticationError` - HTTP 401 for auth failures
- `AuthorizationError` - HTTP 403 for permission denied
- `ContentViolationError` - HTTP 403 for NSFW content
- `NotFoundError` - HTTP 404 for missing resources
- `ConflictError` - HTTP 409 for duplicate resources
- `RateLimitError` - HTTP 429 for rate limiting
- `ImageQualityError` - HTTP 400 for poor image quality
- `AIProcessingError` - HTTP 500 for AI failures
- `DatabaseError` - HTTP 500 for database issues
- `ExternalServiceError` - HTTP 503 for service unavailability
- `StorageError` - HTTP 500 for storage failures

#### Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "User-friendly error message",
    "details": {},
    "timestamp": "2024-01-01T00:00:00.000000",
    "request_id": "uuid-here"
  }
}
```

#### HTTP Status Code Mapping

- **400** - Validation errors, bad requests
- **401** - Authentication required
- **403** - Permission denied, content violations
- **404** - Resource not found
- **409** - Resource conflict
- **422** - Unprocessable entity (validation)
- **429** - Rate limit exceeded
- **500** - Internal server error
- **503** - Service unavailable

### 2. Frontend Error Handling

#### Error Boundary Component (`frontend/src/components/common/ErrorBoundary.tsx`)

React error boundary that catches JavaScript errors in component tree:

- Displays user-friendly error message
- Provides "Try Again" and "Go Home" actions
- Shows error details in development mode
- Logs errors for debugging

**Usage:**
```tsx
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

#### Toast Notifications (`frontend/src/components/common/ToastContainer.tsx`)

Animated toast notifications for user feedback:

- **Success** - Green toast for successful operations
- **Error** - Red toast for errors
- **Warning** - Yellow toast for warnings
- **Info** - Blue toast for information

**Usage:**
```tsx
const toast = useToast()

toast.success('Operation completed!')
toast.error('Something went wrong')
toast.warning('Please review your input')
toast.info('Processing your request...')
```

#### Loading States

**LoadingSpinner** (`frontend/src/components/common/LoadingSpinner.tsx`)
- Animated spinner with customizable size and color
- Optional loading text
- Variants: inline, full-page

**ProgressIndicator** (`frontend/src/components/common/ProgressIndicator.tsx`)
- Linear progress bar for uploads
- Circular progress indicator
- Upload-specific progress with status

**Usage:**
```tsx
<LoadingSpinner size="lg" text="Loading..." />
<ProgressIndicator progress={75} label="Uploading..." />
<UploadProgress fileName="image.jpg" progress={50} status="uploading" />
```

#### Retry Logic (`frontend/src/utils/errorHandling.ts`)

Automatic retry for transient failures:

```typescript
const data = await withRetry(
  () => apiCall(),
  {
    maxRetries: 3,
    retryDelay: 1000,
    retryableStatuses: [408, 429, 500, 502, 503, 504],
    onRetry: (attempt) => {
      console.log(`Retry attempt ${attempt}`)
    }
  }
)
```

**Features:**
- Exponential backoff
- Configurable retry count
- Retryable status codes
- Retry callbacks

#### Error Message Extraction

User-friendly error messages from API responses:

```typescript
import { getErrorMessage, getErrorCode } from '@/utils/errorHandling'

const message = getErrorMessage(error)
const code = getErrorCode(error)
```

### 3. Property-Based Tests

#### Error Response Tests (`tests/property/test_error_response_properties.py`)

**Property 35: HTTP Status Code Correctness**
- Tests authentication errors return 401
- Tests validation errors return 400/422
- Tests not found errors return 404
- Tests content violations return 403

**Property 36: JSON Response Format**
- Tests all responses have JSON content-type
- Tests response bodies are valid JSON
- Tests error responses have proper structure

## User Experience Improvements

### Upload Flow

1. **Image Selection**
   - Drag-and-drop with visual feedback
   - File validation with clear error messages
   - Image preview before upload

2. **Upload Progress**
   - Real-time progress indicator
   - Status updates (uploading → processing → complete)
   - File name and progress percentage

3. **Analysis Feedback**
   - Loading spinner during AI processing
   - Status messages for each stage
   - Retry attempts with user notification

4. **Error Handling**
   - Clear error messages
   - Automatic retry for transient failures
   - Option to try again or go back

### Error Messages

All error messages are:
- **User-friendly** - No technical jargon
- **Actionable** - Tell users what to do next
- **Specific** - Explain what went wrong
- **Translated** - Support multiple languages

### Loading States

Every async operation shows:
- **Loading indicator** - Visual feedback
- **Progress** - For long operations
- **Status text** - What's happening
- **Cancellation** - Where appropriate

## Testing

### Running Property Tests

```bash
# Run all error handling tests
python -m pytest tests/property/test_error_response_properties.py -v

# Run specific test
python -m pytest tests/property/test_error_response_properties.py::test_property_35_authentication_error_status_code -v
```

### Manual Testing

1. **Test Error Boundary**
   - Trigger a JavaScript error in a component
   - Verify error boundary catches it
   - Verify fallback UI displays

2. **Test Toast Notifications**
   - Trigger success, error, warning, info toasts
   - Verify animations work
   - Verify auto-dismiss works

3. **Test Loading States**
   - Upload an image
   - Verify progress indicator shows
   - Verify status updates correctly

4. **Test Retry Logic**
   - Simulate network failure
   - Verify automatic retry
   - Verify retry count displayed

## Best Practices

### Backend

1. **Use Custom Exceptions**
   ```python
   from app.exceptions import ValidationError
   
   if age < 1 or age > 120:
       raise ValidationError("Age must be between 1 and 120")
   ```

2. **Return Consistent Errors**
   ```python
   from app.exceptions import error_response
   
   return JSONResponse(
       status_code=400,
       content=error_response("VALIDATION_ERROR", "Invalid input")
   )
   ```

### Frontend

1. **Wrap Components in Error Boundary**
   ```tsx
   <ErrorBoundary fallback={<CustomError />}>
     <MyComponent />
   </ErrorBoundary>
   ```

2. **Show Loading States**
   ```tsx
   {isLoading && <LoadingSpinner text="Loading..." />}
   {!isLoading && <Content />}
   ```

3. **Use Toast for Feedback**
   ```tsx
   const toast = useToast()
   
   try {
     await saveData()
     toast.success('Saved successfully!')
   } catch (error) {
     toast.error('Failed to save')
   }
   ```

4. **Implement Retry Logic**
   ```tsx
   const data = await withRetry(
     () => fetchData(),
     { maxRetries: 3 }
   )
   ```

## Internationalization

All error messages support i18n:

```json
{
  "error": {
    "boundary": {
      "title": "Something went wrong",
      "message": "We encountered an unexpected error...",
      "retry": "Try Again",
      "home": "Go Home"
    }
  }
}
```

## Future Improvements

1. **Error Tracking Service**
   - Integrate Sentry or similar
   - Automatic error reporting
   - Error analytics

2. **Offline Support**
   - Queue failed requests
   - Retry when online
   - Offline indicators

3. **Advanced Retry**
   - Circuit breaker pattern
   - Adaptive retry delays
   - Request deduplication

4. **Enhanced Feedback**
   - Skeleton screens
   - Optimistic updates
   - Background sync

## Conclusion

The comprehensive error handling system provides:
- ✅ Consistent error responses
- ✅ User-friendly error messages
- ✅ Automatic retry for transient failures
- ✅ Visual feedback for all operations
- ✅ Proper HTTP status codes
- ✅ JSON response format
- ✅ Property-based tests

This ensures a robust and user-friendly experience throughout the SkinGuard platform.
