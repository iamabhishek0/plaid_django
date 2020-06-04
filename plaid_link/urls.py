from django.urls import path
from . import views, views_link

urlpatterns = [
    path('signup/', views.UserCreate.as_view(), name='user-create'),
    path('login/', views.UserLogin.as_view(), name='user-login'),
    path('logout/', views.UserLogout.as_view(), name='user-logout'),
    path('get_access_token/', views_link.get_access_token.as_view(), name='get-access-token'),
]
