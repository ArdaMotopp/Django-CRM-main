import secrets
import requests
from rest_framework import serializers

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from common.serializer import SocialLoginSerializer

# App imports
from accounts.models import Account, Contact, Tags
from accounts.serializer import AccountSerializer
from cases.models import Case
from cases.serializer import CaseSerializer
from common import swagger_params1
from common.models import APISettings, Document, Org, Profile, User
from common.serializer import (
    SocialLoginSerializer,
    OrgProfileCreateSerializer,
    CreateProfileSerializer,
    ShowOrganizationListSerializer,
    ProfileSerializer,
    DocumentSerializer,
    DocumentCreateSerializer,
    DocumentCreateSwaggerSerializer,
    DocumentEditSwaggerSerializer,
    APISettingsSerializer,
    APISettingsListSerializer,
    APISettingsSwaggerSerializer,
    UserReadSerializer,
    UserAdminWriteSerializer,
    PasswordChangeSerializer,
    AdminPasswordResetSerializer,
)
from common.tasks import (
    resend_activation_link_to_user,
    send_email_to_new_user,
    send_email_to_reset_password,
    send_email_user_delete,
)
from common.serializer import (
    SocialLoginSerializer,
    PasswordChangeSerializer,
    AdminPasswordResetSerializer,
)

from contacts.serializer import ContactSerializer
from leads.models import Lead
from leads.serializer import LeadSerializer
from opportunity.models import Opportunity
from opportunity.serializer import OpportunitySerializer
from teams.models import Teams
from teams.serializer import TeamsSerializer
from .permissions import IsOrgAdmin, IsSelfOrOrgAdmin
from .serializer import TeamsAndProfilesResponseSerializer

User = get_user_model()


# ------------------ Admin User Creation ------------------
@extend_schema(tags=["admin-user-creation"])
class AdminUserCreationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOrgAdmin)
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return User.objects.all().order_by("-last_login")

        prof = Profile.objects.filter(user=user).first()
        if not prof:
            raise PermissionDenied("No profile associated with user.")

        admin_org = getattr(prof, "org", None)
        if not (admin_org and prof.is_organization_admin):
            raise PermissionDenied("No organization admin context.")

        return (
            Profile.objects.filter(org=admin_org)
            .select_related("user")
            .order_by("-user__last_login")
        )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return UserAdminWriteSerializer
        return UserReadSerializer

    @extend_schema(request=UserAdminWriteSerializer, responses={201: UserReadSerializer})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if self.request.user.is_superuser or self.request.user.is_staff:
            serializer.save()
            return

        prof = Profile.objects.filter(user=self.request.user).first()
        if not prof or not (prof.org and prof.is_organization_admin):
            raise PermissionDenied("No organization admin context.")

        with transaction.atomic():
            user = serializer.save()
            Profile.objects.get_or_create(user=user, defaults={"org": prof.org})

    def perform_destroy(self, instance):
        instance.delete()


# ------------------ Teams & Users ------------------


class GetTeamsAndUsersView(APIView):
    """
    Returns all teams and active profiles for the current organization.
    """
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["users"],
        parameters=swagger_params1.organization_params,
        responses={200: TeamsAndProfilesResponseSerializer},
    )
    def get(self, request, *args, **kwargs):
        org = request.profile.org
        teams = Teams.objects.filter(org=org).order_by("-id")
        profiles = Profile.objects.filter(is_active=True, org=org).order_by("user__email")

        return Response({
            "teams": TeamsSerializer(teams, many=True).data,
            "profiles": ProfileSerializer(profiles, many=True).data,
        })

