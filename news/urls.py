from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news, name='news'),
    path('detail/<int:submission_id>/', views.detail, name='detail'),  # Add this line

]