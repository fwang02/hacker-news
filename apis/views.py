from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from news.models import Submission, Comment
from news.utils import calculate_score
from .serializers import SubmissionSerializer, CommentSerializer, SubmissionCreateSerializer, SubmissionUpdateSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

class Submission_APIView(APIView):

    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Get all submissions",
        responses={200: SubmissionSerializer(many=True),
                   400: "Invalid sort parameter"},
        manual_parameters=[openapi.Parameter('sort', openapi.IN_QUERY, description="Sort submissions by point or newest", type=openapi.TYPE_STRING)]
    )
    def get(self, request):
        sort = request.query_params.get('sort', 'point')
        submissions = Submission.objects.all()

        if sort == 'point':
            submissions = sorted(submissions, key=lambda x: calculate_score(x), reverse=True)
        elif sort == 'newest':
            submissions = submissions.order_by('-created')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid sort parameter'})

        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        self.check_permissions(request)
        serializer = SubmissionCreateSerializer(data=request.data)
        if serializer.is_valid():
            #serializer.save(author=request.user)
            #return Response(serializer.data, status=status.HTTP_201_CREATED)
            submission = serializer.save(author=request.user)
            response_serializer = SubmissionSerializer(submission)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        self.check_permissions(request)

        submission = get_object_or_404(Submission, id=id)
        # Check if the request user is the author of the submission
        if submission.author != request.user:
            return Response({'error': 'You do not have permission to edit this submission.'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = SubmissionUpdateSerializer(submission, data=request.data, partial=True)
        if serializer.is_valid():
            #serializer.save()
            #return Response(serializer.data)
            submission = serializer.save()
            response_serializer = SubmissionSerializer(submission)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)

class Comment_APIView(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)

class SubmissionDetailView(APIView):
    def get(self, request, id):
        submission = get_object_or_404(Submission, id=id)
        serializer = SubmissionSerializer(submission)
        return Response(serializer.data)

    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)

