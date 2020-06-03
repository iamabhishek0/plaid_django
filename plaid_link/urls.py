from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.UserCreate.as_view(), name = 'user-create'),
]