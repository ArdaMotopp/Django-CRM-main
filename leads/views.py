from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account, Tags
from common.models import APISettings, Attachments, Comment, Profile, User
from common.serializer import (
    AttachmentsSerializer,
    CommentSerializer,
    LeadCommentSerializer,
    ProfileSerializer,
)
from contacts.models import Contact
from leads import swagger_params1
from leads.forms import LeadListForm
from leads.models import Company, Lead
from leads.serializer import (
    CompanySerializer,
    CompanySwaggerSerializer,
    LeadSerializer,
    TagsSerializer,
    LeadCreateSerializer,
    LeadCreateSwaggerSerializer,
    LeadDetailEditSwaggerSerializer,
    LeadCommentEditSwaggerSerializer,
    CreateLeadFromSiteSwaggerSerializer,
    LeadUploadSwaggerSerializer,
)
from leads.tasks import (
    create_lead_from_file,
    send_email_to_assigned_user,
    send_lead_assigned_emails,
)
from teams.models import Teams
from teams.serializer import TeamsSerializer
from common.utils import COUNTRIES, INDCHOICES, LEAD_SOURCE, LEAD_STATUS


# -------------------- Lead List + Create --------------------
class LeadListView(APIView, LimitOffsetPagination):
    model = Lead
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = (
            self.model.objects.filter(org=self.request.profile.org)
            .exclude(status="converted")
            .select_related("created_by")
            .prefetch_related("tags", "assigned_to")
            .order_by("-id")
        )
        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            qs = qs.filter(
                Q(assigned_to__in=[self.request.profile]) | Q(created_by=self.request.profile.user)
            )
        return qs

    @extend_schema(tags=["Leads"], parameters=swagger_params1.lead_list_get_params)
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # open leads
        queryset_open = queryset.exclude(status="closed")
        results_open = self.paginate_queryset(queryset_open.distinct(), request, view=self)
        open_leads = LeadSerializer(results_open, many=True).data

        # closed leads
        queryset_close = queryset.filter(status="closed")
        results_close = self.paginate_queryset(queryset_close.distinct(), request, view=self)
        close_leads = LeadSerializer(results_close, many=True).data

        context = {
            "per_page": 10,
            "page_number": (int(self.offset / 10) + 1,),
            "open_leads": {"leads_count": queryset_open.count(), "open_leads": open_leads},
            "close_leads": {"leads_count": queryset_close.count(), "close_leads": close_leads},
            "contacts": Contact.objects.filter(org=request.profile.org).values("id", "first_name"),
            "status": LEAD_STATUS,
            "source": LEAD_SOURCE,
            "companies": CompanySerializer(
                Company.objects.filter(org=request.profile.org), many=True
            ).data,
            "tags": TagsSerializer(Tags.objects.all(), many=True).data,
            "users": Profile.objects.filter(is_active=True, org=request.profile.org).values(
                "id", "user__email"
            ),
            "countries": COUNTRIES,
            "industries": INDCHOICES,
        }
        return Response(context)

    @extend_schema(
        tags=["Leads"],
        description="Create a new Lead",
        parameters=swagger_params1.organization_params,
        request=LeadCreateSwaggerSerializer,
        operation_id="lead_create",
    )
    def post(self, request, *args, **kwargs):
        serializer = LeadCreateSerializer(data=request.data, request_obj=request)
        if serializer.is_valid():
            lead_obj = serializer.save(created_by=request.profile.user, org=request.profile.org)

            # Tags
            for t in request.data.get("tags", []):
                tag, _ = Tags.objects.get_or_create(name=t)
                lead_obj.tags.add(tag)

            # Contacts
            if request.data.get("contacts"):
                obj_contact = Contact.objects.filter(
                    id__in=request.data["contacts"], org=request.profile.org
                )
                lead_obj.contacts.add(*obj_contact)

            # Assigned Users
            if request.data.get("assigned_to"):
                profiles = Profile.objects.filter(
                    id__in=request.data["assigned_to"], org=request.profile.org
                )
                lead_obj.assigned_to.add(*profiles)
                send_email_to_assigned_user.delay(list(profiles.values_list("id", flat=True)), lead_obj.id)

            # Teams
            if request.data.get("teams"):
                teams = Teams.objects.filter(id__in=request.data["teams"], org=request.profile.org)
                lead_obj.teams.add(*teams)

            # Attachment
            if request.FILES.get("lead_attachment"):
                Attachments.objects.create(
                    created_by=request.profile.user,
                    file_name=request.FILES["lead_attachment"].name,
                    lead=lead_obj,
                    attachment=request.FILES["lead_attachment"],
                )

            return Response({"error": False, "message": "Lead Created Successfully"}, status=201)
        return Response({"error": True, "errors": serializer.errors}, status=400)


