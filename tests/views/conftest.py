import pytest
from unittest.mock import MagicMock, patch
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory, force_authenticate
from common.views import AdminUserCreationViewSet
from tests.views import constants as const

@pytest.fixture
def view_instance():
    """Create a fake view instance with fake request and user."""
    view = AdminUserCreationViewSet() 
    view.request = MagicMock()
    view.request.user = MagicMock()
    yield view

@pytest.fixture
def authenticated_request():
    """Create an authenticated request with a mock user."""
    user = MagicMock()
    factory = APIRequestFactory()
    request = factory.post(const.PASSWORD_URL,{
        'current_password': const.OLD_PASS,
        'new_password': const.NEW_PASS
    })
    force_authenticate(request, user=user, token='abcd1234')
    yield request, user

@pytest.fixture
def connection_parameters():
    """Fixture to provide database connection parameters."""
    yield const.PASSWORD_URL, const.OLD_PASS, const.NEW_PASS, const.EMPTY_PAYLOAD
    
    