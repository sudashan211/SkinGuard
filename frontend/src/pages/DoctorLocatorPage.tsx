import { useState } from 'react'
import { MapPin, Search, Building2, Star, ExternalLink, Navigation2 } from 'lucide-react'
import DoctorMap from '@/components/patient/DoctorMap'
import type { Doctor } from '@/types/doctor'

export default function DoctorLocatorPage() {
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null)
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [googleHospitals, setGoogleHospitals] = useState<any[]>([])
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)

  const handleDoctorSelect = (doctor: Doctor) => {
    setSelectedDoctor(doctor)
  }

  const handleDoctorsLoaded = (loadedDoctors: Doctor[], location: { lat: number; lng: number }) => {
    setDoctors(loadedDoctors)
    setUserLocation(location)
  }

  const handleHospitalsLoaded = (hospitals: any[], location: { lat: number; lng: number }) => {
    // Calculate distance for each hospital
    const hospitalsWithDistance = hospitals.map(hospital => {
      const lat = typeof hospital.geometry.location.lat === 'function' 
        ? hospital.geometry.location.lat() 
        : hospital.geometry.location.lat
      const lng = typeof hospital.geometry.location.lng === 'function'
        ? hospital.geometry.location.lng()
        : hospital.geometry.location.lng
      
      const distance = parseFloat(calculateDistance(location.lat, location.lng, lat, lng))
      
      return {
        ...hospital,
        calculatedDistance: distance
      }
    })
    
    // Sort by: 1) High rating first (4.5+), 2) Then by distance
    const sortedHospitals = hospitalsWithDistance.sort((a, b) => {
      const ratingA = a.rating || 0
      const ratingB = b.rating || 0
      
      // High-rated hospitals (4.5+) come first
      const isHighRatedA = ratingA >= 4.5
      const isHighRatedB = ratingB >= 4.5
      
      if (isHighRatedA && !isHighRatedB) return -1
      if (!isHighRatedA && isHighRatedB) return 1
      
      // If both are high-rated or both are not, sort by rating first
      if (Math.abs(ratingB - ratingA) > 0.1) {
        return ratingB - ratingA // Higher rating first
      }
      
      // If ratings are similar, sort by distance (closer first)
      return a.calculatedDistance - b.calculatedDistance
    })
    
    setGoogleHospitals(sortedHospitals)
    setUserLocation(location)
  }

  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const R = 6371 // Radius of the Earth in km
    const dLat = (lat2 - lat1) * (Math.PI / 180)
    const dLon = (lon2 - lon1) * (Math.PI / 180)
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * (Math.PI / 180)) *
        Math.cos(lat2 * (Math.PI / 180)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    const distance = R * c
    return distance.toFixed(1)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-100 rounded-lg">
              <MapPin className="w-6 h-6 text-blue-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Find Medical Centers</h1>
          </div>
          <p className="text-gray-600 ml-14">
            Locate dermatology clinics and hospitals near you for skin consultations and treatment
          </p>
        </div>

        {/* Info banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <Search className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-1">How it works</h3>
              <p className="text-sm text-blue-800">
                We'll show you dermatology specialists and general hospitals nearby. Dermatology clinics are listed first, 
                followed by general hospitals for serious conditions like skin cancer.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Suggested Hospitals List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6 sticky top-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-blue-600" />
                  <h2 className="text-lg font-semibold text-gray-900">Medical Centers</h2>
                </div>
                {googleHospitals.length > 0 && (
                  <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                    {googleHospitals.length} found
                  </span>
                )}
              </div>
              
              {googleHospitals.length === 0 ? (
                <div className="text-center py-8">
                  <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-sm text-gray-500">Loading medical centers from Google Maps...</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[calc(100vh-300px)] overflow-y-auto pr-2">
                  {googleHospitals.map((hospital, index) => {
                    const lat = typeof hospital.geometry.location.lat === 'function' 
                      ? hospital.geometry.location.lat() 
                      : hospital.geometry.location.lat
                    const lng = typeof hospital.geometry.location.lng === 'function'
                      ? hospital.geometry.location.lng()
                      : hospital.geometry.location.lng
                    
                    return (
                      <div
                        key={hospital.place_id}
                        className="w-full text-left p-4 rounded-lg border-2 transition-all hover:shadow-md border-gray-200 hover:border-blue-300 relative"
                      >
                        {/* Ranking badge for top 3 */}
                        {index < 3 && (
                          <div className="absolute -top-2 -right-2 bg-gradient-to-r from-yellow-400 to-orange-400 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center shadow-lg">
                            {index + 1}
                          </div>
                        )}
                        
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-semibold text-gray-900 text-sm line-clamp-2">
                            {hospital.name}
                          </h3>
                          {userLocation && (
                            <div className="flex items-center gap-1 text-xs text-gray-500 ml-2 flex-shrink-0">
                              <Navigation2 className="w-3 h-3" />
                              {calculateDistance(
                                userLocation.lat,
                                userLocation.lng,
                                lat,
                                lng
                              )} km
                            </div>
                          )}
                        </div>
                        
                        <p className="text-xs text-gray-600 mb-2 line-clamp-2">{hospital.vicinity}</p>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-1">
                            <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                            <span className="text-xs font-medium text-gray-700">
                              {hospital.rating?.toFixed(1) || 'N/A'}
                            </span>
                            {hospital.user_ratings_total && (
                              <span className="text-xs text-gray-500">
                                ({hospital.user_ratings_total})
                              </span>
                            )}
                          </div>
                          
                          <a
                            href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(hospital.name)}&query_place_id=${hospital.place_id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-medium"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <ExternalLink className="w-3 h-3" />
                            View
                          </a>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Map */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <DoctorMap 
                onDoctorSelect={handleDoctorSelect} 
                onDoctorsLoaded={handleDoctorsLoaded}
                onHospitalsLoaded={handleHospitalsLoaded}
                selectedDoctorId={selectedDoctor?.id}
              />
            </div>
          </div>
        </div>

        {/* Selected hospital details (optional expanded view) */}
        {selectedDoctor && (
          <div className="mt-6 bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Selected Hospital</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Hospital/Clinic Name</p>
                <p className="font-medium text-gray-900">{selectedDoctor.clinicName}</p>
              </div>
              {selectedDoctor.fullName && (
                <div>
                  <p className="text-sm text-gray-500">Doctor Name</p>
                  <p className="font-medium text-gray-900">Dr. {selectedDoctor.fullName}</p>
                </div>
              )}
              {selectedDoctor.specialization && (
                <div>
                  <p className="text-sm text-gray-500">Specialization</p>
                  <p className="font-medium text-gray-900">{selectedDoctor.specialization}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-gray-500">Rating</p>
                <p className="font-medium text-gray-900">
                  {selectedDoctor.averageRating?.toFixed(1) || '0.0'} ({selectedDoctor.reviewCount || 0} reviews)
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
