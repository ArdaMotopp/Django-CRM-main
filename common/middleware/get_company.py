import jwt
from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.response import Response
from crum import get_current_user
from django.utils.functional import SimpleLazyObject

from common.models import Org, Profile, User


def get_actual_value(request):
    """
    Returns the actual user object so that request.user works
    even when wrapped in SimpleLazyObject.
    """
    if request.user is None:
        return None
    return request.user


class GetProfileAndOrg(object):
    """
    Middleware to attach request.profile (Profile instance)
    and to resolve the correct organisation from either:
      - 'org' header (UUID)
      - API key header
      - OR automatically fallback to the first active profile's org
        if no org header is provided (e.g. Swagger UI)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        try:
            request.profile = None
            user_id = None

            # 1️⃣ Decode JWT from Authorization header if present
            if request.headers.get("Authorization"):
                token1 = request.headers.get("Authorization")
                token = token1.split(" ")[1]  # get the token part only
                decoded = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO]
                )
                user_id = decoded.get("user_id")

            # 2️⃣ If an API key header is used instead
            api_key = request.headers.get("Token")
            if api_key:
                try:
                    organization = Org.objects.get(api_key=api_key)
                    request.META["org"] = organization.id
                    profile = Profile.objects.filter(
                        org=organization, role="ADMIN"
                    ).first()
                    if profile:
                        user_id = profile.user.id
                except Org.DoesNotExist:
                    raise AuthenticationFailed("Invalid API Key")

            # 3️⃣ Resolve profile/org
            if user_id is not None:
                org_header = request.headers.get("org")

                if org_header:
                    # org header provided: use it directly
                    profile = Profile.objects.get(
                        user_id=user_id, org=org_header, is_active=True
                    )
                    if profile:
                        request.profile = profile
                else:
                    # ➜ fallback when Swagger or another client does not send org header
                    #    use the first active profile for the user
                    profile = Profile.objects.filter(
                        user_id=user_id, is_active=True
                    ).first()
                    if profile:
                        request.profile = profile

        except Exception as exc:
            # Any failure (e.g. no profile found) should block the request
            # and return a 403 Forbidden to the client
            print("GetProfileAndOrg middleware error:", exc)
            raise PermissionDenied()
