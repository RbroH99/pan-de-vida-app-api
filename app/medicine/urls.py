"""
URL mapping for the medicine API.
"""
from django.urls import path, include
from medicine import views

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('medclass', views.MedClassViewSet)
router.register('medicinepresentation', views.MedicinePresentationViewSet)
router.register('medicine', views.MedicineViewSet)
router.register('disease', views.DiseaseViewSet)
router.register('treatments', views.TreatmentViewSet)


app_name = 'medicine'


urlpatterns = [
    path('', include(router.urls)),
]
