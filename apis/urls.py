"""
URL configuration for hacker_news project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from apis.views import *

urlpatterns = [
    path('comments', Comment_APIView.as_view()),
    path('threads', ThreadView.as_view(), name='threads'),
    path('asks', AskView.as_view(), name='asks'),
  
    path('submissions', Submission_APIView.as_view(), name='submit_submission'),
    path('submissions/<int:id>', SubmissionDetailView.as_view(), name='submission_detail'),
    path('submissions/<int:id>', SubmissionDetailView.as_view(), name='delete_submission'),
    path('submissions/<int:id>/vote', Submission_VoteAPIView.as_view(), name='vote_submission'),
    path('submissions/<int:id>/favorite', Submission_FavoriteAPIView.as_view(), name='favorite_submission'),
    path('submissions/<int:id>/hide', Submission_HideAPIView.as_view(), name='hide_submission'),
    path('submissions/<int:id>/comments', Comment_APIView.as_view(), name='add_comment'),
    path('submissions/<int:submission_id>/comments/<int:comment_id>/reply', Comment_ReplyAPIView.as_view(), name='reply_comment'),
    path('submissions/<int:submission_id>/comments/<int:comment_id>', CommentDetailView.as_view(), name='edit_comment'),
    path('submissions/<int:submission_id>/comments/<int:comment_id>', CommentDetailView.as_view(), name='delete_comment'),
    path('submissions/<int:submission_id>/comments/<int:comment_id>', CommentDetailView.as_view(), name='view_comment'),
    path('submissions/<int:submission_id>/comments/<int:comment_id>/vote', Comment_VoteAPIView.as_view(), name='vote_comment'),
    path('submissions/<int:submission_id>/comments/<int:comment_id>/favorite', Comment_FavoriteAPIView.as_view(), name='favorite_comment'),
    path('users/<int:id>/profile', ProfileView.as_view(), name='profile'),
    path('users/<int:user_id>/submissions', UserSubmissions.as_view(), name='user_submissions'),
    path('users/<int:user_id>/comments', UserCommentsAPIView.as_view(), name='user_comments'),
    path('users/<int:user_id>/hidden', UserHiddenSubmissions.as_view(), name='user_hidden_submissions'),
    path('users/<int:user_id>/submissions/favorites', UserFavoriteSubmissions.as_view(), name='user-favorite-submissions'),
    path('users/<int:user_id>/comments/favorites', UserFavoriteComments.as_view(), name='user-favorite-comments'),
    path('users/<int:user_id>/submissions/upvoted', UserUpvotedSubmissions.as_view(), name='user-upvoted-submissions'),
    path('users/<int:user_id>/comments/upvoted', UserUpvotedComments.as_view(), name='user-upvoted-comments'),
]