# -------------------- Lead Detail --------------------
class LeadDetailView(APIView):
    model = Lead
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        return get_object_or_404(Lead, id=pk, org=self.request.profile.org)

    @extend_schema(tags=["Leads"], description="Lead Detail", parameters=swagger_params1.organization_params)
    def get(self, request, pk, **kwargs):
        lead = self.get_object(pk)
        return Response(LeadSerializer(lead).data)


# -------------------- Lead Upload --------------------
class LeadUploadView(APIView):
    model = Lead
    permission_classes = (IsAuthenticated,)

    @extend_schema(tags=["Leads"], parameters=swagger_params1.organization_params, request=LeadUploadSwaggerSerializer)
    def post(self, request, *args, **kwargs):
        lead_form = LeadListForm(request.POST, request.FILES)
        if lead_form.is_valid():
            create_lead_from_file.delay(
                lead_form.validated_rows,
                lead_form.invalid_rows,
                request.profile.id,
                request.get_host(),
                request.profile.org.id,
            )
            return Response({"error": False, "message": "Leads created Successfully"}, status=200)
        return Response({"error": True, "errors": lead_form.errors}, status=400)


# -------------------- Lead Comment --------------------
class LeadCommentView(APIView):
    model = Comment
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        return get_object_or_404(self.model, pk=pk)

    @extend_schema(tags=["Leads"], request=LeadCommentEditSwaggerSerializer)
    def put(self, request, pk, format=None):
        obj = self.get_object(pk)
        if request.profile.role != "ADMIN" and not request.user.is_superuser and request.profile != obj.commented_by:
            return Response({"error": True, "errors": "Permission denied"}, status=403)
        serializer = LeadCommentSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"error": False, "message": "Comment Submitted"}, status=200)
        return Response({"error": True, "errors": serializer.errors}, status=400)

    def delete(self, request, pk, format=None):
        obj = self.get_object(pk)
        if request.profile.role == "ADMIN" or request.user.is_superuser or request.profile == obj.commented_by:
            obj.delete()
            return Response({"error": False, "message": "Comment Deleted"}, status=200)
        return Response({"error": True, "errors": "Permission denied"}, status=403)


# -------------------- Lead Attachments --------------------
class LeadAttachmentView(APIView):
    model = Attachments
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk, format=None):
        obj = get_object_or_404(self.model, pk=pk)
        if request.profile.role == "ADMIN" or request.user.is_superuser or request.profile.user == obj.created_by:
            obj.delete()
            return Response({"error": False, "message": "Attachment Deleted"}, status=200)
        return Response({"error": True, "errors": "Permission denied"}, status=403)


# -------------------- Create Lead from External Site --------------------
class CreateLeadFromSite(APIView):
    @extend_schema(tags=["Leads"], description="Create a Lead via external site API (using API key)", request=CreateLeadFromSiteSwaggerSerializer)
    def post(self, request, *args, **kwargs):
        params = request.data
        api_key = params.get("apikey")
        api_setting = APISettings.objects.filter(apikey=api_key).first()
        if not api_setting:
            return Response({"error": True, "message": "Invalid API key"}, status=403)

        user = api_setting.created_by
        lead = Lead.objects.create(
            title=params.get("title"),
            first_name=params.get("first_name"),
            last_name=params.get("last_name"),
            status="assigned",
            source=api_setting.website,
            description=params.get("description", ""),
            email=params.get("email"),
            phone=params.get("phone"),
            is_active=True,
            created_by=user,
            org=api_setting.org,
        )
        lead.assigned_to.add(user)

        # Optional: create contact
        Contact.objects.create(
            first_name=params.get("first_name"),
            email=params.get("email"),
            phone=params.get("phone"),
            description=params.get("description", ""),
            created_by=user,
            org=api_setting.org,
        )

        return Response({"error": False, "message": "Lead Created successfully."}, status=200)


# -------------------- Companies --------------------
class CompaniesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        companies = Company.objects.filter(org=request.profile.org)
        return Response({"error": False, "data": CompanySerializer(companies, many=True).data}, status=200)

    @extend_schema(tags=["Company"], request=CompanySwaggerSerializer)
    def post(self, request, *args, **kwargs):
        request.data["org"] = request.profile.org.id
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"error": False, "message": "Company created"}, status=200)
        return Response({"error": True, "errors": serializer.errors}, status=400)


class CompanyDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        return get_object_or_404(Company, pk=pk)

    def get(self, request, pk, format=None):
        company = self.get_object(pk)
        return Response({"error": False, "data": CompanySerializer(company).data}, status=200)

    def put(self, request, pk, format=None):
        company = self.get_object(pk)
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"error": False, "message": "Updated Successfully"}, status=200)
        return Response({"error": True, "errors": serializer.errors}, status=400)

    def delete(self, request, pk, format=None):
        company = self.get_object(pk)
        company.delete()
        return Response({"error": False, "message": "Deleted successfully"}, status=200)
