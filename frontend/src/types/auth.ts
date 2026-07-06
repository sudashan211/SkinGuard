export type UserRole = 'patient' | 'doctor' | 'admin'

export interface User {
  id: string
  email: string
  role: UserRole
  verified?: boolean
  created_at?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface SignupData {
  email: string
  password: string
  role: UserRole
  full_name: string
}

export interface AuthResponse {
  user: User
  tokens: AuthTokens
}
