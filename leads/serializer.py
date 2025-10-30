from rest_framework import serializers
from accounts.models import Account, Tags
from common.serializer import (
    AttachmentsSerializer,
    LeadCommentSerializer,
    OrganizationSerializer,
    ProfileSerializer,
    UserSerializer,
)
from contacts.serializer import ContactSerializer
from leads.models import Company, Lead
from teams.serializer import TeamsSerializer
from common.models import Profile


# -------------------- Lead Detail --------------------
class LeadDetailSerializer(serializers.ModelSerializer):
    """Full detail of a Lead (internal use)."""

    class Meta:
        model = Lead
        fields = "__all__"


# -------------------- Tags --------------------
class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ("id", "name", "slug")


# -------------------- Company --------------------
class CompanySwaggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("name",)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "name", "org")


# -------------------- Lead List / Detail --------------------
class LeadSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)
    assigned_to = ProfileSerializer(read_only=True, many=True)
    created_by = UserSerializer()
    country = serializers.SerializerMethodField()
    tags = TagsSerializer(read_only=True, many=True)
    lead_attachment = AttachmentsSerializer(read_only=True, many=True)
    teams = TeamsSerializer(read_only=True, many=True)
    lead_comments = LeadCommentSerializer(read_only=True, many=True)

    def get_country(self, obj):
        return obj.get_country_display()

    class Meta:
        model = Lead
        fields = (
            "id",
            "title",
            "first_name",
            "last_name",
            "phone",
            "email",
            "status",
            "source",
            "address_line",
            "contacts",
            "street",
            "city",
            "state",
            "postcode",
            "country",
            "website",
            "description",
            "lead_attachment",
            "lead_comments",
            "assigned_to",
            "account_name",
            "opportunity_amount",
            "created_by",
            "created_at",
            "is_active",
            "enquiry_type",
            "tags",
            "created_from_site",
            "teams",
            "skype_ID",
            "industry",
            "company",
            "organization",
            "probability",
            "close_date",
        )


# -------------------- Lead Creation --------------------
class LeadCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new Leads (with org auto-attach)."""

    probability = serializers.IntegerField(max_value=100, required=False)

    def __init__(self, *args, **kwargs):
        request_obj = kwargs.pop("request_obj", None)
        super().__init__(*args, **kwargs)

        self.org = None
        if request_obj and hasattr(request_obj, "profile") and request_obj.profile:
            self.org = request_obj.profile.org

        self.fields["first_name"].required = False
        self.fields["last_name"].required = False
        self.fields["title"].required = True

    def validate_account_name(self, account_name):
        if not account_name:
            return account_name
        if self.org and Account.objects.filter(name__iexact=account_name, org=self.org).exists():
            raise serializers.ValidationError("Account already exists with this name")
        return account_name

    def validate_title(self, title):
        if self.org and Lead.objects.filter(title__iexact=title, org=self.org).exists():
            raise serializers.ValidationError("Lead already exists with this title")
        return title

    def create(self, validated_data):
        if self.org:
            validated_data["org"] = self.org
        return super().create(validated_data)

    class Meta:
        model = Lead
        fields = (
            "title",
            "first_name",
            "last_name",
            "account_name",
            "phone",
            "email",
            "status",
            "source",
            "website",
            "description",
            "address_line",
            "street",
            "city",
            "state",
            "postcode",
            "opportunity_amount",
            "country",
            "skype_ID",
            "industry",
            "company",
            "probability",
            "close_date",
        )


# -------------------- Swagger Serializers --------------------
class LeadCreateSwaggerSerializer(serializers.ModelSerializer):
    """For API docs when creating a Lead."""

    class Meta:
        model = Lead
        fields = (
            "title",
            "first_name",
            "last_name",
            "account_name",
            "phone",
            "email",
            "status",
            "source",
            "website",
            "description",
            "address_line",
            "street",
            "city",
            "state",
            "postcode",
            "opportunity_amount",
            "country",
            "skype_ID",
            "industry",
            "company",
            "probability",
            "close_date",
        )


class CreateLeadFromSiteSwaggerSerializer(serializers.Serializer):
    apikey = serializers.CharField()
    title = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.CharField()
    source = serializers.CharField()
    description = serializers.CharField()


class LeadDetailEditSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()
    lead_attachment = serializers.FileField()


class LeadCommentEditSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()


class LeadUploadSwaggerSerializer(serializers.Serializer):
    leads_file = serializers.FileField()
