"""
URL mapping for the dispatch API.
"""
from django.urls import path, include
from dispatch import views

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('dispatches', views.DispatchViewSet)
router.register('dispatch-item', views.DispatchItemViewSet)
router.register('item', views.ItemViewSet)


app_name = 'dispatch'


urlpatterns = [
    path('', include(router.urls)),
]
