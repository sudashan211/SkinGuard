# Google Maps Integration Setup

This document explains how to set up and use the Google Maps integration for the Doctor Locator feature.

## Prerequisites

1. **Google Cloud Platform Account**: You need a Google Cloud Platform account to create a Google Maps API key.

## Setup Instructions

### 1. Create a Google Maps API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Maps JavaScript API
   - Geocoding API (optional, for address lookup)
4. Go to "Credentials" and create an API key
5. Restrict the API key (recommended):
   - Set application restrictions (HTTP referrers for web)
   - Set API restrictions (only enable Maps JavaScript API)

### 2. Configure Environment Variables

Add your Google Maps API key to the `.env` file:

```bash
VITE_GOOGLE_MAPS_API_KEY=your_api_key_here
```

**Important**: Never commit your API key to version control. The `.env` file should be in `.gitignore`.

### 3. Test the Integration

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Navigate to the Doctor Locator page at `/patient/doctors`

3. Allow location access when prompted by your browser

4. The map should load and display:
   - Your current location (blue circle)
   - Nearby verified doctors (red medical markers)

## Features

### User Location Detection

The map automatically detects the user's location using the browser's Geolocation API:

- **Desktop**: Uses IP-based location or browser location services
- **Mobile**: Uses GPS for accurate positioning
- **Fallback**: If location access is denied, shows a default location

### Doctor Markers

- Red medical cross markers indicate verified doctor locations
- Click on a marker to view doctor details
- Markers are placed at exact coordinates from the database

### Info Windows

When you click a doctor marker, an info window displays:

- Clinic name
- Doctor name
- Specialization
- Rating and review count
- WhatsApp contact button

### WhatsApp Integration

The "Contact on WhatsApp" button:

- Opens WhatsApp with a pre-filled message
- Message: "I would like to share my Derman Report"
- Works on both mobile and desktop (WhatsApp Web)

### GPS Centering

The navigation button (top-right) centers the map on your current location.

## Component Structure

```
frontend/src/
├── components/patient/
│   └── DoctorMap.tsx          # Main map component
├── pages/
│   └── DoctorLocatorPage.tsx  # Doctor locator page
├── services/
│   └── doctor.ts              # Doctor API service
└── types/
    └── doctor.ts              # Doctor type definitions
```

## API Integration

The map fetches nearby doctors from the backend API:

```typescript
GET /api/doctors/nearby?lat={latitude}&lng={longitude}&radius={radius_km}
```

Response:
```json
[
  {
    "id": "uuid",
    "clinicName": "Skin Care Clinic",
    "lat": 40.7128,
    "lng": -74.0060,
    "whatsappNo": "1234567890",
    "averageRating": 4.5,
    "reviewCount": 120,
    "verified": true,
    "fullName": "John Doe",
    "specialization": "Dermatology"
  }
]
```

## Troubleshooting

### Map Not Loading

1. **Check API Key**: Ensure `VITE_GOOGLE_MAPS_API_KEY` is set in `.env`
2. **Check Browser Console**: Look for API key errors
3. **Verify API Restrictions**: Make sure Maps JavaScript API is enabled
4. **Check Billing**: Google Maps requires billing to be enabled (free tier available)

### Location Not Detected

1. **Browser Permissions**: Check if location access is allowed
2. **HTTPS Required**: Geolocation API requires HTTPS (except localhost)
3. **Fallback**: The map will use a default location if geolocation fails

### No Doctors Showing

1. **Check Backend**: Ensure the backend API is running
2. **Verify Database**: Check if there are verified doctors in the database
3. **Check Radius**: Try increasing the search radius (default: 50km)
4. **Check Console**: Look for API errors in the browser console

## Mobile Considerations

### GPS Accuracy

- Mobile devices provide more accurate GPS coordinates
- The map automatically uses high-accuracy mode
- May take a few seconds to get precise location

### Touch Interactions

- Pinch to zoom
- Drag to pan
- Tap markers to view details
- Tap info window to close

### Performance

- Map loads asynchronously to avoid blocking UI
- Markers are rendered efficiently
- Info windows are created on-demand

## Security Best Practices

1. **API Key Restrictions**: Always restrict your API key to specific domains
2. **Environment Variables**: Never commit API keys to version control
3. **Rate Limiting**: Google Maps has usage limits; monitor your usage
4. **HTTPS**: Always use HTTPS in production for geolocation

## Cost Considerations

Google Maps offers a free tier:

- $200 monthly credit
- Maps JavaScript API: $7 per 1,000 loads
- Most small to medium applications stay within free tier

Monitor usage in Google Cloud Console to avoid unexpected charges.

## Future Enhancements

Potential improvements for the doctor locator:

1. **Search by Address**: Allow users to search for doctors by address
2. **Filters**: Filter doctors by specialization, rating, availability
3. **Directions**: Integrate Google Maps directions
4. **Clustering**: Group nearby markers when zoomed out
5. **Street View**: Show clinic street view
6. **Appointment Booking**: Book appointments directly from the map

## References

- [Google Maps JavaScript API Documentation](https://developers.google.com/maps/documentation/javascript)
- [@react-google-maps/api Documentation](https://react-google-maps-api-docs.netlify.app/)
- [Geolocation API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API)
