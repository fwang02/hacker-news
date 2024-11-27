from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from news.models import Submission, Comment
from news.utils import calculate_score
from .serializers import SubmissionSerializer, CommentSerializer, SubmissionCreateSerializer
from rest_framework.permissions import IsAuthenticated
from .utils import get_user_from_api_key

class Submission_APIView(APIView):

    def get(self, request):
        sort = request.query_params.get('sort', 'score')
        submissions = Submission.objects.all()

        if sort == 'score':
            submissions = sorted(submissions, key=lambda x: calculate_score(x), reverse=True)
        elif sort == 'newest':
            submissions = submissions.order_by('-created')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid sort parameter'})

        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        serializer = SubmissionCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)

class Comment_APIView(APIView):
    def get(self, request):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)

class SubmissionDetailView(APIView):
    def get(self, request, id):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        submission = get_object_or_404(Submission, id=id)
        serializer = SubmissionSerializer(submission)
        return Response(serializer.data)

    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)

