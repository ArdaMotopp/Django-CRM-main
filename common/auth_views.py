from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()   # email OR username
    password = serializers.CharField()

@extend_schema(
    tags=["auth"],
    request=LoginSerializer,               # <-- tells Swagger the request body
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="LoginResponse",
                fields={
                    "access": serializers.CharField(),
                    "refresh": serializers.CharField(),
                },
            ),
            description="JWT tokens",
        ),
        401: OpenApiResponse(description="Invalid credentials"),
        403: OpenApiResponse(description="User inactive"),
    },
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=ser.validated_data["identifier"],
            password=ser.validated_data["password"],
        )
        if not user:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({"detail": "User inactive."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)}, status=200)
