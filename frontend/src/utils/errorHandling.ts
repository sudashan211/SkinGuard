/**
 * Error Handling Utilities
 * 
 * Provides utilities for handling API errors, retry logic, and user-friendly error messages.
 * 
 * Requirements: 13.4 - Comprehensive error handling with retry logic
 */

export interface APIError {
  code: string
  message: string
  details?: any
  timestamp?: string
  request_id?: string
}

export interface RetryConfig {
  maxRetries?: number
  retryDelay?: number
  retryableStatuses?: number[]
  onRetry?: (attempt: number, error: any) => void
}

/**
 * Default retry configuration
 */
const DEFAULT_RETRY_CONFIG: Required<RetryConfig> = {
  maxRetries: 3,
  retryDelay: 1000, // 1 second
  retryableStatuses: [408, 429, 500, 502, 503, 504], // Transient errors
  onRetry: () => {},
}

/**
 * Check if an error is retryable
 */
function isRetryableError(error: any, retryableStatuses: number[]): boolean {
  // Network errors (no response)
  if (!error.response) {
    return true
  }

  // Check if status code is retryable
  return retryableStatuses.includes(error.response.status)
}

/**
 * Sleep utility for retry delays
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Retry wrapper for async functions
 * 
 * Automatically retries failed requests with exponential backoff
 * for transient failures (network errors, 5xx errors, rate limits)
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  config: RetryConfig = {}
): Promise<T> {
  const { maxRetries, retryDelay, retryableStatuses, onRetry } = {
    ...DEFAULT_RETRY_CONFIG,
    ...config,
  }

  let lastError: any

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error

      // Don't retry if this is the last attempt
      if (attempt === maxRetries) {
        break
      }

      // Don't retry if error is not retryable
      if (!isRetryableError(error, retryableStatuses)) {
        break
      }

      // Calculate delay with exponential backoff
      const delay = retryDelay * Math.pow(2, attempt)

      // Call retry callback
      onRetry(attempt + 1, error)

      // Wait before retrying
      await sleep(delay)
    }
  }

  throw lastError
}

/**
 * Extract user-friendly error message from API error
 */
export function getErrorMessage(error: any): string {
  // Handle API error response
  if (error.response?.data?.error) {
    const apiError = error.response.data.error as APIError
    return apiError.message || 'An error occurred'
  }

  // Handle validation errors
  if (error.response?.status === 422) {
    return 'Invalid data provided. Please check your input.'
  }

  // Handle authentication errors
  if (error.response?.status === 401) {
    return 'Authentication required. Please log in.'
  }

  // Handle authorization errors
  if (error.response?.status === 403) {
    return 'You do not have permission to perform this action.'
  }

  // Handle not found errors
  if (error.response?.status === 404) {
    return 'The requested resource was not found.'
  }

  // Handle rate limit errors
  if (error.response?.status === 429) {
    return 'Too many requests. Please try again later.'
  }

  // Handle server errors
  if (error.response?.status >= 500) {
    return 'Server error. Please try again later.'
  }

  // Handle network errors
  if (error.message === 'Network Error' || !error.response) {
    return 'Network error. Please check your connection and try again.'
  }

  // Default error message
  return error.message || 'An unexpected error occurred'
}

/**
 * Get error code from API error
 */
export function getErrorCode(error: any): string {
  if (error.response?.data?.error?.code) {
    return error.response.data.error.code
  }
  return 'UNKNOWN_ERROR'
}

/**
 * Check if error is a specific type
 */
export function isErrorType(error: any, code: string): boolean {
  return getErrorCode(error) === code
}

/**
 * Format validation errors for display
 */
export function formatValidationErrors(error: any): string[] {
  if (error.response?.data?.error?.details) {
    const details = error.response.data.error.details
    if (Array.isArray(details)) {
      return details.map((detail: any) => {
        const field = detail.loc?.join('.') || 'field'
        return `${field}: ${detail.msg}`
      })
    }
  }
  return [getErrorMessage(error)]
}

/**
 * Error handler for React Query
 */
export function handleQueryError(error: any, toast?: any) {
  const message = getErrorMessage(error)
  console.error('Query error:', error)
  
  if (toast) {
    toast.error(message)
  }
  
  return message
}

/**
 * Error handler for mutations
 */
export function handleMutationError(error: any, toast?: any) {
  const message = getErrorMessage(error)
  console.error('Mutation error:', error)
  
  if (toast) {
    toast.error(message)
  }
  
  return message
}

/**
 * Check if error requires authentication
 */
export function requiresAuth(error: any): boolean {
  return error.response?.status === 401
}

/**
 * Check if error is a content violation
 */
export function isContentViolation(error: any): boolean {
  return error.response?.status === 403 && 
         getErrorCode(error) === 'CONTENT_VIOLATION'
}

/**
 * Log error to external service (placeholder)
 * TODO: Integrate with error tracking service (e.g., Sentry)
 */
export function logError(error: any, context?: Record<string, any>) {
  console.error('Error logged:', {
    error,
    context,
    timestamp: new Date().toISOString(),
  })
  
  // TODO: Send to error tracking service
  // Sentry.captureException(error, { extra: context })
}
