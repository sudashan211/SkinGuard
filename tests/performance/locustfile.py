"""
Load testing configuration for SkinGuard API using Locust

This file defines load testing scenarios to test API endpoints under load.
Run with: locust -f tests/performance/locustfile.py --host=http://localhost:8000

Validates: Requirements 20.1, 20.2
"""

from locust import HttpUser, task, between, events
import random
import json
import time
from io import BytesIO
from PIL import Image


class SkinGuardUser(HttpUser):
    """
    Simulates a typical SkinGuard user performing various actions
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """
        Called when a simulated user starts
        Login and get authentication token
        """
        # Register/login as a test user
        self.patient_id = None
        self.doctor_id = None
        self.auth_token = None
        
        # Try to login
        response = self.client.post("/api/auth/login", json={
            "email": f"loadtest_{random.randint(1, 1000)}@test.com",
            "password": "testpassword123"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            self.patient_id = data.get("user_id")
    
    def get_auth_headers(self):
        """Get authorization headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    @task(3)
    def view_reports(self):
        """
        Most common task: View medical reports
        Weight: 3 (happens 3x more often than other tasks)
        """
        with self.client.get(
            "/api/reports",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="GET /api/reports"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # Unauthorized is expected for some users
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def upload_image(self):
        """
        Upload and analyze skin image
        Weight: 1 (less frequent, more resource intensive)
        """
        # Create a test image
        img = Image.new('RGB', (512, 512), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {'image': ('test.jpg', img_bytes, 'image/jpeg')}
        
        with self.client.post(
            "/api/analyze-skin",
            files=files,
            headers=self.get_auth_headers(),
            catch_response=True,
            name="POST /api/analyze-skin",
            timeout=30  # AI analysis can take time
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.success()  # Expected for unauthorized
            elif response.status_code == 403:
                response.success()  # Expected for NSFW rejection
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def find_nearby_doctors(self):
        """
        Search for nearby doctors
        Weight: 2 (common task)
        """
        # Random coordinates
        lat = random.uniform(40.0, 41.0)
        lng = random.uniform(-74.0, -73.0)
        
        with self.client.get(
            f"/api/doctors/nearby?lat={lat}&lng={lng}&radius=10",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="GET /api/doctors/nearby"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def view_appointments(self):
        """
        View user appointments
        Weight: 1
        """
        with self.client.get(
            "/api/appointments",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="GET /api/appointments"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def health_check(self):
        """
        Health check endpoint
        Weight: 1
        """
        with self.client.get(
            "/health",
            catch_response=True,
            name="GET /health"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


class DoctorUser(HttpUser):
    """
    Simulates a doctor user accessing reports and managing appointments
    """
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login as doctor"""
        self.auth_token = None
        
        response = self.client.post("/api/auth/login", json={
            "email": f"doctor_{random.randint(1, 100)}@test.com",
            "password": "testpassword123"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
    
    def get_auth_headers(self):
        """Get authorization headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    @task(3)
    def view_pending_reports(self):
        """View pending patient reports"""
        with self.client.get(
            "/api/doctors/reports/pending",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="GET /api/doctors/reports/pending"
        ) as response:
            if response.status_code in [200, 401, 403]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def view_appointments(self):
        """View doctor appointments"""
        with self.client.get(
            "/api/appointments",
            headers=self.get_auth_headers(),
            catch_response=True,
            name="GET /api/appointments (doctor)"
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


# Event listeners for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    print("\n" + "="*60)
    print("LOAD TEST STARTED")
    print("="*60)
    print(f"Host: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    print("\n" + "="*60)
    print("LOAD TEST COMPLETED")
    print("="*60)
    
    stats = environment.stats
    
    print("\nREQUEST STATISTICS:")
    print(f"  Total requests: {stats.total.num_requests}")
    print(f"  Total failures: {stats.total.num_failures}")
    print(f"  Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"  Min response time: {stats.total.min_response_time:.2f}ms")
    print(f"  Max response time: {stats.total.max_response_time:.2f}ms")
    print(f"  Requests per second: {stats.total.total_rps:.2f}")
    
    print("\nPERFORMANCE TARGETS:")
    avg_response_time = stats.total.avg_response_time
    if avg_response_time < 500:
        print(f"  ✓ Average response time: {avg_response_time:.2f}ms (target: <500ms)")
    else:
        print(f"  ✗ Average response time: {avg_response_time:.2f}ms (target: <500ms)")
    
    failure_rate = (stats.total.num_failures / stats.total.num_requests * 100) if stats.total.num_requests > 0 else 0
    if failure_rate < 1:
        print(f"  ✓ Failure rate: {failure_rate:.2f}% (target: <1%)")
    else:
        print(f"  ✗ Failure rate: {failure_rate:.2f}% (target: <1%)")
    
    print("="*60 + "\n")


# Custom load test shapes
from locust import LoadTestShape

class StepLoadShape(LoadTestShape):
    """
    A step load shape that gradually increases load
    
    Step 1: 10 users for 60 seconds
    Step 2: 25 users for 60 seconds
    Step 3: 50 users for 60 seconds
    Step 4: 100 users for 60 seconds
    """
    
    step_time = 60
    step_load = 10
    spawn_rate = 5
    time_limit = 240
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > self.time_limit:
            return None
        
        current_step = run_time // self.step_time
        return (self.step_load * (current_step + 1), self.spawn_rate)


if __name__ == "__main__":
    print("""
    Load Testing for SkinGuard API
    
    Usage:
        # Basic load test
        locust -f tests/performance/locustfile.py --host=http://localhost:8000
        
        # Headless mode with specific users and duration
        locust -f tests/performance/locustfile.py --host=http://localhost:8000 \\
               --users 50 --spawn-rate 5 --run-time 5m --headless
        
        # With step load shape
        locust -f tests/performance/locustfile.py --host=http://localhost:8000 \\
               --headless --load-shape StepLoadShape
    
    Then open http://localhost:8089 to view the web UI
    """)
