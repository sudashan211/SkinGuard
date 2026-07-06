# Phase 9: Frontend Foundation - Setup Guide

**Phase**: 9 of 18  
**Status**: Ready to Start  
**Backend Progress**: 92% Complete  
**Frontend Progress**: 0% (Starting Now)

---

## Overview

Phase 9 marks the beginning of frontend development for SkinGuard. We'll set up a modern React application with TypeScript, Vite, and all necessary dependencies for building the patient, doctor, and admin interfaces.

---

## Phase 9 Tasks

### Task 21: Frontend Project Setup

#### 21.1 Initialize React + Vite Project with TypeScript
- Set up Vite configuration
- Install dependencies (React Query, Zustand, Tailwind CSS, Framer Motion, React Dropzone, Google Maps React)
- Configure TypeScript strict mode
- Set up ESLint and Prettier
- **Requirements**: 11.1

#### 21.2 Set up Supabase Client
- Install Supabase JS client
- Configure authentication
- Create API service layer for all backend endpoints
- **Requirements**: 1.2

#### 21.3 Implement Routing and Layout
- Set up React Router with protected routes
- Create main layout component
- Implement role-based route guards
- **Requirements**: 1.4, 1.5, 1.6

### Task 22: Authentication UI

#### 22.1 Create Login and Signup Forms
- Build LoginForm component
- Build SignupForm component with role selection
- Implement form validation
- Connect to authentication API
- **Requirements**: 1.1, 1.2

#### 22.2 Implement Authentication Context
- Create AuthProvider with Zustand
- Implement login, logout, session management
- Create ProtectedRoute component
- **Requirements**: 1.2

#### 22.3 Create Landing Page with Carousel
- Build carousel component with Framer Motion
- Create 3 slides: AI Screening, Find Doctors, Secure History
- Add smooth transitions
- Add authentication buttons
- **Requirements**: 11.1, 11.2

---

## Technology Stack

### Core Framework
- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server

### State Management
- **Zustand**: Lightweight state management
- **React Query (TanStack Query)**: Server state management

### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library

### Routing
- **React Router v6**: Client-side routing

### Forms
- **React Hook Form**: Form management
- **Zod**: Schema validation

### UI Components
- **React Dropzone**: File uploads
- **@react-google-maps/api**: Google Maps integration
- **Lucide React**: Icon library

### Backend Integration
- **Supabase JS Client**: Database and auth
- **Axios**: HTTP client

---

## Step-by-Step Setup

### Step 1: Create Vite Project

```bash
# Create new Vite project with React + TypeScript
npm create vite@latest frontend -- --template react-ts

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Step 2: Install Core Dependencies

```bash
# State management and data fetching
npm install zustand @tanstack/react-query

# Routing
npm install react-router-dom

# Styling and animations
npm install -D tailwindcss postcss autoprefixer
npm install framer-motion

# Forms and validation
npm install react-hook-form zod @hookform/resolvers

# UI components
npm install react-dropzone lucide-react

# Backend integration
npm install @supabase/supabase-js axios

# Google Maps
npm install @react-google-maps/api

# Utilities
npm install date-fns clsx
```

### Step 3: Install Dev Dependencies

```bash
# TypeScript types
npm install -D @types/node

# Linting and formatting
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier eslint-plugin-prettier

# Testing (optional for now)
npm install -D vitest @testing-library/react @testing-library/jest-dom
npm install -D @testing-library/user-event jsdom
```

### Step 4: Configure Tailwind CSS

```bash
# Initialize Tailwind
npx tailwindcss init -p
```

Update `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
    },
  },
  plugins: [],
}
```

Update `src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-900;
  }
}
```

### Step 5: Configure TypeScript

Update `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### Step 6: Configure Vite

Update `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### Step 7: Set Up ESLint

Create `.eslintrc.cjs`:

```javascript
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'prettier',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
  },
}
```

### Step 8: Set Up Prettier

Create `.prettierrc`:

```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80,
  "arrowParens": "avoid"
}
```

### Step 9: Create Project Structure

```bash
# Create directory structure
mkdir -p src/{components,pages,hooks,services,store,types,utils,layouts}
mkdir -p src/components/{auth,common,patient,doctor,admin}
```

Project structure:

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── auth/          # Login, Signup, ProtectedRoute
│   │   ├── common/        # Shared components (Button, Input, etc.)
│   │   ├── patient/       # Patient-specific components
│   │   ├── doctor/        # Doctor-specific components
│   │   └── admin/         # Admin-specific components
│   ├── pages/
│   │   ├── LandingPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── SignupPage.tsx
│   │   ├── PatientDashboard.tsx
│   │   ├── DoctorDashboard.tsx
│   │   └── AdminDashboard.tsx
│   ├── layouts/
│   │   ├── MainLayout.tsx
│   │   ├── AuthLayout.tsx
│   │   └── DashboardLayout.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   └── useToast.ts
│   ├── services/
│   │   ├── api.ts         # Axios instance
│   │   ├── auth.ts        # Auth API calls
│   │   ├── patient.ts     # Patient API calls
│   │   ├── doctor.ts      # Doctor API calls
│   │   └── supabase.ts    # Supabase client
│   ├── store/
│   │   ├── authStore.ts   # Auth state (Zustand)
│   │   └── uiStore.ts     # UI state (Zustand)
│   ├── types/
│   │   ├── auth.ts
│   │   ├── patient.ts
│   │   ├── doctor.ts
│   │   └── api.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   ├── validators.ts
│   │   └── helpers.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── .env
├── .env.example
├── .eslintrc.cjs
├── .prettierrc
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

### Step 10: Create Environment Variables

Create `.env`:

```env
# Backend API
VITE_API_URL=http://localhost:8000

# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key

# Google Maps
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

Create `.env.example`:

```env
# Backend API
VITE_API_URL=http://localhost:8000

# Supabase
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=

# Google Maps
VITE_GOOGLE_MAPS_API_KEY=
```

---

## Initial Implementation

### 1. Supabase Client Setup

Create `src/services/supabase.ts`:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### 2. API Client Setup

Create `src/services/api.ts`:

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Token expired, try to refresh
      // Implement refresh logic here
    }
    return Promise.reject(error)
  }
)

export default api
```

### 3. Auth Store

Create `src/store/authStore.ts`:

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  role: 'patient' | 'doctor' | 'admin'
  verified?: boolean
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (user: User, accessToken: string, refreshToken: string) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      login: (user, accessToken, refreshToken) =>
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
        }),
      logout: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        }),
      updateUser: (userData) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null,
        })),
    }),
    {
      name: 'auth-storage',
    }
  )
)
```

### 4. React Query Setup

Create `src/main.tsx`:

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
)
```

### 5. Router Setup

Create `src/App.tsx`:

```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Pages (to be created)
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import PatientDashboard from './pages/PatientDashboard'
import DoctorDashboard from './pages/DoctorDashboard'
import AdminDashboard from './pages/AdminDashboard'

// Protected Route Component
const ProtectedRoute = ({ 
  children, 
  allowedRoles 
}: { 
  children: React.ReactNode
  allowedRoles: string[]
}) => {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Patient routes */}
        <Route
          path="/patient/*"
          element={
            <ProtectedRoute allowedRoles={['patient']}>
              <PatientDashboard />
            </ProtectedRoute>
          }
        />

        {/* Doctor routes */}
        <Route
          path="/doctor/*"
          element={
            <ProtectedRoute allowedRoles={['doctor']}>
              <DoctorDashboard />
            </ProtectedRoute>
          }
        />

        {/* Admin routes */}
        <Route
          path="/admin/*"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        {/* 404 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

---

## Running the Frontend

### Development Server

```bash
# Start frontend dev server
npm run dev

# Frontend will be available at http://localhost:3000
```

### Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

### Linting and Formatting

```bash
# Run ESLint
npm run lint

# Format code with Prettier
npm run format
```

---

## Next Steps After Setup

Once the frontend foundation is set up, you'll implement:

1. **Task 21.1**: Complete Vite configuration and dependencies ✓
2. **Task 21.2**: Set up Supabase client and API service layer ✓
3. **Task 21.3**: Implement routing and layout components
4. **Task 22.1**: Create login and signup forms
5. **Task 22.2**: Implement authentication context
6. **Task 22.3**: Create landing page with carousel

---

## Verification Checklist

After setup, verify:

- [ ] Vite dev server starts without errors
- [ ] TypeScript compilation works
- [ ] Tailwind CSS is working
- [ ] ESLint runs without errors
- [ ] Prettier formats code correctly
- [ ] Environment variables are loaded
- [ ] Supabase client connects
- [ ] API client is configured
- [ ] Auth store persists data
- [ ] React Query is set up
- [ ] Router navigation works

---

## Useful Commands

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Format code
npm run format

# Type check
npm run type-check

# Run tests (when implemented)
npm run test
```

---

## Resources

### Documentation
- [Vite](https://vitejs.dev/)
- [React](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Router](https://reactrouter.com/)
- [Zustand](https://github.com/pmndrs/zustand)
- [React Query](https://tanstack.com/query/latest)
- [Supabase JS](https://supabase.com/docs/reference/javascript)

### Design Resources
- [Tailwind UI](https://tailwindui.com/)
- [Headless UI](https://headlessui.com/)
- [Lucide Icons](https://lucide.dev/)
- [Framer Motion](https://www.framer.com/motion/)

---

**Phase 9 Setup Guide Version**: 1.0  
**Last Updated**: February 12, 2026  
**Status**: Ready to Begin Frontend Development
