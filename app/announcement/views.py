from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Announcement
from core.permissions import IsColaboratorMinimun
from core.filters import AnnouncementFilterSet

from .serializers import AnnouncementSerializer

from django.db.models import Q


class AnnouncementViewSet(viewsets.ModelViewSet):
    """Manage announcements in the database."""
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filterset_class = AnnouncementFilterSet
    ordering_fields = ['date', 'initial_date', 'final_date']
    ordering = ['-date']

    def perform_create(self, serializer):
        if not IsColaboratorMinimun.has_permission(self, self.request, self):
            self.permission_denied(
                self.request,
                message="You don't have permission to create an announcement."
            )
        return super().perform_create(serializer)

    def get_queryset(self):
        queryset = Announcement.objects.all()
        user_role = self.request.user.role
        if user_role > 1:
            print(queryset.first().directed_to)
            specific_ids = [announcement.id for announcement in queryset if user_role in (announcement.directed_to if announcement.directed_to else [])] # noqa
            queryset = queryset.filter(
                Q(is_public=True) | Q(id__in=specific_ids)
                )

        # Apply search filter to queryset if needed
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(author__name__icontains=search)
            )

        # Order queryset
        queryset = queryset.order_by('-date')

        return queryset
