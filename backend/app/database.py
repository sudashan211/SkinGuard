"""
Database connection and client management
"""
from typing import Optional
from app.config import settings
import os

# Check if using local PostgreSQL
USE_POSTGRES = os.getenv("DATABASE_URL", "").startswith("postgresql://")

# Conditional imports based on demo mode and database type
if not settings.demo_mode:
    if USE_POSTGRES:
        # Use local PostgreSQL
        from app.postgres_db import get_postgres_client, PostgreSQLClient
        
        supabase: PostgreSQLClient = get_postgres_client()
        supabase_anon: PostgreSQLClient = get_postgres_client()
        
        def get_supabase_client() -> PostgreSQLClient:
            """Get PostgreSQL client"""
            return get_postgres_client()
        
        def get_supabase_anon_client() -> PostgreSQLClient:
            """Get PostgreSQL client (same as regular for local)"""
            return get_postgres_client()
    else:
        # Use Supabase
        from supabase import create_client, Client
        
        def get_supabase_client() -> Client:
            """
            Create and return a Supabase client instance
            
            Returns:
                Client: Supabase client for database operations
            """
            return create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_service_role_key
            )

        def get_supabase_anon_client() -> Client:
            """
            Create and return a Supabase client with anon key (for auth operations)
            
            Returns:
                Client: Supabase client with anon key
            """
            return create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_anon_key
            )

        # Global client instance
        supabase: Client = get_supabase_client()
        supabase_anon: Client = get_supabase_anon_client()
else:
    # Demo mode - no database connection needed
    supabase = None
    supabase_anon = None
    
    def get_supabase_client():
        """Demo mode - returns None"""
        return None
    
    def get_supabase_anon_client():
        """Demo mode - returns None"""
        return None
