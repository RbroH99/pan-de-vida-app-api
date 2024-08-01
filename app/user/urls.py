"""
URLs mapping for the user API.
"""
from django.urls import path, include

from user import views

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('admin', views.AdminUserViewset, basename='admin')

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('', include(router.urls)),
]
