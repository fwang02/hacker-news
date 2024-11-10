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

]
