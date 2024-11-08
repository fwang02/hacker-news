from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news, name='news'),
    path('detail/<int:submission_id>/', views.detail, name='detail'),  # Add this line
    path('hide_submission/<int:submission_id>/', views.hide_submission, name='hide_submission'),
    path('delete/<int:submission_id>/', views.delete_submission, name='delete_submission'),  # Add this line
    path('search/', views.search, name='search'),
]