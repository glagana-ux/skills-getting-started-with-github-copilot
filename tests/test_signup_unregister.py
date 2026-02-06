"""Tests for signup and unregister endpoints"""
import pytest


def test_signup_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]


def test_signup_adds_participant(client):
    """Test that signup actually adds the participant to the activity"""
    # Get initial participant count
    response = client.get("/activities")
    initial_count = len(response.json()["Chess Club"]["participants"])
    
    # Sign up a new student
    client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
    
    # Verify participant was added
    response = client.get("/activities")
    final_count = len(response.json()["Chess Club"]["participants"])
    assert final_count == initial_count + 1
    assert "newstudent@mergington.edu" in response.json()["Chess Club"]["participants"]


def test_signup_nonexistent_activity(client):
    """Test signup to non-existent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_registered(client):
    """Test that signup fails if student is already registered"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_full(client):
    """Test that signup fails when activity is at max capacity"""
    # Get an activity with limited spots
    response = client.get("/activities")
    math_club = response.json()["Math Olympiad"]  # max_participants: 10
    
    # Fill the activity to capacity
    with_new_participants = [
        "participant1@mergington.edu",
        "participant2@mergington.edu",
        "participant3@mergington.edu",
        "participant4@mergington.edu",
        "participant5@mergington.edu",
        "participant6@mergington.edu",
        "participant7@mergington.edu",
        "participant8@mergington.edu"
    ]
    
    for email in with_new_participants:
        client.post(f"/activities/Math%20Olympiad/signup?email={email}")
    
    # Try to signup when full
    response = client.post(
        "/activities/Math%20Olympiad/signup?email=overflow@mergington.edu"
    )
    assert response.status_code == 400
    assert "full" in response.json()["detail"]


def test_unregister_success(client):
    """Test successful unregister from an activity"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "michael@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]


def test_unregister_removes_participant(client):
    """Test that unregister actually removes the participant"""
    # Verify participant exists
    response = client.get("/activities")
    assert "michael@mergington.edu" in response.json()["Chess Club"]["participants"]
    initial_count = len(response.json()["Chess Club"]["participants"])
    
    # Unregister
    client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
    
    # Verify participant was removed
    response = client.get("/activities")
    final_count = len(response.json()["Chess Club"]["participants"])
    assert final_count == initial_count - 1
    assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]


def test_unregister_nonexistent_activity(client):
    """Test unregister from non-existent activity returns 404"""
    response = client.delete(
        "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_registered(client):
    """Test unregister fails if student is not registered"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_signup_then_unregister(client):
    """Test complete workflow: signup then unregister"""
    email = "workflow@mergington.edu"
    activity = "Basketball%20Team"
    
    # Sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    # Verify participant is there
    response = client.get("/activities")
    assert email in response.json()["Basketball Team"]["participants"]
    
    # Unregister
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    
    # Verify participant is removed
    response = client.get("/activities")
    assert email not in response.json()["Basketball Team"]["participants"]
