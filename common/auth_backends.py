# common/auth_backends.py
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend:
    """
    Authenticate with either username OR email in a single 'username' field.
    Robust to custom user models (USERNAME_FIELD may be 'email').
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        DRF SimpleJWT's default login serializer sends 'username'.
        If you build your own serializer and call authenticate(identifier=..., password=...),
        Django will still pass it here as 'username' or in kwargs.
        """
        identifier = username or kwargs.get("identifier") or kwargs.get(User.USERNAME_FIELD)
        if not identifier or not password:
            return None

        # Build a flexible query over available fields (email, username, USERNAME_FIELD)
        fields_in_model = {f.name for f in User._meta.get_fields()}
        candidate_fields = {User.USERNAME_FIELD, "email", "username"} & fields_in_model

        q = Q()
        for f in candidate_fields:
            q |= Q(**{f"{f}__iexact": identifier})

        user = User.objects.filter(q).first()
        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
