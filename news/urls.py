from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.news, name='news'),
    path('submit/', views.submit, name='submit'),
    path('newest/', views.newest, name='newest'),
    path('login/', views.login_view, name='login'),
    path('create_account/', views.create_account, name='create_account'),
    path('logout/', views.logout, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

]
