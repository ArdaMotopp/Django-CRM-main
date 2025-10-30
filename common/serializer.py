import re
from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers
from common.models import (
    Address,
    APISettings,
    Attachments,
    Comment,
    Document,
    Org,
    Profile,
    User,
)
from teams.serializer import TeamsSerializer  # needed for TeamsAndProfilesResponseSerializer

# ------------------ Organization ------------------
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Org
        fields = ("id", "name", "api_key")


# ------------------ Comments ------------------
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class LeadCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "comment", "commented_on", "commented_by", "lead")


# ------------------ Org Profile ------------------
class OrgProfileCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)

    class Meta:
        model = Org
        fields = ["name"]

    def validate_name(self, name):
        if re.search(r"[~\!_.@#\$%\^&\*\ \(\)\+{}\":;'/\[\]]", name):
            raise serializers.ValidationError("Organization name should not contain special characters")
        if Org.objects.filter(name=name).exists():
            raise serializers.ValidationError("Organization already exists with this name")
        return name


class ShowOrganizationListSerializer(serializers.ModelSerializer):
    org = OrganizationSerializer()

    class Meta:
        model = Profile
        fields = (
            "role",
            "alternate_phone",
            "has_sales_access",
            "has_marketing_access",
            "is_organization_admin",
            "org",
        )


# ------------------ Address ------------------
class BillingAddressSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()

    def get_country(self, obj):
        return obj.get_country_display()

    class Meta:
        model = Address
        fields = ("address_line", "street", "city", "state", "postcode", "country")


# ------------------ User & Profile ------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "profile_pic"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "user_details",
            "role",
            "address",
            "has_marketing_access",
            "has_sales_access",
            "phone",
            "date_of_joining",
            "is_active",
        )


# ------------------ Attachments ------------------
class AttachmentsSerializer(serializers.ModelSerializer):
    file_path = serializers.SerializerMethodField()

    def get_file_path(self, obj):
        return obj.attachment.url if obj.attachment else None

    class Meta:
        model = Attachments
        fields = ["id", "created_by", "file_name", "created_at", "file_path"]


# ------------------ Documents ------------------
class DocumentSerializer(serializers.ModelSerializer):
    shared_to = ProfileSerializer(read_only=True, many=True)
    teams = serializers.SerializerMethodField()
    created_by = UserSerializer()
    org = OrganizationSerializer()

    def get_teams(self, obj):
        return obj.teams.all().values()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "document_file",
            "status",
            "shared_to",
            "teams",
            "created_at",
            "created_by",
            "org",
        ]


class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["title", "document_file", "status", "org"]

    def __init__(self, *args, **kwargs):
        request_obj = kwargs.pop("request_obj", None)
        super().__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.org = getattr(request_obj, "profile", None).org if request_obj else None


# ------------------ API Settings ------------------
class APISettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = APISettings
        fields = ("title", "website")

    def validate_website(self, website):
        if website and not (website.startswith("http://") or website.startswith("https://")):
            raise serializers.ValidationError("Please provide valid schema (http:// or https://)")
        return website


class APISettingsListSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()
    lead_assigned_to = ProfileSerializer(read_only=True, many=True)
    tags = serializers.SerializerMethodField()
    org = OrganizationSerializer()

    def get_tags(self, obj):
        return obj.tags.all().values()

    class Meta:
        model = APISettings
        fields = [
            "title",
            "apikey",
            "website",
            "created_at",
            "created_by",
            "lead_assigned_to",
            "tags",
            "org",
        ]


# ------------------ User Admin / Password ------------------
User = get_user_model()

class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "profile_pic", "is_active", "last_login"]


class UserAdminWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "email", "profile_pic", "password", "is_active", "is_staff"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.email = user.email.lower().strip()
        user.set_password(password)
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)


class AdminPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)


# ------------------ Social Login ------------------
class SocialLoginSerializer(serializers.Serializer):
    token = serializers.CharField()


# ------------------ Teams + Profiles Response ------------------
class TeamsAndProfilesResponseSerializer(serializers.Serializer):
    teams = TeamsSerializer(many=True)
    profiles = ProfileSerializer(many=True)
class CreateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "role",
            "phone",
            "alternate_phone",
            "has_sales_access",
            "has_marketing_access",
            "is_organization_admin",
        )
class DocumentCreateSwaggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["title", "document_file", "teams", "shared_to"]

class DocumentEditSwaggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["title", "document_file", "teams", "shared_to", "status"]
class APISettingsSwaggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = APISettings
        fields = [
            "title",
            "website",
            "lead_assigned_to",
            "tags",
        ]
