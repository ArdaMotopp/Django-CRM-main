from django.urls import path
from .views import (
    LeadListView,
    LeadDetailView,
    LeadUploadView,
    LeadCommentView,
    LeadAttachmentView,
    CreateLeadFromSite,
    CompaniesView,
    CompanyDetail,
)

app_name = "api_leads"

urlpatterns = [
    # Leads
    path("", LeadListView.as_view(), name="lead-list"),                      # GET list, POST create
    path("<uuid:pk>/", LeadDetailView.as_view(), name="lead-detail"),        # GET, PUT, DELETE
    path("upload/", LeadUploadView.as_view(), name="lead-upload"),

    # Comments & Attachments
    path("comments/<int:pk>/", LeadCommentView.as_view(), name="lead-comment"),
    path("attachments/<int:pk>/", LeadAttachmentView.as_view(), name="lead-attachment"),

    # External site lead creation
    path("create-from-site/", CreateLeadFromSite.as_view(), name="create-lead-from-site"),

    # Companies
    path("companies/", CompaniesView.as_view(), name="company-list"),
    path("companies/<int:pk>/", CompanyDetail.as_view(), name="company-detail"),
]
