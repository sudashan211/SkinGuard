"""
Demo data storage for local development without database
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

# In-memory storage
users_db: Dict[str, dict] = {}
patients_db: Dict[str, dict] = {}
patient_data_db: Dict[str, dict] = {}  # For patient health profiles
doctors_db: Dict[str, dict] = {}
screenings_db: Dict[str, dict] = {}
appointments_db: Dict[str, dict] = {}
medical_reports_db: Dict[str, dict] = {}
reviews_db: Dict[str, dict] = {}

# Demo users (passwords stored in plain text for demo mode)
DEMO_USERS = {
    "patient@demo.com": {
        "id": "demo-patient-001",
        "email": "patient@demo.com",
        "full_name": "Demo Patient",
        "password": "demo123",  # Plain text in demo mode
        "role": "patient",
        "verified": True,
        "created_at": datetime.utcnow().isoformat(),
    },
    "doctor@demo.com": {
        "id": "demo-doctor-001",
        "email": "doctor@demo.com",
        "full_name": "Dr. Demo Doctor",
        "password": "demo123",  # Plain text in demo mode
        "role": "doctor",
        "verified": True,  # Demo doctor is pre-verified
        "created_at": datetime.utcnow().isoformat(),
    },
    "admin@demo.com": {
        "id": "demo-admin-001",
        "email": "admin@demo.com",
        "full_name": "Demo Admin",
        "password": "demo123",  # Plain text in demo mode
        "role": "admin",
        "verified": True,
        "created_at": datetime.utcnow().isoformat(),
    }
}

# Initialize demo data
def init_demo_data():
    """Initialize demo data for testing"""
    global users_db, patients_db, patient_data_db, doctors_db, medical_reports_db, appointments_db, reviews_db
    
    # Add demo users
    for email, user in DEMO_USERS.items():
        users_db[user["id"]] = user
        
        # Create patient health profile
        if user["role"] == "patient":
            patient_data_db[user["id"]] = {
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "age": 35,
                "skin_type": "III",
                "family_history": "No family history of skin cancer",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        
        # Create doctor profile
        elif user["role"] == "doctor":
            doctor_id = str(uuid.uuid4())
            doctors_db[user["id"]] = {
                "id": doctor_id,
                "user_id": user["id"],
                "license_no": "DEM123456",
                "clinic_name": "Demo Dermatology Clinic",
                "lat": 40.7128,  # New York coordinates
                "lng": -74.0060,
                "whatsapp_no": "+1234567891",
                "specialization": "Dermatology",
                "bio": "Experienced dermatologist specializing in skin cancer detection",
                "education": "MD from Demo Medical School, Residency in Dermatology",
                "certifications": "Board Certified in Dermatology",
                "languages": "English, Spanish",
                "clinic_hours": "Mon-Fri: 9AM-5PM, Sat: 10AM-2PM",
                "average_rating": 4.8,
                "review_count": 2,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            # Create demo medical reports for doctor to review
            report1_id = str(uuid.uuid4())
            medical_reports_db[report1_id] = {
                "id": report1_id,
                "patient_id": "demo-patient-001",
                "image_url": "/uploads/demo-patient-001/demo-urgent.jpg",
                "ai_prediction": {
                    "predictions": [
                        {"class": "melanoma", "confidence": 0.92},
                        {"class": "basal_cell_carcinoma", "confidence": 0.05},
                        {"class": "benign_keratosis", "confidence": 0.03}
                    ]
                },
                "symptoms": "Dark irregular mole that has changed in size",
                "status": "urgent",
                "risk_level": "high",
                "body_location": "back",
                "consultation_notes": None,
                "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            }
            
            report2_id = str(uuid.uuid4())
            medical_reports_db[report2_id] = {
                "id": report2_id,
                "patient_id": "demo-patient-001",
                "image_url": "/uploads/demo-patient-001/demo-safe.jpg",
                "ai_prediction": {
                    "predictions": [
                        {"class": "benign_keratosis", "confidence": 0.88},
                        {"class": "melanocytic_Nevi", "confidence": 0.10},
                        {"class": "melanoma", "confidence": 0.02}
                    ]
                },
                "symptoms": "Small brown spot, no changes",
                "status": "safe",
                "risk_level": "low",
                "body_location": "arm",
                "consultation_notes": None,
                "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
                "updated_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            }
            
            # Create demo appointments
            appt1_id = str(uuid.uuid4())
            appointments_db[appt1_id] = {
                "id": appt1_id,
                "patient_id": "demo-patient-001",
                "doctor_id": doctor_id,
                "report_id": report1_id,
                "scheduled_at": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                "status": "pending",
                "consultation_type": "in_person",
                "video_room_url": None,
                "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            }
            
            appt2_id = str(uuid.uuid4())
            appointments_db[appt2_id] = {
                "id": appt2_id,
                "patient_id": "demo-patient-001",
                "doctor_id": doctor_id,
                "report_id": report2_id,
                "scheduled_at": (datetime.utcnow() - timedelta(days=10)).isoformat(),
                "status": "completed",
                "consultation_type": "video",
                "video_room_url": "https://video.skinguard.app/room/demo-room-123",
                "created_at": (datetime.utcnow() - timedelta(days=15)).isoformat(),
                "updated_at": (datetime.utcnow() - timedelta(days=10)).isoformat(),
            }
            
            # Create demo reviews
            review1_id = str(uuid.uuid4())
            reviews_db[review1_id] = {
                "id": review1_id,
                "patient_id": "demo-patient-001",
                "doctor_id": doctor_id,
                "appointment_id": appt2_id,
                "rating": 5,
                "review_text": "Excellent doctor! Very thorough and explained everything clearly.",
                "flagged": False,
                "created_at": (datetime.utcnow() - timedelta(days=9)).isoformat(),
            }
            
            review2_id = str(uuid.uuid4())
            reviews_db[review2_id] = {
                "id": review2_id,
                "patient_id": "demo-patient-001",
                "doctor_id": doctor_id,
                "appointment_id": None,
                "rating": 4,
                "review_text": "Great experience, would recommend.",
                "flagged": False,
                "created_at": (datetime.utcnow() - timedelta(days=20)).isoformat(),
            }

# Initialize on module load
init_demo_data()


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    for user in users_db.values():
        if user["email"] == email:
            return user
    return None


def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID"""
    return users_db.get(user_id)


