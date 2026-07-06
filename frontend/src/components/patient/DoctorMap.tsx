import { useState, useCallback, useEffect } from 'react'
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api'
import { Phone, Star, Navigation, Calendar } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import type { Doctor } from '@/types/doctor'
import { doctorService } from '@/services/doctor'
import AppointmentBookingModal from './AppointmentBookingModal'

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''

// Libraries to load for Google Maps - must be defined outside component to prevent reinitialization
const libraries = ["places"] as const

// Default center (will be replaced by user location)
const DEFAULT_CENTER = {
  lat: 40.7128,
  lng: -74.006,
}

const MAP_CONTAINER_STYLE = {
  width: '100%',
  height: '600px',
}

const MAP_OPTIONS = {
  disableDefaultUI: false,
  zoomControl: true,
  mapTypeControl: false,
  streetViewControl: false,
  fullscreenControl: true,
}

interface DoctorMapProps {
  onDoctorSelect?: (doctor: Doctor) => void
  onDoctorsLoaded?: (doctors: Doctor[], location: { lat: number; lng: number }) => void
  onHospitalsLoaded?: (hospitals: any[], location: { lat: number; lng: number }) => void
  selectedDoctorId?: string
}

// Interface for Google Places hospital
interface GoogleHospital {
  place_id: string
  name: string
  vicinity: string
  geometry: {
    location: {
      lat: () => number
      lng: () => number
    }
  }
  rating?: number
  user_ratings_total?: number
  formatted_phone_number?: string
  opening_hours?: {
    open_now?: boolean
  }
}

