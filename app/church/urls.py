"""
URL mapping for the church API.
"""
from django.urls import path, include
from church import views

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('municipalities', views.MunicipalityViewSet)
router.register('denominations', views.DenominationViewSet)
router.register('churches', views.ChurchViewSet)


app_name = 'church'


urlpatterns = [
    path('', include(router.urls)),
    path('provinces/', views.ProvincesOptionsView.as_view(), name='provinces'),
]
