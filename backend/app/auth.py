"""
Authentication utilities and JWT token management
Requirements: 1.1, 1.2
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status
from app.config import settings
import uuid

# Conditional imports based on demo mode
if not settings.demo_mode:
    from app.database import supabase, supabase_anon
else:
    from app import demo_data
    supabase = None
    supabase_anon = None


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches
    """
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: Data to encode in the token
        
    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token to decode
        
    Returns:
        Dict: Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def register_user(email: str, password: str, full_name: str, role: str) -> Dict[str, Any]:
    """
    Register a new user and create profile
    Requirements: 1.1
    
    Args:
        email: User email
        password: User password
        full_name: User full name
        role: User role (patient, doctor, admin)
        
    Returns:
        Dict: User profile data
        
    Raises:
        HTTPException: If registration fails
    """
    if settings.demo_mode:
        # Demo mode registration - plain text password
        existing_user = demo_data.get_user_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user_data = {
            "email": email,
            "password": password,  # Plain text in demo mode
            "role": role,
        }
        user = demo_data.create_user(user_data)
        
        # Create profile based on role
        if role == "patient":
            profile = demo_data.create_patient({
                "user_id": user["id"],
                "first_name": full_name.split()[0] if full_name else "",
                "last_name": full_name.split()[-1] if len(full_name.split()) > 1 else "",
            })
        elif role == "doctor":
            profile = demo_data.create_doctor({
                "user_id": user["id"],
                "first_name": full_name.split()[0] if full_name else "",
                "last_name": full_name.split()[-1] if len(full_name.split()) > 1 else "",
            })
        
        return {
            "id": user["id"],
            "email": email,
            "full_name": full_name,
            "role": role,
            "verified": False,
            "language_preference": "en",
            "created_at": user["created_at"]
        }
    
    try:
        # Check if using PostgreSQL (local database)
        import os
        use_postgres = os.getenv("DATABASE_URL", "").startswith("postgresql://")
        
        if use_postgres:
            # PostgreSQL registration - direct database insert
            # Check if email already exists
            existing = supabase.table("profiles").select("id").eq("email", email).execute()
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Generate UUID for user
            user_id = str(uuid.uuid4())
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Create profile record
            profile_data = {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "role": role,
                "verified": True if role == "doctor" else False,  # Auto-verify doctors
                "language_preference": "en",
                "password_hash": hashed_password
            }
            
            profile_response = supabase.table("profiles").insert(profile_data).execute()
            
            if not profile_response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user profile"
                )
            
            # If doctor, create doctor profile automatically
            if role == "doctor":
                doctor_data = {
                    "user_id": user_id,
                    "license_no": f"MD-{user_id[:8]}",  # Generate unique license number
                    "clinic_name": f"{full_name}'s Clinic",
                    "lat": 1.3521,  # Default Singapore coordinates
                    "lng": 103.8198,
                    "whatsapp_no": "+65-0000-0000",  # Default placeholder
                    "specialization": "Dermatology",
                    "bio": f"Dermatologist - {full_name}",
                    "languages": "English",
                    "clinic_hours": "Mon-Fri: 9AM-5PM",
                    "average_rating": 0.0,
                    "review_count": 0
                }
                
                try:
                    doctor_result = supabase.table("doctors").insert(doctor_data).execute()
                    print(f"[SIGNUP] Doctor profile created: {doctor_result.data}")
                except Exception as e:
                    # Log error but don't fail registration
                    print(f"[SIGNUP] ERROR: Failed to create doctor profile: {e}")
                    import traceback
                    traceback.print_exc()
            
            return profile_response.data[0]
        else:
            # Supabase Auth registration
            auth_response = supabase_anon.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account"
                )
            
            user_id = auth_response.user.id
            
            # Create profile record with UUID and role
            profile_data = {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "role": role,
                "verified": True if role == "doctor" else False,  # Auto-verify doctors
                "language_preference": "en"
            }
            
            profile_response = supabase.table("profiles").insert(profile_data).execute()
            
            if not profile_response.data:
                # Rollback: delete auth user if profile creation fails
                try:
                    supabase.auth.admin.delete_user(user_id)
                except:
                    pass
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user profile"
                )
            
            return profile_response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user with email and password
    Requirements: 1.2
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Dict: Authentication response with tokens and user data
        
    Raises:
        HTTPException: If authentication fails
    """
    if settings.demo_mode:
        # Demo mode authentication - simple password check
        user = demo_data.get_user_by_email(email)
        if not user or user["password"] != password:  # Plain text comparison in demo mode
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create custom JWT tokens
        token_data = {
            "sub": user["id"],
            "email": email,
            "role": user["role"],
            "verified": True
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": user["id"]})
        
        # Get profile based on role
        profile = None
        if user["role"] == "patient":
            profile = demo_data.get_patient_by_user_id(user["id"])
        elif user["role"] == "doctor":
            profile = demo_data.get_doctor_by_user_id(user["id"])
        
        user_profile = {
            "id": user["id"],
            "email": email,
            "full_name": f"{profile.get('first_name', '')} {profile.get('last_name', '')}" if profile else "Demo User",
            "role": user["role"],
            "verified": True,
            "language_preference": "en",
            "created_at": user["created_at"],
            "updated_at": user["created_at"]  # Add updated_at field
        }
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60,
            "user": user_profile
        }
    
    try:
        # Check if using PostgreSQL (local database)
        import os
        use_postgres = os.getenv("DATABASE_URL", "").startswith("postgresql://")
        
        if use_postgres:
            # PostgreSQL authentication - verify password hash
            profile_response = supabase.table("profiles").select("*").eq("email", email).execute()
            
            if not profile_response.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            user_profile = profile_response.data[0]
            
            # Verify password
            if not verify_password(password, user_profile.get("password_hash", "")):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Create custom JWT tokens
            token_data = {
                "sub": str(user_profile["id"]),
                "email": email,
                "role": user_profile["role"],
                "verified": user_profile["verified"]
            }
            
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token({"sub": str(user_profile["id"])})
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.jwt_access_token_expire_minutes * 60,
                "user": user_profile
            }
        else:
            # Supabase Auth authentication
            auth_response = supabase_anon.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user or not auth_response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Get user profile
            profile_response = supabase.table("profiles").select("*").eq("id", auth_response.user.id).execute()
            
            if not profile_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            user_profile = profile_response.data[0]
            
            # Create custom JWT tokens
            token_data = {
                "sub": str(auth_response.user.id),
                "email": email,
                "role": user_profile["role"],
                "verified": user_profile["verified"]
            }
            
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token({"sub": str(auth_response.user.id)})
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.jwt_access_token_expire_minutes * 60,
                "user": user_profile
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


def get_current_user_from_token(token: str) -> Dict[str, Any]:
    """
    Get current user profile from JWT token
    Requirements: 1.2
    
    Args:
        token: JWT access token
        
    Returns:
        Dict: User profile data
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    if settings.demo_mode:
        # Demo mode - get user from demo data
        user = demo_data.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get profile based on role
        profile = None
        if user["role"] == "patient":
            profile = demo_data.get_patient_by_user_id(user_id)
        elif user["role"] == "doctor":
            profile = demo_data.get_doctor_by_user_id(user_id)
        
        return {
            "id": user["id"],
            "email": user["email"],
            "full_name": f"{profile.get('first_name', '')} {profile.get('last_name', '')}" if profile else "Demo User",
            "role": user["role"],
            "verified": True,
            "language_preference": "en",
            "created_at": user["created_at"],
            "updated_at": user["created_at"]  # Add updated_at field
        }
    
    # Get user profile from database
    profile_response = supabase.table("profiles").select("*").eq("id", user_id).execute()
    
    if not profile_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return profile_response.data[0]


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """
    Refresh access token using refresh token
    Requirements: 1.2
    
    Args:
        refresh_token: JWT refresh token
        
    Returns:
        Dict: New access token and refresh token
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    payload = decode_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    if settings.demo_mode:
        # Demo mode - get user from demo data
        user = demo_data.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create new tokens
        token_data = {
            "sub": user_id,
            "email": user["email"],
            "role": user["role"],
            "verified": True
        }
        
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token({"sub": user_id})
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60
        }
    
    # Get user profile
    profile_response = supabase.table("profiles").select("*").eq("id", user_id).execute()
    
    if not profile_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_profile = profile_response.data[0]
    
    # Create new tokens
    token_data = {
        "sub": user_id,
        "email": user_profile["email"],
        "role": user_profile["role"],
        "verified": user_profile["verified"]
    }
    
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token({"sub": user_id})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60
    }
