from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allows access only if user is admin."""

    def has_permission(self, request, view):
        user_role = getattr(request.user, 'role', None)

        return user_role == 1


class IsNotDonor(BasePermission):
    """Allows access only if user is not Donor."""

    def has_permission(self, request, view):
        if hasattr(request.user, 'role'):
            if request.user.role == 5:
                return False
        return True
