from common.models import Address, Comment, CommentFiles, User
from django.contrib import admin

# Custom User Admin to handle user creation and email sending
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.crypto import get_random_string
from .models import User, Address, Comment, CommentFiles 

class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "is_active", "is_staff")
    search_fields = ("email",)
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password", "profile_pic")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email",  "is_active", "is_staff")}
         ),
    )

    def save_model(self, request, obj, form, change):
        """
        When creating a new user from the admin:
        - Generate a secure temporary password
        - Save the user with that password
        - Send an invite email with login details
        """
        if not change:  # new user
            temp_password = get_random_string(length=8)
            obj.set_password(temp_password)
            super().save_model(request, obj, form, change)
            send_mail(
                subject="Your account has been created",
                message=f"Your temporary password is: {temp_password}",
                from_email=None,
                recipient_list=[obj.email],
            )
        else:
            # Existing user
            super().save_model(request, obj, form, change)

# End custom User Admin to handle user creation and email sending


# Register your models here.

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Comment)
admin.site.register(CommentFiles)

# common/admin.py





