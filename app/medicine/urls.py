"""
URL mapping for the medicine API.
"""
from django.urls import path, include
from medicine import views

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('medclass', views.MedClassViewSet)


app_name = 'medicine'


urlpatterns = [
    path('', include(router.urls)),
]
