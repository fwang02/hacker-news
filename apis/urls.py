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
from apis import views
from apis.views import *
from news.models import Comment

urlpatterns = [
    path('comments', Comment_APIView.as_view()),
    path('submissions/<int:id>', SubmissionDetailView.as_view(), name='submission_detail'),
    path('submissions', Submission_APIView.as_view(), name='submit_submission'),
    path('submissions/<int:id>/update', Submission_APIView.as_view(), name='update_submission_title'),
    path('submissions/<int:id>/delete', Submission_APIView.as_view(), name='delete_submission'),
    path('submissions/<int:id>/vote', Submission_VoteAPIView.as_view(), name='vote_submission'),
    path('submissions/<int:id>/unvote', Submission_VoteAPIView.as_view(), name='unvote_submission'),
]