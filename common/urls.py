from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    AdminUserCreationViewSet,
    GetTeamsAndUsersView,
    ApiHomeView,
    OrgProfileCreateView,
    ProfileView,
    GoogleLoginView,
    UserViewSet,
    MePasswordView,
    AdminPasswordResetView,
)

app_name = "common"

urlpatterns = [
    path("admin-users/", AdminUserCreationViewSet.as_view({"get": "list", "post": "create"}), name="admin-user-list"),
    path("teams-users/", GetTeamsAndUsersView.as_view(), name="teams-users"),
    path("dashboard/", ApiHomeView.as_view(), name="dashboard"),
    path("org-profile/", OrgProfileCreateView.as_view(), name="org-profile"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    path("users/", UserViewSet.as_view({"get": "list", "post": "create"}), name="user-list"),
    path("me/password/", MePasswordView.as_view(), name="me-password"),
    path("users/<int:user_id>/password/", AdminPasswordResetView.as_view(), name="admin-password-reset"),

    # 🔑 JWT login & refresh
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