// Mock hospital data generator - creates realistic hospitals around a location
const generateMockHospitals = (centerLat: number, centerLng: number): GoogleHospital[] => {
  const mockHospitals = [
    // Dermatology-specific facilities
    {
      name: "Advanced Dermatology & Skin Cancer Center",
      vicinity: "123 Medical Plaza, Downtown",
      rating: 4.8,
      user_ratings_total: 342,
      type: "dermatology"
    },
    {
      name: "SkinCare Specialists Clinic",
      vicinity: "456 Health Avenue, Medical District",
      rating: 4.7,
      user_ratings_total: 218,
      type: "dermatology"
    },
    {
      name: "Dermatology Associates Medical Group",
      vicinity: "789 Wellness Street, City Center",
      rating: 4.6,
      user_ratings_total: 167,
      type: "dermatology"
    },
    {
      name: "Cosmetic & Medical Dermatology Institute",
      vicinity: "321 Beauty Boulevard, Uptown",
      rating: 4.9,
      user_ratings_total: 289,
      type: "dermatology"
    },
    {
      name: "Skin Health Clinic",
      vicinity: "654 Care Lane, Midtown",
      rating: 4.5,
      user_ratings_total: 134,
      type: "dermatology"
    },
    // General hospitals with dermatology departments
    {
      name: "City General Hospital",
      vicinity: "100 Hospital Drive, Medical Center",
      rating: 4.4,
      user_ratings_total: 892,
      type: "hospital"
    },
    {
      name: "Memorial Medical Center",
      vicinity: "200 Memorial Way, Healthcare District",
      rating: 4.6,
      user_ratings_total: 1247,
      type: "hospital"
    },
    {
      name: "Regional Medical Hospital",
      vicinity: "300 Regional Road, Hospital Quarter",
      rating: 4.3,
      user_ratings_total: 678,
      type: "hospital"
    },
    {
      name: "University Medical Center",
      vicinity: "400 University Avenue, Campus Area",
      rating: 4.7,
      user_ratings_total: 1534,
      type: "hospital"
    },
    {
      name: "St. Mary's Hospital",
      vicinity: "500 Saint Mary's Street, Old Town",
      rating: 4.5,
      user_ratings_total: 923,
      type: "hospital"
    },
    {
      name: "Community Health Hospital",
      vicinity: "600 Community Circle, Suburban Area",
      rating: 4.2,
      user_ratings_total: 456,
      type: "hospital"
    },
    {
      name: "Central Medical Hospital",
      vicinity: "700 Central Boulevard, Business District",
      rating: 4.6,
      user_ratings_total: 1089,
      type: "hospital"
    }
  ]

  // Generate positions around the center location (within ~10km radius)
  return mockHospitals.map((hospital, index) => {
    // Create a circular distribution around center
    const angle = (index / mockHospitals.length) * 2 * Math.PI
    const distance = 0.05 + Math.random() * 0.1 // 5-15km roughly
    
    const lat = centerLat + distance * Math.cos(angle)
    const lng = centerLng + distance * Math.sin(angle)
    
    return {
      place_id: `mock_${index}_${Date.now()}`,
      name: hospital.name,
      vicinity: hospital.vicinity,
      geometry: {
        location: {
          lat: () => lat,
          lng: () => lng
        }
      },
      rating: hospital.rating,
      user_ratings_total: hospital.user_ratings_total,
      formatted_phone_number: `+1 (555) ${String(Math.floor(Math.random() * 900) + 100)}-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      opening_hours: {
        open_now: Math.random() > 0.2 // 80% chance of being open
      }
    }
  })
}

export default function DoctorMap({ onDoctorSelect, onDoctorsLoaded, onHospitalsLoaded, selectedDoctorId }: DoctorMapProps) {
  const [map, setMap] = useState<google.maps.Map | null>(null)
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [googleHospitals, setGoogleHospitals] = useState<GoogleHospital[]>([])
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null)
  const [selectedHospital, setSelectedHospital] = useState<GoogleHospital | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [locationError, setLocationError] = useState<string | null>(null)
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false)
  const [doctorToBook, setDoctorToBook] = useState<Doctor | null>(null)

  // Validate API key before attempting to load Google Maps
  if (!GOOGLE_MAPS_API_KEY || GOOGLE_MAPS_API_KEY.trim() === '') {
    return (
      <div className="flex items-center justify-center h-96 bg-yellow-50 rounded-lg border-2 border-yellow-200">
        <div className="text-center max-w-md px-6">
          <div className="text-yellow-600 mb-4">
            <svg
              className="w-16 h-16 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Google Maps API Key Required
          </h3>
          <p className="text-sm text-gray-700 mb-4">
            Please set <code className="bg-gray-100 px-2 py-1 rounded text-xs font-mono">VITE_GOOGLE_MAPS_API_KEY</code> in your <code className="bg-gray-100 px-2 py-1 rounded text-xs font-mono">.env</code> file
          </p>
          <div className="text-left bg-white p-4 rounded-lg border border-gray-200 mb-4">
            <p className="text-xs font-semibold text-gray-700 mb-2">Setup Instructions:</p>
            <ol className="text-xs text-gray-600 space-y-1 list-decimal list-inside">
              <li>Visit <a href="https://console.cloud.google.com/google/maps-apis" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google Cloud Console</a></li>
              <li>Create or select a project</li>
              <li>Enable the Maps JavaScript API</li>
              <li>Create an API key in the Credentials section</li>
              <li>Add <code className="bg-gray-100 px-1 rounded font-mono">VITE_GOOGLE_MAPS_API_KEY=your_api_key</code> to your <code className="bg-gray-100 px-1 rounded font-mono">.env</code> file</li>
              <li>Restart your development server</li>
            </ol>
          </div>
          <p className="text-xs text-gray-500">
            Need help? Check the <a href="https://developers.google.com/maps/documentation/javascript/get-api-key" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google Maps API documentation</a>
          </p>
        </div>
      </div>
    )
  }

  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: GOOGLE_MAPS_API_KEY,
    libraries: libraries as any,
  })

  // Get user's current location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        position => {
          const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          }
          setUserLocation(location)
          setLocationError(null)
        },
        error => {
          console.error('Error getting location:', error)
          setLocationError('Unable to get your location. Showing default location.')
          // Use default location if geolocation fails
          setUserLocation(DEFAULT_CENTER)
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        }
      )
    } else {
      setLocationError('Geolocation is not supported by your browser.')
      setUserLocation(DEFAULT_CENTER)
    }
  }, [])

  // Fetch nearby doctors when user location is available
  useEffect(() => {
    if (userLocation) {
      fetchNearbyDoctors(userLocation.lat, userLocation.lng)
    }
  }, [userLocation])

  // Fetch nearby hospitals when map is loaded
  useEffect(() => {
    if (map && userLocation) {
      fetchNearbyHospitals(userLocation.lat, userLocation.lng)
    }
  }, [map, userLocation])

  const fetchNearbyHospitals = (lat: number, lng: number) => {
    if (!map) return

    // Set a timeout to use mock data if API doesn't respond within 3 seconds
    const fallbackTimeout = setTimeout(() => {
      console.warn('⚠️ Google Places API timeout. Using mock hospital data for demo.')
      const mockHospitals = generateMockHospitals(lat, lng)
      setGoogleHospitals(mockHospitals)
      if (onHospitalsLoaded) {
        onHospitalsLoaded(mockHospitals, { lat, lng })
      }
    }, 3000)

    try {
      const service = new google.maps.places.PlacesService(map)
      const allResults: GoogleHospital[] = []
      const seenPlaceIds = new Set<string>() // Track unique places
      
      let searchesCompleted = 0
      const totalSearches = 3 // We'll do 3 searches: dermatology hospitals, clinics, and general hospitals
      let hasApiError = false // Track if API fails
    
    // Function to finalize results after all searches complete
    const finalizeResults = () => {
      // Clear the fallback timeout since we got results
      clearTimeout(fallbackTimeout)
      
      console.log(`All searches completed. Total unique results: ${allResults.length}`)
      
      // If API failed or no results, use mock data
      if (hasApiError || allResults.length === 0) {
        console.warn('⚠️ Google Places API failed or returned no results. Using mock hospital data for demo.')
        const mockHospitals = generateMockHospitals(lat, lng)
        setGoogleHospitals(mockHospitals)
        if (onHospitalsLoaded) {
          onHospitalsLoaded(mockHospitals, { lat, lng })
        }
        return
      }
      
      // Categorize results
      const dermatologySpecific: GoogleHospital[] = []
      const generalHospitals: GoogleHospital[] = []
      
      allResults.forEach(place => {
        const name = place.name.toLowerCase()
        const vicinity = place.vicinity?.toLowerCase() || ''
        
        // Check if it's dermatology/skin specific
        const dermaKeywords = [
          'dermatology', 'dermatologist', 'skin', 'kulit', 
          'derma', 'skincare', 'aesthetic', 'beauty',
          'cosmetic', 'laser', 'facial'
        ]
        
        const isDermaSpecific = dermaKeywords.some(keyword => 
          name.includes(keyword) || vicinity.includes(keyword)
        )
        
        // Check if it's a general hospital
        const hospitalKeywords = ['hospital', 'medical center', 'medical centre', 'clinic']
        const isHospital = hospitalKeywords.some(keyword => 
          name.includes(keyword) || vicinity.includes(keyword)
        )
        
        if (isDermaSpecific) {
          dermatologySpecific.push(place)
        } else if (isHospital) {
          generalHospitals.push(place)
        }
      })
      
      // Combine: dermatology-specific first, then general hospitals
      const combinedResults = [...dermatologySpecific, ...generalHospitals]
      
      console.log(`Categorized: ${dermatologySpecific.length} dermatology-specific, ${generalHospitals.length} general hospitals`)
      console.log(`Total to display: ${combinedResults.length}`)
      
      setGoogleHospitals(combinedResults)
      if (onHospitalsLoaded) {
        onHospitalsLoaded(combinedResults, { lat, lng })
      }
    }
    
    // Recursive function to handle pagination for each search
    const handleResults = (searchType: string) => {
      return (results: any[] | null, status: google.maps.places.PlacesServiceStatus, pagination: any) => {
        if (status === google.maps.places.PlacesServiceStatus.OK && results) {
          // Add only unique results
          const newResults = results.filter((r: any) => {
            if (!seenPlaceIds.has(r.place_id)) {
              seenPlaceIds.add(r.place_id)
              return true
            }
            return false
          })
          
          allResults.push(...(newResults as GoogleHospital[]))
          console.log(`[${searchType}] Fetched ${newResults.length} new places, total: ${allResults.length}`)
          
          // Try to get more results if available (up to 60 per search, 180 total)
          if (pagination && pagination.hasNextPage && allResults.length < 180) {
            console.log(`[${searchType}] Fetching next page...`)
            setTimeout(() => {
              pagination.nextPage(handleResults(searchType))
            }, 2000) // Required delay by Google
          } else {
            // This search is complete
            console.log(`[${searchType}] Search completed`)
            searchesCompleted++
            if (searchesCompleted === totalSearches) {
              finalizeResults()
            }
          }
        } else {
          console.error(`[${searchType}] Places search failed:`, status)
          
          // Mark API error for specific failure types
          if (status === 'REQUEST_DENIED' || status === 'OVER_QUERY_LIMIT' || status === 'UNKNOWN_ERROR') {
            hasApiError = true
            console.warn(`⚠️ Google Places API error detected: ${status}`)
          }
          
          searchesCompleted++
          if (searchesCompleted === totalSearches) {
            finalizeResults()
          }
        }
      }
    }
    
    console.log('Starting multi-search for dermatology centers and general hospitals...')
    
    // Search 1: Hospitals with dermatology keyword (dermatology departments)
    const dermaHospitalRequest = {
      location: new google.maps.LatLng(lat, lng),
      radius: 50000, // 50km radius
      type: 'hospital',
      keyword: 'dermatology skin',
    }
    
    // Search 2: Doctor offices/clinics with dermatology keyword (specialized clinics)
    const dermaClinicRequest = {
      location: new google.maps.LatLng(lat, lng),
      radius: 50000, // 50km radius
      type: 'doctor',
      keyword: 'dermatology skin clinic',
    }
    
    // Search 3: General hospitals (for serious cases like skin cancer)
    const generalHospitalRequest = {
      location: new google.maps.LatLng(lat, lng),
      radius: 50000, // 50km radius
      type: 'hospital',
      // No keyword - get all hospitals
    }
    
    console.log('[DERMA-HOSPITAL] Starting dermatology hospital search...')
    service.nearbySearch(dermaHospitalRequest, handleResults('DERMA-HOSPITAL'))
    
    // Delay searches slightly to avoid rate limiting
    setTimeout(() => {
      console.log('[DERMA-CLINIC] Starting dermatology clinic search...')
      service.nearbySearch(dermaClinicRequest, handleResults('DERMA-CLINIC'))
    }, 500)
    
    setTimeout(() => {
      console.log('[GENERAL-HOSPITAL] Starting general hospital search...')
      service.nearbySearch(generalHospitalRequest, handleResults('GENERAL-HOSPITAL'))
    }, 1000)
    
    } catch (error) {
      // If PlacesService fails to initialize, use mock data immediately
      console.error('Failed to initialize Google Places Service:', error)
      console.warn('⚠️ Using mock hospital data for demo.')
      clearTimeout(fallbackTimeout)
      const mockHospitals = generateMockHospitals(lat, lng)
      setGoogleHospitals(mockHospitals)
      if (onHospitalsLoaded) {
        onHospitalsLoaded(mockHospitals, { lat, lng })
      }
    }
  }

  const fetchNearbyDoctors = async (lat: number, lng: number) => {
    try {
      setLoading(true)
      setError(null)
      const nearbyDoctors = await doctorService.getNearbyDoctors({
        lat,
        lng,
        radius: 50, // 50km radius
      })
      setDoctors(nearbyDoctors)
      
      // Notify parent component
      if (onDoctorsLoaded) {
        onDoctorsLoaded(nearbyDoctors, { lat, lng })
      }
    } catch (err) {
      console.error('Error fetching doctors:', err)
      setError('Failed to load nearby doctors. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const onLoad = useCallback((map: google.maps.Map) => {
    setMap(map)
  }, [])

  const onUnmount = useCallback(() => {
    setMap(null)
  }, [])

  const handleMarkerClick = (doctor: Doctor) => {
    setSelectedDoctor(doctor)
    if (onDoctorSelect) {
      onDoctorSelect(doctor)
    }
  }

  const handleCenterOnUser = () => {
    if (map && userLocation) {
      map.panTo(userLocation)
      map.setZoom(12)
    }
  }

  const handleWhatsAppClick = (whatsappNo: string) => {
    const url = doctorService.generateWhatsAppUrl(whatsappNo)
    window.open(url, '_blank')
  }

  const handleBookAppointment = (doctor: Doctor) => {
    setDoctorToBook(doctor)
    setIsBookingModalOpen(true)
  }

  const handleBookingSuccess = () => {
    // Optionally refresh doctors or show success message
    console.log('Appointment booked successfully')
  }

  if (loadError) {
    return (
      <div className="flex items-center justify-center h-96 bg-red-50 rounded-lg">
        <div className="text-center">
          <p className="text-red-600 font-semibold">Error loading Google Maps</p>
          <p className="text-sm text-red-500 mt-2">Please check your API key configuration</p>
        </div>
      </div>
    )
  }

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading map...</p>
        </div>
      </div>
    )
  }

  const mapCenter = userLocation || DEFAULT_CENTER

  return (
    <div className="relative">
      {/* Location error banner */}
      <AnimatePresence>
        {locationError && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-2 rounded-lg shadow-lg"
          >
            <p className="text-sm">{locationError}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading overlay */}
      {loading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10 rounded-lg">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading nearby doctors...</p>
          </div>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 bg-red-100 border border-red-400 text-red-800 px-4 py-2 rounded-lg shadow-lg">
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Center on user button */}
      {userLocation && (
        <button
          onClick={handleCenterOnUser}
          className="absolute top-4 right-4 z-10 bg-white hover:bg-gray-50 text-gray-700 p-3 rounded-lg shadow-lg transition-colors"
          title="Center on my location"
        >
          <Navigation className="w-5 h-5" />
        </button>
      )}

      {/* Google Map */}
      <GoogleMap
        mapContainerStyle={MAP_CONTAINER_STYLE}
        center={mapCenter}
        zoom={12}
        onLoad={onLoad}
        onUnmount={onUnmount}
        options={MAP_OPTIONS}
      >
        {/* User location marker */}
        {userLocation && (
          <Marker
            position={userLocation}
            icon={{
              path: google.maps.SymbolPath.CIRCLE,
              scale: 8,
              fillColor: '#3B82F6',
              fillOpacity: 1,
              strokeColor: '#FFFFFF',
              strokeWeight: 2,
            }}
            title="Your Location"
          />
        )}

        {/* Doctor markers */}
        {doctors.map(doctor => {
          const isSelected = selectedDoctorId === doctor.id
          return (
            <Marker
              key={doctor.id}
              position={{ lat: doctor.lat, lng: doctor.lng }}
              onClick={() => handleMarkerClick(doctor)}
              icon={{
                url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                  <svg xmlns="http://www.w3.org/2000/svg" width="${isSelected ? 40 : 32}" height="${isSelected ? 50 : 40}" viewBox="0 0 32 40">
                    <path fill="${isSelected ? '#2563EB' : '#DC2626'}" d="M16 0C7.163 0 0 7.163 0 16c0 8.837 16 24 16 24s16-15.163 16-24C32 7.163 24.837 0 16 0z"/>
                    <circle cx="16" cy="16" r="6" fill="white"/>
                    <path fill="${isSelected ? '#2563EB' : '#DC2626'}" d="M16 12v8M12 16h8" stroke="white" stroke-width="1.5"/>
                    ${isSelected ? '<circle cx="16" cy="16" r="10" fill="none" stroke="#2563EB" stroke-width="2" opacity="0.5"/>' : ''}
                  </svg>
                `),
                scaledSize: new google.maps.Size(isSelected ? 40 : 32, isSelected ? 50 : 40),
                anchor: new google.maps.Point(isSelected ? 20 : 16, isSelected ? 50 : 40),
              }}
              title={doctor.clinicName}
              animation={isSelected ? google.maps.Animation.BOUNCE : undefined}
            />
          )
        })}

        {/* Info window for selected doctor */}
        {selectedDoctor && (
          <InfoWindow
            position={{ lat: selectedDoctor.lat, lng: selectedDoctor.lng }}
            onCloseClick={() => setSelectedDoctor(null)}
          >
            <div className="p-2 max-w-xs">
              <h3 className="font-semibold text-lg text-gray-900 mb-1">
                {selectedDoctor.clinicName}
              </h3>
              
              {selectedDoctor.fullName && (
                <p className="text-sm text-gray-600 mb-2">Dr. {selectedDoctor.fullName}</p>
              )}

              {selectedDoctor.specialization && (
                <p className="text-sm text-gray-500 mb-2">{selectedDoctor.specialization}</p>
              )}

              {/* Rating */}
              <div className="flex items-center gap-1 mb-3">
                <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                <span className="text-sm font-medium text-gray-700">
                  {selectedDoctor.averageRating?.toFixed(1) || '0.0'}
                </span>
                <span className="text-xs text-gray-500">
                  ({selectedDoctor.reviewCount || 0} reviews)
                </span>
              </div>

              {/* WhatsApp button */}
              <button
                onClick={() => handleWhatsAppClick(selectedDoctor.whatsappNo)}
                className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2 transition-colors mb-2"
              >
                <Phone className="w-4 h-4" />
                <span className="text-sm font-medium">Contact on WhatsApp</span>
              </button>

              {/* Book Appointment button */}
              <button
                onClick={() => handleBookAppointment(selectedDoctor)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2 transition-colors"
              >
                <Calendar className="w-4 h-4" />
                <span className="text-sm font-medium">Book Appointment</span>
              </button>
            </div>
          </InfoWindow>
        )}
      </GoogleMap>

      {/* Doctors count */}
      <div className="mt-4 text-center text-sm text-gray-600">
        {doctors.length > 0 ? (
          <p>
            Found <span className="font-semibold text-gray-900">{doctors.length}</span> verified
            doctor{doctors.length !== 1 ? 's' : ''} nearby
          </p>
        ) : (
          !loading && <p>No verified doctors found in your area</p>
        )}
      </div>

      {/* Appointment Booking Modal */}
      {doctorToBook && (
        <AppointmentBookingModal
          isOpen={isBookingModalOpen}
          onClose={() => setIsBookingModalOpen(false)}
          doctor={doctorToBook}
          onSuccess={handleBookingSuccess}
        />
      )}
    </div>
  )
}
