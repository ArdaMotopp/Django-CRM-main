import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from common.models import Profile, Org
from teams.models import Teams


User = get_user_model()

@pytest.mark.django_db
def test_get_teams_and_users_with_token():
    # 1. organization
    org = Org.objects.create(name="Test Org")

    # 2. user + profile
    user = User.objects.create_user(email="ali@test.com", password="testpass123")
    Profile.objects.create(user=user, org=org, is_active=True)

    # 3. team
    Teams.objects.create(name="Team A", org=org)

    client = APIClient()

    # 4. Receiving token
    client.force_authenticate(user=user)

    # token_resp = client.post(
    #     "/api/auth/login/", {"identifier": "ali@test.com", "password": "testpass123"}, 
    #     format="json")
    #access_token = resp.data["access"]

    # 5. Adding token to header
    #client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    # 6. Calling actual endpoint
    resp = client.get("/api/teams-user/")
    assert resp.status_code == 200

    data = resp.json()
    assert "teams" in data
    assert "profiles" in data
    assert data["teams"][0]["name"] == "Team A"
    assert data["profiles"][0]["user"]["email"] == "ali@test.com"
