from django.urls import path
from . import views

urlpatterns = [
    path('', views.news, name='news'),
    path('submit/', views.submit, name='submit'),
    path('newest/', views.newest, name='newest'),
    path('login/', views.login, name='login'),
    path('create_account/', views.create_account, name='create_account'),
    path('logout/', views.logout, name='logout'),

]
