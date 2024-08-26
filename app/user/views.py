"""
Views for the userAPI.
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
"""
import jwt.utils
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework import generics, permissions, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.conf import settings

from user.serializers import UserSerializer

from core.permissions import IsAdminRole

import jwt

from datetime import datetime, timedelta


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class AdminUserViewset(viewsets.ModelViewSet):
    """Viewset for the admin users to manage users in the system."""
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role']
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'email']

    actions = {
        'list': ['get'],
        'create': ['post'],
        'retrieve': ['get'],
        'update': ['put', 'patch'],
        'partial_update': ['patch'],
        'destroy': ['delete']
    }

    def get_queryset(self):
        try:
            users = get_user_model().objects.exclude(id=self.request.user.id)
            return users
        except AttributeError:
            raise Http404("No se encontró el usuario.")


UserModel = get_user_model()


class PasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            user = UserModel.objects.get(email=email)

            token = self.generate_password_reset_token(user)
            reset_url = \
                f"{request.build_absolute_uri('reset-password/')}?token={token}"

            html_message = render_to_string(
                'password_reset_email.html',
                {'user': user, 'reset_url': reset_url}
            )

            send_mail(
                subject="Restablecer contraseña",
                message=html_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False
            )

            return JsonResponse(
                {"message": "Email enviado con instrucciones de recuperación"}
                )
        except UserModel.DoesNotExist:
            return JsonResponse(
                {"error": f"Usuario {email} no encontrado"},
                status=404
                )

    def generate_password_reset_token(self, user):
        expires_in = timedelta(hours=1)
        payload = {
            'user_id': user.id,
            'exp': (datetime.now() + expires_in).timestamp()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


class ResetPasswordView(APIView):
    def get(self, request, token):
        try:
            decoded_token = jwt.decode(
                force_str(token),
                settings.SECRET_KEY, algorithms=['HS256']
            )
            user = UserModel.objects.get(id=decoded_token['user_id'])

            try:
                new_password = request.data.get('password')
                user.set_password(new_password)
                user.save()
                return Response(
                    {"success": True,
                     "message": "Contraseña restablecida con éxito"
                     }
                    )
            except ValidationError as e:
                return Response({"error": str(e)})
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "El token ha expirado"}, status=400)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Token inválido"}, status=400)
        except UserModel.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=404)
