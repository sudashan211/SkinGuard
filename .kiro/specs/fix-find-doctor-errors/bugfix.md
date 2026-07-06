# Bugfix Requirements Document

## Introduction

The Find Doctor feature (doctor map) is currently failing with three distinct errors that prevent users from viewing nearby doctors. The feature crashes with a 500 Internal Server Error when the `/api/doctors/nearby` endpoint is called, Google Maps fails to load due to an invalid API key configuration, and some doctor-related endpoints return 401 Unauthorized errors. This bugfix addresses all three issues to restore full functionality to the doctor directory feature.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the `/api/doctors/nearby` endpoint is called with valid coordinates AND no doctors exist in the database THEN the system crashes with a 500 Internal Server Error due to attempting to access attributes on None values from the doctor records

1.2 WHEN the DoctorMap component loads AND the `VITE_GOOGLE_MAPS_API_KEY` environment variable is not set or is empty THEN the system displays "InvalidKeyMapError" and Google Maps fails to load

1.3 WHEN users access authenticated doctor endpoints (such as `/api/doctors/register` or `/api/doctors/reports/pending`) without proper authentication THEN the system returns 401 Unauthorized errors

### Expected Behavior (Correct)

2.1 WHEN the `/api/doctors/nearby` endpoint is called with valid coordinates AND no doctors exist in the database THEN the system SHALL return an empty array `[]` with HTTP 200 status without crashing

2.2 WHEN the DoctorMap component loads AND the `VITE_GOOGLE_MAPS_API_KEY` environment variable is not set or is empty THEN the system SHALL display a user-friendly error message instructing users to configure the Google Maps API key

2.3 WHEN users access authenticated doctor endpoints without proper authentication THEN the system SHALL return 401 Unauthorized with a clear error message indicating authentication is required

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the `/api/doctors/nearby` endpoint is called with valid coordinates AND verified doctors exist within the specified radius THEN the system SHALL CONTINUE TO return the list of nearby doctors with their details (clinic name, location, rating, etc.)

3.2 WHEN the DoctorMap component loads AND the `VITE_GOOGLE_MAPS_API_KEY` is properly configured THEN the system SHALL CONTINUE TO display the Google Maps interface with doctor markers and user location

3.3 WHEN authenticated doctor users access protected endpoints with valid credentials THEN the system SHALL CONTINUE TO allow access and return the requested data

3.4 WHEN users interact with doctor markers on the map THEN the system SHALL CONTINUE TO display doctor information in info windows with WhatsApp contact and appointment booking options

3.5 WHEN users request their geolocation AND geolocation is available THEN the system SHALL CONTINUE TO center the map on the user's location and fetch nearby doctors
