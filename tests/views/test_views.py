import pytest
from common import status
from tests.views import constants as const 
from unittest.mock import MagicMock, patch
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory, force_authenticate
from common.views import AdminUserCreationViewSet, MePasswordView, AdminPasswordResetView
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient




user = get_user_model()

#========================== AdminUserCreationViewSet Tests ==============================================#
class TestAdminUserCreationViewSet:
    """Tests for AdminUserCreationViewSet."""
    
    def test_TB001_get_queryset_superuser(self, view_instance, mocker):
        """Test that a superuser gets ALL users ordered by last_login."""
        #  ========================= Arrange: make the fake user a superuser ========================
        view_instance.request.user.is_superuser = True
        view_instance.request.user.is_staff = False
        
        # Create a fake queryset and patch the User.objects.all() to return it
        fake_queryset = MagicMock()
        mocker.patch("common.views.User.objects.all", return_value=fake_queryset)
        
        # Make fake queryset.order_by() return a known value
        fake_queryset.order_by.return_value = "ALL_USERS"
        
        # ========================= Act: call the method we are testing =============================
        result = view_instance.get_queryset()
        
        # ========================= Assert: check that we got the expected result ===================
        assert result == "ALL_USERS"
        fake_queryset.order_by.assert_called_once_with("-last_login")

    def test_TB002_get_queryset_no_profile(self, view_instance, mocker):
        """Test that a non-superuser without a profile raises PermissionDenied."""
        # Arrange: make the fake user a (non-superuser/non-staff)
        user = view_instance.request.user
        user.is_superuser = False
        user.is_staff = False
        
        # Patch Profile.objects.filter() to return an object whose .first() is None
        fake_profile_qs = MagicMock()
        fake_profile_qs.first.return_value = None
        mocker.patch("common.views.Profile.objects.filter", return_value=fake_profile_qs)
        

        # Act & Assert: check that calling get_queryset raises PermissionDenied
        with pytest.raises(PermissionDenied) as exe:
            view_instance.get_queryset()
        assert "No profile associated with user." in str(exe.value)

# ============================= MePasswordView Tests ====================================================#
class TestMEPasswordView:
    def test_TB003_me_password_view_change_password(self, authenticated_request):
        """Test MePasswordView to ensure users can change their own password."""
        # ================ Arrange: create a mock user and request =================

        request, user = authenticated_request
        # patch the serialier to simulate valid data
        with patch('common.views.PasswordChangeSerializer') as mock_serializer_class:
            mock_serializer = MagicMock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.validated_data = {"new_password": "new_pass"}
            mock_serializer_class.return_value = mock_serializer

            # ================ Act: create the view and call the post method =================
            view = MePasswordView.as_view()
            response = view(request)

            # ================ Assert: check that the response is 200 OK and password was set =================
            assert response.status_code == 200
            mock_serializer_class.assert_called_once()
            mock_serializer.is_valid.assert_called_once_with(raise_exception=True)
            user.set_password.assert_called_once_with("new_pass")
            user.save.assert_called_once()

    def test_TB004_me_password_view_empty_payload(self, connection_parameters):
        """Test MePasswordView with empty payload returns 400."""
        # ================ Arrange: create a mock user and request with empty data =================
        password_url, old_pass, new_pass, empty_payload = connection_parameters
        user = MagicMock()
        factory = APIRequestFactory()
        request = factory.post(password_url, empty_payload)
        force_authenticate(request, user=user)

        # ================ Act: create the view and call the post method =================
        view = MePasswordView.as_view()
        response = view(request)

        # ================ Assert: check that the response is 400 Bad Request =================
        assert response.status_code == 400
    
    def test_TB005_me_password_view_invalid_current_password(self, authenticated_request):
        """Test MePasswordView with incorrect current password returns 400."""
        # ================ Arrange: create a mock user and request =================
        request, user = authenticated_request
        user.check_password.return_value = False  # Simulate wrong current password

        # ================ Act: create the view and call the post method =================
        view = MePasswordView.as_view()
        response = view(request)

        # ================ Assert: check that the response is 400 Bad Request =================
        assert response.status_code == 400
        assert "Incorrect password." in str(response.data)

# ============================= AdminPasswordResetView Tests ====================================================#
@pytest.mark.django_db
class TestAdminPasswordResetView:
    """
    POST /api/users/{user_id}/password/ (admin only)  {new_password}
    """
    def test_TB006_Post_password_reset_unauthenticated_user(self):
        """Test that an unauthenticated user cannot reset another user's password."""
        # ================ Arrange: create a mock user and request =================
        test_user01 = user.objects.create_user(
            email=const.TEST_EMAIL, 
            password=const.OLD_PASS
            )
        client = APIClient()
        # ================ Act: create the view and call the post method =================
        response = client.post(
            const.URL.format(user_id=test_user01.id),
            {'new_password': const.NEW_PASS},
            format='json'
        )
            
        # ================ Assert: check that the response is 401 Unauthorized =================
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        assert "Authentication credentials were not provided." in str(response.data)
        
    def test_TB007_Post_admin_password_reset_non_admin_user(self):
        """Test that a non-admin user cannot reset another user's password."""
        # ================ Arrange: create a mock user and request =================
        test_user01 = user.objects.create_user(
            email=const.TEST_EMAIL, 
            password=const.OLD_PASS
        )
        test_user02 = user.objects.create_user(
            email=const.TEST_EMAIL_2, 
            password=const.OLD_PASS_2
        )
        client = APIClient()
        client.force_authenticate(user=test_user02)

        # ================ Act: create the view and call the post method =================
        response = client.post(
            const.URL.format(user_id=test_user01.id),
            {'new_password': const.NEW_PASS},
            format='json'
        )

        # ================ Assert: check that the response is 403 Forbidden =================
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "You do not have permission to perform this action." in str(response.data)