# ------------------ Dashboard ------------------
class ApiHomeView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(parameters=swagger_params1.organization_params)
    def get(self, request, format=None):
        accounts = Account.objects.filter(status="open", org=request.profile.org)
        contacts = Contact.objects.filter(org=request.profile.org)
        leads = Lead.objects.filter(org=request.profile.org).exclude(
            Q(status="converted") | Q(status="closed")
        )
        opportunities = Opportunity.objects.filter(org=request.profile.org)

        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            accounts = accounts.filter(
                Q(assigned_to=self.request.profile) | Q(created_by=self.request.profile.user)
            )
            contacts = contacts.filter(
                Q(assigned_to__id__in=self.request.profile)
                | Q(created_by=self.request.profile.user)
            )
            leads = leads.filter(
                Q(assigned_to__id__in=self.request.profile)
                | Q(created_by=self.request.profile.user)
            ).exclude(status="closed")
            opportunities = opportunities.filter(
                Q(assigned_to__id__in=self.request.profile)
                | Q(created_by=self.request.profile.user)
            )

        return Response(
            {
                "accounts_count": accounts.count(),
                "contacts_count": contacts.count(),
                "leads_count": leads.count(),
                "opportunities_count": opportunities.count(),
                "accounts": AccountSerializer(accounts, many=True).data,
                "contacts": ContactSerializer(contacts, many=True).data,
                "leads": LeadSerializer(leads, many=True).data,
                "opportunities": OpportunitySerializer(opportunities, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


# ------------------ Org Creation ------------------
class OrgProfileCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrgProfileCreateSerializer

    @extend_schema(description="Organization and profile creation API", request=OrgProfileCreateSerializer)
    def post(self, request, format=None):
        data = request.data
        data["api_key"] = secrets.token_hex(16)
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            org_obj = serializer.save()
            profile_obj = Profile.objects.create(
                user=request.user, org=org_obj, is_organization_admin=True, role="ADMIN"
            )
            return Response(
                {
                    "error": False,
                    "message": "New Org is Created.",
                    "org": self.serializer_class(org_obj).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response({"error": True, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description="Return ORG list associated with user")
    def get(self, request, format=None):
        profiles = Profile.objects.filter(user=request.user)
        serializer = ShowOrganizationListSerializer(profiles, many=True)
        return Response({"error": False, "profile_org_list": serializer.data}, status=status.HTTP_200_OK)


# ------------------ User Profile ------------------
class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(parameters=swagger_params1.organization_params)
    def get(self, request, format=None):
        return Response({"user_obj": ProfileSerializer(request.profile).data}, status=status.HTTP_200_OK)


# ------------------ Documents ------------------
# (keeping your DocumentListView, DocumentDetailView unchanged except imports cleanup)


# ------------------ API Settings ------------------
# (keeping your DomainList, DomainDetailView unchanged)


# ------------------ Google Login ------------------
class GoogleLoginView(APIView):
    """
    Login with Google OAuth2
    """
    @extend_schema(description="Login through Google", request=SocialLoginSerializer)
    def post(self, request):
        payload = {"access_token": request.data.get("token")}
        r = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", params=payload)
        data = r.json()
        if "error" in data:
            return Response({"message": "Invalid or expired Google token."}, status=status.HTTP_400_BAD_REQUEST)
        user, _ = User.objects.get_or_create(
            email=data["email"],
            defaults={
                "profile_pic": data.get("picture"),
                "password": make_password(BaseUserManager().make_random_password()),
            },
        )
        token = RefreshToken.for_user(user)
        return Response(
            {
                "username": user.email,
                "access_token": str(token.access_token),
                "refresh_token": str(token),
                "user_id": user.id,
            }
        )


# ------------------ User Management ------------------
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrgAdmin]
    lookup_field = "pk"

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Profile.objects.select_related("user").order_by("-user__last_login")
        prof = Profile.objects.filter(user=self.request.user).first()
        if not prof or not (prof.org and prof.is_organization_admin):
            raise PermissionDenied("No organization admin context.")
        return Profile.objects.filter(org=prof.org).select_related("user").order_by("-user__last_login")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return UserAdminWriteSerializer
        return UserReadSerializer

    def perform_create(self, serializer):
        if self.request.user.is_superuser or self.request.user.is_staff:
            serializer.save()
            return
        prof = getattr(self.request.user, "profile", None)
        admin_org = getattr(prof, "org", None)
        if not (prof and admin_org and prof.is_organization_admin):
            raise PermissionDenied("No organization admin context.")
        with transaction.atomic():
            user = serializer.save()
            Profile.objects.get_or_create(user=user, defaults={"org": admin_org})

    def perform_destroy(self, instance):
        instance.delete()


# ------------------ Password Management ------------------
class MePasswordView(APIView):
    """
    POST /api/users/me/password/  {current_password, new_password}
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    @extend_schema(
        tags=["users"],
        request=PasswordChangeSerializer,
        responses={200: dict},
        operation_id="user_change_own_password"
    )
    def post(self, request):
        ser = PasswordChangeSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        request.user.set_password(ser.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Password updated."}, status=status.HTTP_200_OK)


class AdminPasswordResetView(APIView):
    """
    POST /api/users/{user_id}/password/ (admin only) {new_password}
    """
    permission_classes = [IsAuthenticated, IsOrgAdmin]

    @extend_schema(
        tags=["users"],
        request=AdminPasswordResetSerializer,
        responses={200: dict},
        operation_id="admin_reset_user_password"
    )
    def post(self, request, user_id):
        if request.user.is_superuser or request.user.is_staff:
            target = get_object_or_404(User.objects, pk=user_id)
        else:
            prof = getattr(request.user, "profile", None)
            admin_org = getattr(prof, "org", None)
            if not (prof and admin_org and prof.is_organization_admin):
                raise PermissionDenied("No organization admin context.")
            target = get_object_or_404(User.objects.filter(profile__org=admin_org), pk=user_id)

        ser = AdminPasswordResetSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        target.set_password(ser.validated_data["new_password"])
        target.save()
        return Response({"detail": "Password reset."}, status=status.HTTP_200_OK)
