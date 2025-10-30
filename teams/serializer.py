from rest_framework import serializers
from teams.models import Teams


class TeamsSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Teams
        fields = (
            "id",
            "name",
            "description",
            "users",
            "created_at",
            "created_by",
            "created_on_arrow",
        )

    def get_users(self, obj):
        # Lazy import avoids circular import
        from common.serializer import ProfileSerializer
        return ProfileSerializer(obj.users.all(), many=True).data

    def get_created_by(self, obj):
        # Lazy import avoids circular import
        from common.serializer import UserSerializer
        return UserSerializer(obj.created_by).data if obj.created_by else None


class TeamCreateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        request_obj = kwargs.pop("request_obj", None)
        super().__init__(*args, **kwargs)
        self.org = getattr(request_obj, "profile", None).org if request_obj else None

        self.fields["name"].required = True
        self.fields["description"].required = False

    def validate_name(self, name):
        qs = Teams.objects.filter(name__iexact=name, org=self.org)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Team already exists with this name")
        return name

    class Meta:
        model = Teams
        fields = (
            "name",
            "description",
            "created_at",
            "created_by",
            "created_on_arrow",
            "org",
        )


class TeamswaggerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teams
        fields = ("name", "description", "users")
