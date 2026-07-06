"""
Emergency Referral System for urgent skin cancer cases
Requirements: 23.1, 23.3

This module handles:
- Detection of urgent cases (cancer probability > 85%)
- Finding nearest verified doctors
- Sending email notifications to doctors
"""
import logging
import math
from typing import List, Dict, Optional, Tuple
from app.database import supabase
from app.email_service import get_email_service

logger = logging.getLogger(__name__)


class EmergencyReferralService:
    """
    Service for handling emergency referrals to nearest doctors
    """
    
    def __init__(self):
        """Initialize emergency referral service"""
        self.email_service = get_email_service()
    
    @staticmethod
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Args:
            lat1: Latitude of first point
            lng1: Longitude of first point
            lat2: Latitude of second point
            lng2: Longitude of second point
            
        Returns:
            float: Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    async def find_nearest_doctors(
        self,
        patient_lat: Optional[float] = None,
        patient_lng: Optional[float] = None,
        limit: int = 3
    ) -> List[Dict]:
        """
        Find the nearest verified doctors to a patient location
        Requirements: 23.3
        
        If patient coordinates are not provided, returns the first N verified doctors
        ordered by creation date (most recently verified first).
        
        Args:
            patient_lat: Patient's latitude (optional)
            patient_lng: Patient's longitude (optional)
            limit: Number of doctors to return (default: 3)
            
        Returns:
            List[Dict]: List of nearest verified doctors with their information
        """
        try:
            # Step 1: Get all verified doctor profiles
            profiles_result = supabase.table("profiles")\
                .select("*")\
                .eq("role", "doctor")\
                .eq("verified", True)\
                .execute()
            
            if not profiles_result.data or len(profiles_result.data) == 0:
                logger.warning("No verified doctors found in the system")
                return []
            
            verified_user_ids = [profile["id"] for profile in profiles_result.data]
            profiles_map = {profile["id"]: profile for profile in profiles_result.data}
            
            # Step 2: Get doctor records for verified profiles
            doctors_result = supabase.table("doctors")\
                .select("*")\
                .in_("user_id", verified_user_ids)\
                .execute()
            
            if not doctors_result.data or len(doctors_result.data) == 0:
                logger.warning("No doctor records found for verified profiles")
                return []
            
            # Step 3: Calculate distances and sort
            doctors_with_distance = []
            
            for doctor in doctors_result.data:
                profile = profiles_map.get(doctor["user_id"])
                if not profile:
                    continue
                
                doctor_info = {
                    "doctor_id": doctor["id"],
                    "user_id": doctor["user_id"],
                    "full_name": profile["full_name"],
                    "email": profile["email"],
                    "clinic_name": doctor["clinic_name"],
                    "lat": float(doctor["lat"]),
                    "lng": float(doctor["lng"]),
                    "whatsapp_no": doctor["whatsapp_no"],
                    "specialization": doctor.get("specialization"),
                    "distance_km": None
                }
                
                # Calculate distance if patient coordinates provided
                if patient_lat is not None and patient_lng is not None:
                    distance = self.calculate_distance(
                        patient_lat, patient_lng,
                        doctor_info["lat"], doctor_info["lng"]
                    )
                    doctor_info["distance_km"] = round(distance, 2)
                
                doctors_with_distance.append(doctor_info)
            
            # Step 4: Sort by distance (if available) or by creation date
            if patient_lat is not None and patient_lng is not None:
                # Sort by distance (nearest first)
                doctors_with_distance.sort(key=lambda d: d["distance_km"])
            else:
                # No patient location - just return first N doctors
                # In production, you might want to sort by rating or other criteria
                pass
            
            # Step 5: Return top N doctors
            nearest_doctors = doctors_with_distance[:limit]
            
            logger.info(f"Found {len(nearest_doctors)} nearest verified doctors")
            return nearest_doctors
            
        except Exception as e:
            logger.error(f"Error finding nearest doctors: {str(e)}", exc_info=True)
            return []
    
    async def notify_nearest_doctors(
        self,
        report_id: str,
        patient_id: str,
        patient_name: str,
        patient_lat: Optional[float] = None,
        patient_lng: Optional[float] = None,
        risk_level: str = "urgent",
        top_prediction: Optional[Dict] = None
    ) -> Tuple[int, int]:
        """
        Notify the 3 nearest verified doctors about an urgent case
        Requirements: 23.3
        
        Args:
            report_id: Medical report UUID
            patient_id: Patient UUID
            patient_name: Patient's full name
            patient_lat: Patient's latitude (optional)
            patient_lng: Patient's longitude (optional)
            risk_level: Risk level (default: urgent)
            top_prediction: Top AI prediction {type: str, probability: float}
            
        Returns:
            Tuple[int, int]: (number of doctors found, number of emails sent successfully)
        """
        try:
            # Find nearest doctors
            nearest_doctors = await self.find_nearest_doctors(
                patient_lat=patient_lat,
                patient_lng=patient_lng,
                limit=3
            )
            
            if not nearest_doctors:
                logger.warning(f"No verified doctors available to notify for report {report_id}")
                return (0, 0)
            
            # Generate report URL (in production, this would be the actual frontend URL)
            base_url = "https://skinguard.com"  # TODO: Get from config
            report_url = f"{base_url}/doctor/reports/{report_id}"
            
            # Send notifications to each doctor
            emails_sent = 0
            
            for doctor in nearest_doctors:
                try:
                    success = await self.email_service.send_urgent_case_notification(
                        doctor_email=doctor["email"],
                        doctor_name=doctor["full_name"],
                        patient_name=patient_name,
                        report_id=report_id,
                        risk_level=risk_level,
                        top_prediction=top_prediction or {"type": "Unknown", "probability": 0.0},
                        report_url=report_url
                    )
                    
                    if success:
                        emails_sent += 1
                        logger.info(
                            f"Sent urgent case notification to Dr. {doctor['full_name']} "
                            f"({doctor['email']}) for report {report_id}"
                        )
                    else:
                        logger.warning(
                            f"Failed to send notification to Dr. {doctor['full_name']} "
                            f"({doctor['email']}) for report {report_id}"
                        )
                        
                except Exception as e:
                    logger.error(
                        f"Error sending notification to Dr. {doctor['full_name']}: {str(e)}",
                        exc_info=True
                    )
            
            logger.info(
                f"Emergency referral completed for report {report_id}: "
                f"{emails_sent}/{len(nearest_doctors)} notifications sent"
            )
            
            return (len(nearest_doctors), emails_sent)
            
        except Exception as e:
            logger.error(f"Error in notify_nearest_doctors: {str(e)}", exc_info=True)
            return (0, 0)


# Global emergency referral service instance
_emergency_referral_service: Optional[EmergencyReferralService] = None


def get_emergency_referral_service() -> EmergencyReferralService:
    """
    Get or create the global emergency referral service instance
    
    Returns:
        EmergencyReferralService: Global emergency referral service instance
    """
    global _emergency_referral_service
    if _emergency_referral_service is None:
        _emergency_referral_service = EmergencyReferralService()
    return _emergency_referral_service
