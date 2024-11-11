from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news, name='news'),
    path('detail/<int:submission_id>/', views.detail, name='detail'),  # Add this line
    path('hide_submission/<int:submission_id>/', views.hide_submission, name='hide_submission'),
    path('delete/<int:submission_id>/', views.delete_submission, name='delete_submission'),  # Add this line
    path('search/', views.search, name='search'),
    path('submit/', views.submit, name='submit'),
    path('newest/', views.newest, name='newest'),
    path('<int:submission_id>/', views.submission_details, name='submission_detail'),
    path('confirm-delete/<int:comment_id>/', views.confirm_delete, name='confirm_delete'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('from', views.submissions_by_domain, name='submissions_by_domain'),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
]