from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("users", views.UserViewSet)
urlpatterns = [
    path('', include('djoser.urls.jwt')),  # jwt/
]
urlpatterns += router.urls
