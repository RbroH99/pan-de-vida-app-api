"""
URL mapping for the contact API.
"""
from django.urls import path, include
from contact import views

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('notes', views.NoteViewSet)
router.register('contacts', views.ContactViewSet)
router.register('phone_numbers', views.PhoneNumberViewSet)


app_name = 'contact'


urlpatterns = [
    path('', include(router.urls)),
]
