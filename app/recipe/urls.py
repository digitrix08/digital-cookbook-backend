from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagViewSet

app_name = 'recipe'

router = DefaultRouter()
router.register('tag', TagViewSet)

urlpatterns = [
    path('', include(router.urls))
]
