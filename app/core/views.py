from rest_framework_simplejwt.views import TokenObtainPairView
from core.serializers import RoleIncludedTokenObtainSerializer


class RoleIncludedTokenObtainView(TokenObtainPairView):
    """Custom obtain pair view to include user role."""
    serializer_class = RoleIncludedTokenObtainSerializer
