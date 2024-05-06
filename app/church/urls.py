"""
URL mapping for the church API.
"""
from django.urls import path, include
from church import views

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('municipalitys', views.MunicipalityViewSet)
router.register('denominations', views.DenominationViewSet)
router.register('churchs', views.ChurchViewSet)


app_name = 'church'


urlpatterns = [
    path('', include(router.urls)),
]
