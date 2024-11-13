from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.profile, name='profile'),
    path('submissions/', views.submissions, name='submissions'),
    path('hidden/', views.hidden_submissions, name='hidden_submissions'),
    path('unhide/<int:submission_id>/', views.unhide_submission, name='unhide_submission'),
    path('upvote/submission/<int:submission_id>/', views.upvote, name='upvote_submission'),
    path('unvote/submission/<int:submission_id>/', views.unvote, name='unvote_submission'),
    path('upvoted/', views.upvoted_submissions, name='voted_submissions'),
    path('favorites/', views.favorites, name='favorites'),
    path('favorite/submission/<int:submission_id>', views.add_favorite_submission, name='add_favorite_submission'),
    path('favorite/comment/<int:comment_id>', views.add_favorite_comment, name='add_favorite_comment'),
    path('unfavorite/submission/<int:submission_id>', views.remove_favorite_submission, name='remove_favorite_submission'),
    path('unfavorite/comment/<int:comment_id>', views.remove_favorite_comment, name='remove_favorite_comment'),


]
