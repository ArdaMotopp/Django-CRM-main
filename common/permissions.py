from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOrgAdmin(BasePermission):
    """
    Company admin can manage company users.
    - True if:
      * superuser, or staff (platform-level), OR
      * user.profile.is_organization_admin is True
    """
    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False

        # Platform admins always pass
        if getattr(u, "is_superuser", False) or getattr(u, "is_staff", False):
            return True

        # Org admin via Profile
        prof = getattr(u, "profile", None)
        return bool(prof and prof.is_organization_admin)


class IsSelfOrOrgAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "is_staff", False):
            return True
        return obj == request.user
