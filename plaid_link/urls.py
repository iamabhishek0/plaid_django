from django.urls import path
from . import views, views_link

urlpatterns = [
    path('', views.index, name="index"),
    path('home/', views.home, name="home"),
    path('signup/', views.UserCreate.as_view(), name='user-create'),
    path('login/', views.UserLogin.as_view(), name='user-login'),
    path('logout/', views.UserLogout.as_view(), name='user-logout'),
    path('get_access_token/', views_link.get_access_token.as_view(), name='get-access-token'),
    path('get_transactions/', views_link.get_transaction.as_view(), name='get_transaction'),
    path('webhook/', views_link.webhook, name='webhook'),
]
