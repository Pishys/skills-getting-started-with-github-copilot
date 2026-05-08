"""
Tests for the FastAPI app using AAA (Arrange-Act-Assert) pattern
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

@pytest.fixture
def client():
    """Create a TestClient for the app"""
    return TestClient(app)


class TestRoot:
    """Tests for root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to /static/index.html"""
        # Arrange: No special setup needed
        
        # Act: Make GET request to root
        response = client.get("/", follow_redirects=False)
        
        # Assert: Check redirect status and location
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for get_activities endpoint"""
    
    def test_get_activities_returns_dict(self, client):
        """Test that get_activities returns a dictionary"""
        # Arrange: No special setup needed
        
        # Act: Make GET request to activities
        response = client.get("/activities")
        
        # Assert: Check response status and type
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that activities include expected activity names"""
        # Arrange: Define expected activities
        expected_activities = ["Chess Club", "Programming Class", "Gym Class", 
                             "Basketball Team", "Soccer Club", "Art Class", 
                             "Drama Club", "Debate Team", "Science Club"]
        
        # Act: Make GET request to activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Check that all expected activities are present
        for activity in expected_activities:
            assert activity in activities
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        # Arrange: Define required fields
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act: Make GET request to activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Check that each activity has all required fields
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"


class TestSignup:
    """Tests for signup endpoint"""
    
    def test_signup_valid_activity(self, client):
        """Test signing up for a valid activity"""
        # Arrange: Define test data
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act: Make POST request to signup
        response = client.post(f"/activities/{activity_name}/signup", 
                              params={"email": email})
        
        # Assert: Check response status and content
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
    
    def test_signup_activity_not_found(self, client):
        """Test signing up for non-existent activity"""
        # Arrange: Define test data for non-existent activity
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act: Make POST request to signup
        response = client.post(f"/activities/{activity_name}/signup",
                              params={"email": email})
        
        # Assert: Check error response
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self, client):
        """Test that duplicate signup returns 400"""
        # Arrange: Define test data and perform initial signup
        activity_name = "Chess Club"
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/{activity_name}/signup",
                               params={"email": email})
        assert response1.status_code == 200
        
        # Act: Attempt duplicate signup
        response2 = client.post(f"/activities/{activity_name}/signup",
                               params={"email": email})
        
        # Assert: Check error response for duplicate
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_updates_participant_list(self, client):
        """Test that signup actually updates the participants list"""
        # Arrange: Define test data
        activity_name = "Programming Class"
        email = "participant@mergington.edu"
        
        # Get initial activities
        response_before = client.get("/activities")
        activities_before = response_before.json()
        participants_before = set(activities_before[activity_name]["participants"])
        
        # Act: Sign up
        client.post(f"/activities/{activity_name}/signup",
                   params={"email": email})
        
        # Assert: Check that email was added to participants
        response_after = client.get("/activities")
        activities_after = response_after.json()
        participants_after = set(activities_after[activity_name]["participants"])
        
        assert email in participants_after
        assert len(participants_after) == len(participants_before) + 1


class TestUnregister:
    """Tests for unregister endpoint"""
    
    def test_unregister_valid_student(self, client):
        """Test unregistering a signed-up student"""
        # Arrange: Define test data and sign up first
        activity_name = "Drama Club"
        email = "unreg_student@mergington.edu"
        
        # First sign up
        client.post(f"/activities/{activity_name}/signup",
                   params={"email": email})
        
        # Act: Unregister
        response = client.delete(f"/activities/{activity_name}/unregister",
                                params={"email": email})
        
        # Assert: Check success response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
    
    def test_unregister_activity_not_found(self, client):
        """Test unregistering from non-existent activity"""
        # Arrange: Define test data for non-existent activity
        activity_name = "Fake Activity"
        email = "student@mergington.edu"
        
        # Act: Make DELETE request to unregister
        response = client.delete(f"/activities/{activity_name}/unregister",
                                params={"email": email})
        
        # Assert: Check error response
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_student_not_registered(self, client):
        """Test unregistering a student who is not signed up"""
        # Arrange: Define test data
        activity_name = "Soccer Club"
        email = "notstudent@mergington.edu"
        
        # Act: Make DELETE request to unregister
        response = client.delete(f"/activities/{activity_name}/unregister",
                                params={"email": email})
        
        # Assert: Check error response
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_removes_from_participant_list(self, client):
        """Test that unregister actually removes the student"""
        # Arrange: Define test data and sign up
        activity_name = "Science Club"
        email = "remove_me@mergington.edu"
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup",
                   params={"email": email})
        
        # Get participants before
        response_before = client.get("/activities")
        participants_before = set(response_before.json()[activity_name]["participants"])
        assert email in participants_before
        
        # Act: Unregister
        client.delete(f"/activities/{activity_name}/unregister",
                     params={"email": email})
        
        # Assert: Check that email was removed
        response_after = client.get("/activities")
        participants_after = set(response_after.json()[activity_name]["participants"])
        
        assert email not in participants_after
        assert len(participants_after) == len(participants_before) - 1