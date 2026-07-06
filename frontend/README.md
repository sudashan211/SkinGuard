# SkinGuard Frontend

React + TypeScript + Vite frontend for the SkinGuard AI Skin Cancer Screening Platform.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Query** - Server state management
- **React Router** - Routing
- **Framer Motion** - Animations
- **Axios** - HTTP client
- **Supabase** - Backend integration

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`
- Supabase project (optional, for full functionality)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
# VITE_API_URL=http://localhost:8000
# VITE_SUPABASE_URL=your-supabase-url
# VITE_SUPABASE_ANON_KEY=your-supabase-key
# VITE_GOOGLE_MAPS_API_KEY=your-google-maps-key
```

### Development

```bash
# Start dev server (runs on http://localhost:3000)
npm run dev

# Type check
npm run type-check

# Lint code
npm run lint

# Format code
npm run format
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/       # React components
│   ├── auth/        # Authentication components
│   ├── common/      # Shared components
│   ├── patient/     # Patient-specific components
│   ├── doctor/      # Doctor-specific components
│   └── admin/       # Admin-specific components
├── pages/           # Page components
├── layouts/         # Layout components
├── hooks/           # Custom React hooks
├── services/        # API services
│   ├── api.ts      # Axios instance
│   ├── auth.ts     # Auth API calls
│   └── supabase.ts # Supabase client
├── store/           # Zustand stores
│   ├── authStore.ts # Authentication state
│   └── uiStore.ts   # UI state (toasts, sidebar)
├── types/           # TypeScript types
├── utils/           # Utility functions
│   ├── constants.ts # App constants
│   └── helpers.ts   # Helper functions
├── App.tsx          # Main app component
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## Features Implemented

### Phase 9: Frontend Foundation ✅

- ✅ Task 21.1: React + Vite + TypeScript setup
  - Vite configuration
  - All dependencies installed
  - TypeScript strict mode
  - ESLint and Prettier configured

- ✅ Task 21.2: Supabase client setup
  - Supabase JS client configured
  - API service layer with Axios
  - Request/response interceptors
  - Token refresh logic

- ✅ Task 21.3: Routing and layout
  - React Router with protected routes
  - MainLayout for public pages
  - AuthLayout for login/signup
  - DashboardLayout for authenticated pages
  - Role-based route guards

### Authentication

- Login page with form validation
- Signup page with role selection
- Protected routes by role (patient, doctor, admin)
- JWT token management
- Auto token refresh
- Persistent auth state with Zustand

### UI Components

- Landing page with hero and features
- Login and signup forms
- Dashboard layouts for all roles
- Responsive sidebar navigation
- Toast notifications system

## Environment Variables

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# Supabase Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Google Maps API Key
VITE_GOOGLE_MAPS_API_KEY=your-api-key
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run type-check` - Run TypeScript type checking

## API Integration

The frontend connects to the backend API at `http://localhost:8000` by default.

### Authentication Flow

1. User submits login/signup form
2. Request sent to `/api/auth/login` or `/api/auth/signup`
3. Backend returns user data and JWT tokens
4. Tokens stored in localStorage and Zustand store
5. Axios interceptor adds token to all requests
6. Token auto-refreshes on 401 errors

### API Service

```typescript
import api from '@/services/api'

// All requests automatically include auth token
const response = await api.get('/api/reports')
```

## State Management

### Auth Store (Zustand)

```typescript
import { useAuthStore } from '@/store/authStore'

const { user, isAuthenticated, login, logout } = useAuthStore()
```

### UI Store (Zustand)

```typescript
import { useUIStore } from '@/store/uiStore'

const { addToast, isSidebarOpen, toggleSidebar } = useUIStore()
```

## Custom Hooks

### useAuth

```typescript
import { useAuth } from '@/hooks/useAuth'

const { user, isAuthenticated, login, signup, logout } = useAuth()
```

### useToast

```typescript
import { useToast } from '@/hooks/useToast'

const toast = useToast()
toast.success('Operation successful!')
toast.error('Something went wrong')
```

## Styling

Uses Tailwind CSS with custom configuration:

- Primary color: Blue (customizable in `tailwind.config.js`)
- Utility classes for common patterns
- Responsive design with mobile-first approach
- Custom component classes (btn, input, card)

## Next Steps

### Phase 10: Patient Dashboard UI
- Diagnostic uploader component
- Symptom wizard component
- Results display component
- Report history component

### Phase 11: Doctor Locator UI
- Google Maps integration
- Doctor markers and cards
- Appointment booking modal

### Phase 12: Doctor and Admin Dashboards
- Pending reports view
- Report detail view
- Admin verification interface
- Analytics dashboard

## Troubleshooting

### Port already in use

```bash
# Change port in vite.config.ts or use:
npm run dev -- --port 3001
```

### API connection issues

- Ensure backend is running on `http://localhost:8000`
- Check CORS configuration in backend
- Verify `VITE_API_URL` in `.env`

### Build errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Contributing

1. Follow the existing code structure
2. Use TypeScript for all new files
3. Follow ESLint and Prettier rules
4. Test on multiple screen sizes
5. Ensure accessibility compliance

## License

Copyright © 2026 SkinGuard. All rights reserved.
