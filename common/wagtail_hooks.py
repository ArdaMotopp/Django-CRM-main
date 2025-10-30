from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Org, Profile

class OrgWagtailAdmin(ModelAdmin):
    model = Org
    menu_label = "Organizations"
    menu_icon = "group"   # pick any Wagtail icon
    list_display = ("name",)
    search_fields = ("name",)

class ProfileWagtailAdmin(ModelAdmin):
    model = Profile
    menu_label = "Profiles"
    menu_icon = "user"
    list_display = ("user", "org", "is_organization_admin")
    search_fields = ("user__email", "org__name")

modeladmin_register(OrgWagtailAdmin)
modeladmin_register(ProfileWagtailAdmin)
