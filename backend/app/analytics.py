"""
Analytics Service for SkinGuard Platform
Requirements: 20.1, 20.2, 20.3, 20.5, 20.6

Provides analytics and usage statistics for the admin dashboard.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.config import settings
import logging

# Conditional imports based on demo mode
if not settings.demo_mode:
    from app.database import supabase
else:
    supabase = None

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for generating platform analytics and usage statistics"""
    
    async def get_dashboard_metrics(self) -> Dict:
        """
        Get analytics dashboard metrics
        Requirements: 20.3
        
        Property 65: Analytics Dashboard Metrics Completeness
        For any admin accessing the analytics dashboard, the displayed data should 
        include daily active users, total screenings performed, and average processing time.
        
        Returns:
            Dict containing:
            - daily_active_users: Number of unique users active in the last 24 hours
            - total_screenings: Total number of medical reports created
            - average_processing_time: Average AI processing time in seconds
        """
        if settings.demo_mode:
            # Return demo data
            return {
                "daily_active_users": 42,
                "total_screenings": 156,
                "average_processing_time": 3.45
            }
        
        try:
            # Calculate 24 hours ago
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            
            # Get daily active users (unique users who created reports in last 24 hours)
            daily_users_result = supabase.rpc(
                'get_daily_active_users',
                {'since_timestamp': yesterday}
            ).execute()
            
            daily_active_users = 0
            if daily_users_result.data is not None:
                daily_active_users = daily_users_result.data
            else:
                # Fallback: count distinct patient_ids from recent reports
                reports_result = supabase.table("medical_reports")\
                    .select("patient_id")\
                    .gte("created_at", yesterday)\
                    .execute()
                
                if reports_result.data:
                    unique_patients = set(r["patient_id"] for r in reports_result.data)
                    daily_active_users = len(unique_patients)
            
            # Get total screenings (all medical reports)
            total_result = supabase.table("medical_reports")\
                .select("id", count="exact")\
                .execute()
            
            total_screenings = total_result.count if total_result.count is not None else 0
            
            # Get average processing time from audit logs
            # Processing times are logged in audit_logs with action="ai_processing"
            processing_logs = supabase.table("audit_logs")\
                .select("metadata")\
                .eq("action", "ai_processing")\
                .execute()
            
            average_processing_time = 0.0
            if processing_logs.data and len(processing_logs.data) > 0:
                processing_times = []
                for log in processing_logs.data:
                    metadata = log.get("metadata", {})
                    total_time = metadata.get("total_processing_time")
                    if total_time is not None:
                        processing_times.append(float(total_time))
                
                if processing_times:
                    average_processing_time = sum(processing_times) / len(processing_times)
            
            metrics = {
                "daily_active_users": daily_active_users,
                "total_screenings": total_screenings,
                "average_processing_time": round(average_processing_time, 2)
            }
            
            logger.info(f"Generated dashboard metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error generating dashboard metrics: {str(e)}", exc_info=True)
            # Return default values on error
            return {
                "daily_active_users": 0,
                "total_screenings": 0,
                "average_processing_time": 0.0
            }
    
    async def get_usage_pattern_statistics(self) -> Dict:
        """
        Get usage pattern statistics
        Requirements: 20.5
        
        Property 67: Usage Pattern Statistics
        For any usage analysis query, the system should provide statistics on 
        most common cancer types detected and geographic distribution of users.
        
        Returns:
            Dict containing:
            - most_common_cancer_types: List of cancer types with detection counts
            - geographic_distribution: List of locations with user counts
        """
        if settings.demo_mode:
            # Return demo data
            return {
                "most_common_cancer_types": [
                    {"cancer_type": "Melanoma", "count": 45},
                    {"cancer_type": "Basal Cell Carcinoma", "count": 38},
                    {"cancer_type": "Squamous Cell Carcinoma", "count": 27},
                    {"cancer_type": "Benign", "count": 46}
                ],
                "geographic_distribution": [
                    {"location": "California", "count": 32},
                    {"location": "New York", "count": 28},
                    {"location": "Texas", "count": 24},
                    {"location": "Florida", "count": 20}
                ]
            }
        
        try:
            # Get most common cancer types from AI predictions
            reports_result = supabase.table("medical_reports")\
                .select("ai_prediction")\
                .execute()
            
            cancer_type_counts = {}
            
            if reports_result.data:
                for report in reports_result.data:
                    ai_prediction = report.get("ai_prediction", {})
                    predictions = ai_prediction.get("predictions", [])
                    
                    # Find the cancer type with highest probability
                    if predictions:
                        max_prediction = max(predictions, key=lambda p: p.get("probability", 0))
                        cancer_type = max_prediction.get("type", "unknown")
                        
                        if cancer_type in cancer_type_counts:
                            cancer_type_counts[cancer_type] += 1
                        else:
                            cancer_type_counts[cancer_type] = 1
            
            # Sort by count descending
            most_common_cancer_types = [
                {"cancer_type": cancer_type, "count": count}
                for cancer_type, count in sorted(
                    cancer_type_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ]
            
            # Get geographic distribution from doctors table
            # (using doctor locations as proxy for user distribution)
            doctors_result = supabase.table("doctors")\
                .select("lat, lng, clinic_name")\
                .execute()
            
            geographic_distribution = []
            
            if doctors_result.data:
                # Group by approximate location (rounded coordinates)
                location_counts = {}
                
                for doctor in doctors_result.data:
                    lat = doctor.get("lat")
                    lng = doctor.get("lng")
                    
                    if lat is not None and lng is not None:
                        # Round to 1 decimal place for grouping nearby locations
                        location_key = f"{round(float(lat), 1)},{round(float(lng), 1)}"
                        
                        if location_key in location_counts:
                            location_counts[location_key] += 1
                        else:
                            location_counts[location_key] = 1
                
                # Convert to list format
                geographic_distribution = [
                    {
                        "location": location,
                        "user_count": count,
                        "latitude": float(location.split(',')[0]),
                        "longitude": float(location.split(',')[1])
                    }
                    for location, count in sorted(
                        location_counts.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                ]
            
            statistics = {
                "most_common_cancer_types": most_common_cancer_types,
                "geographic_distribution": geographic_distribution
            }
            
            logger.info(f"Generated usage pattern statistics: {len(most_common_cancer_types)} cancer types, {len(geographic_distribution)} locations")
            return statistics
            
        except Exception as e:
            logger.error(f"Error generating usage pattern statistics: {str(e)}", exc_info=True)
            # Return empty data on error
            return {
                "most_common_cancer_types": [],
                "geographic_distribution": []
            }
    
    async def generate_weekly_health_report(self) -> Dict:
        """
        Generate weekly platform health report
        Requirements: 20.6
        
        Property 68: Weekly Health Report Generation
        For any week, the system should generate a summary report containing 
        platform health metrics (uptime, error rates, user activity).
        
        Returns:
            Dict containing:
            - week_start: Start date of the week
            - week_end: End date of the week
            - total_users: Total number of users
            - active_users: Number of active users this week
            - total_screenings: Total screenings performed this week
            - error_rate: Error rate percentage for the week
            - average_response_time: Average API response time
            - top_cancer_types: Most detected cancer types this week
            - system_uptime: Estimated system uptime percentage
        """
        try:
            from datetime import timedelta
            
            # Calculate week boundaries
            week_end = datetime.utcnow()
            week_start = week_end - timedelta(days=7)
            
            week_start_iso = week_start.isoformat()
            week_end_iso = week_end.isoformat()
            
            # Get total users
            total_users_result = supabase.table("profiles")\
                .select("id", count="exact")\
                .execute()
            
            total_users = total_users_result.count if total_users_result.count is not None else 0
            
            # Get active users this week (users who created reports)
            active_users_result = supabase.table("medical_reports")\
                .select("patient_id")\
                .gte("created_at", week_start_iso)\
                .lte("created_at", week_end_iso)\
                .execute()
            
            active_users = 0
            if active_users_result.data:
                unique_patients = set(r["patient_id"] for r in active_users_result.data)
                active_users = len(unique_patients)
            
            # Get total screenings this week
            screenings_result = supabase.table("medical_reports")\
                .select("id", count="exact")\
                .gte("created_at", week_start_iso)\
                .lte("created_at", week_end_iso)\
                .execute()
            
            total_screenings = screenings_result.count if screenings_result.count is not None else 0
            
            # Get error rate for the week
            api_requests_result = supabase.table("audit_logs")\
                .select("metadata")\
                .eq("action", "api_request")\
                .gte("created_at", week_start_iso)\
                .lte("created_at", week_end_iso)\
                .execute()
            
            error_rate = 0.0
            if api_requests_result.data and len(api_requests_result.data) > 0:
                total_requests = len(api_requests_result.data)
                error_count = sum(
                    1 for req in api_requests_result.data
                    if req.get("metadata", {}).get("is_error", False)
                )
                error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0.0
            
            # Get average response time for the week
            response_times = []
            if api_requests_result.data:
                for req in api_requests_result.data:
                    metadata = req.get("metadata", {})
                    response_time = metadata.get("response_time")
                    if response_time is not None:
                        response_times.append(float(response_time))
            
            average_response_time = 0.0
            if response_times:
                average_response_time = sum(response_times) / len(response_times)
            
            # Get top cancer types detected this week
            reports_result = supabase.table("medical_reports")\
                .select("ai_prediction")\
                .gte("created_at", week_start_iso)\
                .lte("created_at", week_end_iso)\
                .execute()
            
            cancer_type_counts = {}
            if reports_result.data:
                for report in reports_result.data:
                    ai_prediction = report.get("ai_prediction", {})
                    predictions = ai_prediction.get("predictions", [])
                    
                    if predictions:
                        max_prediction = max(predictions, key=lambda p: p.get("probability", 0))
                        cancer_type = max_prediction.get("type", "unknown")
                        
                        if cancer_type in cancer_type_counts:
                            cancer_type_counts[cancer_type] += 1
                        else:
                            cancer_type_counts[cancer_type] = 1
            
            top_cancer_types = [
                {"cancer_type": cancer_type, "count": count}
                for cancer_type, count in sorted(
                    cancer_type_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]  # Top 5
            ]
            
            # Calculate system uptime (based on successful vs failed requests)
            # Uptime = (successful requests / total requests) * 100
            system_uptime = 100.0 - error_rate if api_requests_result.data else 100.0
            
            report = {
                "week_start": week_start_iso,
                "week_end": week_end_iso,
                "total_users": total_users,
                "active_users": active_users,
                "total_screenings": total_screenings,
                "error_rate": round(error_rate, 2),
                "average_response_time": round(average_response_time, 3),
                "top_cancer_types": top_cancer_types,
                "system_uptime": round(system_uptime, 2)
            }
            
            logger.info(
                f"Generated weekly health report: "
                f"{total_screenings} screenings, {active_users} active users, "
                f"{error_rate:.2f}% error rate, {system_uptime:.2f}% uptime"
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating weekly health report: {str(e)}", exc_info=True)
            # Return default values on error
            return {
                "week_start": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                "week_end": datetime.utcnow().isoformat(),
                "total_users": 0,
                "active_users": 0,
                "total_screenings": 0,
                "error_rate": 0.0,
                "average_response_time": 0.0,
                "top_cancer_types": [],
                "system_uptime": 100.0,
                "error": str(e)
            }
