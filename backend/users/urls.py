from django.urls import path
from rest_framework.authtoken import views as drf_views

urlpatterns = [
    path('auth/token/login/', drf_views.obtain_auth_token),
]