def create_user(user_data: dict) -> dict:
    """Create a new user"""
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        **user_data,
        "created_at": datetime.utcnow().isoformat(),
    }
    users_db[user_id] = user
    return user


def get_patient_by_user_id(user_id: str) -> Optional[dict]:
    """Get patient profile by user ID"""
    return patients_db.get(user_id)


def get_patient_data_by_user_id(user_id: str) -> Optional[dict]:
    """Get patient health data by user ID"""
    return patient_data_db.get(user_id)


def create_patient(patient_data: dict) -> dict:
    """Create a new patient profile"""
    patient_id = patient_data.get("user_id", str(uuid.uuid4()))
    patient = {
        "id": patient_id,
        **patient_data,
        "created_at": datetime.utcnow().isoformat(),
    }
    patients_db[patient_id] = patient
    return patient


def create_patient_data(patient_data: dict) -> dict:
    """Create a new patient health profile"""
    data_id = str(uuid.uuid4())
    user_id = patient_data.get("user_id")
    data = {
        "id": data_id,
        **patient_data,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    patient_data_db[user_id] = data
    return data


def update_patient_data(user_id: str, update_data: dict) -> Optional[dict]:
    """Update patient health profile"""
    if user_id in patient_data_db:
        patient_data_db[user_id].update(update_data)
        patient_data_db[user_id]["updated_at"] = datetime.utcnow().isoformat()
        return patient_data_db[user_id]
    return None


def get_doctor_by_user_id(user_id: str) -> Optional[dict]:
    """Get doctor profile by user ID"""
    return doctors_db.get(user_id)


def create_doctor(doctor_data: dict) -> dict:
    """Create a new doctor profile"""
    doctor_id = str(uuid.uuid4())
    user_id = doctor_data.get("user_id")
    doctor = {
        "id": doctor_id,
        **doctor_data,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    doctors_db[user_id] = doctor
    return doctor


def update_doctor(user_id: str, update_data: dict) -> Optional[dict]:
    """Update doctor profile"""
    if user_id in doctors_db:
        doctors_db[user_id].update(update_data)
        doctors_db[user_id]["updated_at"] = datetime.utcnow().isoformat()
        return doctors_db[user_id]
    return None


def get_all_doctors() -> List[dict]:
    """Get all doctors"""
    return list(doctors_db.values())


def create_screening(screening_data: dict) -> dict:
    """Create a new screening"""
    screening_id = str(uuid.uuid4())
    screening = {
        "id": screening_id,
        **screening_data,
        "created_at": datetime.utcnow().isoformat(),
    }
    screenings_db[screening_id] = screening
    return screening


def get_screenings_by_patient(patient_id: str) -> List[dict]:
    """Get all screenings for a patient"""
    return [s for s in screenings_db.values() if s.get("patient_id") == patient_id]


def get_screening_by_id(screening_id: str) -> Optional[dict]:
    """Get screening by ID"""
    return screenings_db.get(screening_id)


def create_medical_report(report_data: dict) -> dict:
    """Create a new medical report"""
    # Use the ID from report_data if provided, otherwise generate new one
    report_id = report_data.get("id", str(uuid.uuid4()))
    report = {
        **report_data,
        "id": report_id,
    }
    # Ensure created_at is set if not provided
    if "created_at" not in report:
        report["created_at"] = datetime.utcnow().isoformat()
    
    medical_reports_db[report_id] = report
    return report


def get_reports_by_patient(patient_id: str) -> List[dict]:
    """Get all medical reports for a patient"""
    reports = [r for r in medical_reports_db.values() if r.get("patient_id") == patient_id]
    # Sort by created_at descending (newest first)
    reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return reports


def get_report_by_id(report_id: str) -> Optional[dict]:
    """Get medical report by ID"""
    return medical_reports_db.get(report_id)


def get_reports_by_status(status_filter: Optional[str] = None) -> List[dict]:
    """Get medical reports filtered by status"""
    if status_filter:
        return [r for r in medical_reports_db.values() if r.get("status") == status_filter]
    else:
        # Return safe and urgent reports (exclude flagged)
        return [r for r in medical_reports_db.values() if r.get("status") in ["safe", "urgent"]]


def get_appointments_by_doctor_id(doctor_id: str) -> List[dict]:
    """Get all appointments for a doctor"""
    appointments = [a for a in appointments_db.values() if a.get("doctor_id") == doctor_id]
    # Sort by scheduled_at
    appointments.sort(key=lambda x: x.get("scheduled_at", ""), reverse=False)
    return appointments


def get_appointments_by_patient_id(patient_id: str) -> List[dict]:
    """Get all appointments for a patient"""
    appointments = [a for a in appointments_db.values() if a.get("patient_id") == patient_id]
    # Sort by scheduled_at
    appointments.sort(key=lambda x: x.get("scheduled_at", ""), reverse=False)
    return appointments


def get_reviews_by_doctor_id(doctor_id: str) -> List[dict]:
    """Get all reviews for a doctor"""
    reviews = [r for r in reviews_db.values() if r.get("doctor_id") == doctor_id]
    # Sort by created_at descending (newest first)
    reviews.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return reviews


def update_report_notes(report_id: str, notes: str) -> Optional[dict]:
    """Update consultation notes for a report"""
    if report_id in medical_reports_db:
        medical_reports_db[report_id]["consultation_notes"] = notes
        medical_reports_db[report_id]["updated_at"] = datetime.utcnow().isoformat()
        return medical_reports_db[report_id]
    return None


def get_appointment_by_id(appointment_id: str) -> Optional[dict]:
    """Get appointment by ID"""
    return appointments_db.get(appointment_id)


def update_appointment(appointment_id: str, update_data: dict) -> Optional[dict]:
    """Update appointment"""
    if appointment_id in appointments_db:
        appointments_db[appointment_id].update(update_data)
        appointments_db[appointment_id]["updated_at"] = datetime.utcnow().isoformat()
        return appointments_db[appointment_id]
    return None
