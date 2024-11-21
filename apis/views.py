from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from news.models import Submission, Comment
from .serializers import SubmissionSerializer, CommentSerializer


# Create your views here.
class Submission_APIView(APIView):
    def get(self, request):
        submissions = Submission.objects.all()
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

class Comment_APIView(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

