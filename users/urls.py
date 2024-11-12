from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.profile, name='profile'),
    path('submissions/', views.submissions, name='submissions'),
    path('hidden/', views.hidden_submissions, name='hidden_submissions'),
    path('unhide/<int:submission_id>/', views.unhide_submission, name='unhide_submission'),
    path('upvote/<int:submission_id>/', views.upvote, name='upvote'),
    path('unvote/<int:submission_id>/', views.unvote, name='unvote'),
    path('upvoted/', views.upvoted_submissions, name='voted_submissions'),
    path('favorites/', views.favorites, name='favorites'),
    path('favorite/<int:submission_id>', views.add_favorite_submission, name='add_favorite_submission'),
    path('favorite/<int:comment_id>', views.add_favorite_comment, name='add_favorite_comment'),
    path('unfavorite/<int:submission_id>', views.remove_favorite_submission, name='remove_favorite_submission'),
    path('unfavorite/<int:comment_id>', views.remove_favorite_comment, name='remove_favorite_comment'),


]
