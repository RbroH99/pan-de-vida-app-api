from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RoleIncludedTokenObtainSerializer(TokenObtainPairSerializer):
    """Custon token obtain view to include role in the response."""
    def validate(self, attrs):
        data = super().validate(attrs)

        data['role'] = self.user.role

        return data
