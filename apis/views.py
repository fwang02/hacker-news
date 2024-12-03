import re

from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from news.models import *
from news.utils import calculate_score
from users.models import *
from .serializers import *


class Submission_APIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # get all submissions in page hackernews
    @swagger_auto_schema(
        tags=['Submission'],
        security=[],
        operation_description="Get all submissions",
        responses={200: SubmissionSerializer(many=True),
                   400: "Invalid sort parameter"},
        manual_parameters=[openapi.Parameter('sort', openapi.IN_QUERY, description="Sort submissions by point or newest", type=openapi.TYPE_STRING)]
    )
    def get(self, request):
        sort = request.query_params.get('sort', 'point')
        from_domain = request.query_params.get('from', None)
        submissions = Submission.objects.all()

        if from_domain:
            domain_regex = re.compile(
                r'^(?:[a-zA-Z0-9]'  # First character of the domain
                r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'  # Sub domain + hostname
                r'+[a-zA-Z]{2,6}\.?$'  # First level TLD
            )
            if not domain_regex.match(from_domain):
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid domain parameter'})
            submissions = submissions.filter(domain=from_domain)

        if sort == 'point':
            submissions = sorted(submissions, key=lambda x: calculate_score(x), reverse=True)
        elif sort == 'newest':
            submissions = submissions.order_by('-created')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid sort parameter'})

        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    #create a new submission
    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Create a submission",
        #request_body=SubmissionCreateSerializer,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the submission'),
                'url': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the submission'),
                'text': openapi.Schema(type=openapi.TYPE_STRING, description='Text of the submission')
            },
            example={
                "title": "titulo ejemplo",
                "url": "https://www.youtube.com/",
                "text": "texto ejemplo"
            }
        ),
        responses={
            201: SubmissionSerializer,
            400: openapi.Response(
                description="Validation errors",
                examples={
                    "application/json": {
                        "non_field_errors": ["Either 'url' or 'text' must be provided."],
                        "title": ["A submission with this title already exists."]
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"message": "Invalid token."},
                        {"message": "Invalid token header. No credentials provided."}
                    ]
                }
            )
        }
    )
    def post(self, request):
        self.authentication_classes = [TokenAuthentication]
        serializer = SubmissionCreateSerializer(data=request.data)
        if serializer.is_valid():
            #serializer.save(author=request.user)
            #return Response(serializer.data, status=status.HTTP_201_CREATED)
            submission = serializer.save(author=request.user)
            response_serializer = SubmissionSerializer(submission)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)

class Comment_APIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # Get all comments
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    # Agregar un comentario
    @swagger_auto_schema(
        tags=['Comment'],
        operation_description="Add a comment",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, description="Text of the comment"),
            },
            required=['text'],
            example={
                'text': "Este es un comentario de prueba."
            }
        ),
        responses={
            201: openapi.Response(description="Comment created successfully", schema=CommentSerializer),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Unauthorized"),
        }
    )
    def post(self, request, id):
        self.authentication_classes = [TokenAuthentication]
        
        # Obtener la Submission correspondiente al ID proporcionado en la URL
        try:
            submission = Submission.objects.get(id=id)
        except Submission.DoesNotExist:
            return Response({"detail": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)

        # Crear el comentario usando el serializer, pasando la submission al contexto
        serializer = CommentCreateSerializer(data=request.data, context={'submission': submission})

        if serializer.is_valid():
            comment = serializer.save(author=request.user)
            response_serializer = CommentSerializer(comment)  # Serializar para la respuesta
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)

class Comment_ReplyAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    #Reply comment
    @swagger_auto_schema(
        tags=['Comment'],
        operation_description="Reply to a comment",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, description="Text of the comment"),
            },
            required=['text'],
            example={
                'text': "This is a reply to the comment."
            }
        ),
        responses={
            201: openapi.Response(description="Reply created successfully", schema=CommentSerializer),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Unauthorized"),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "message": "Submission not found or Parent comment not found."
                    }
                }
            ),
        }
    )
    def post(self, request, submission_id, comment_id):
        try:
            submission = Submission.objects.get(id=submission_id)
            parent_comment = Comment.objects.get(id=comment_id, submission=submission)
        except Submission.DoesNotExist:
            return Response({"message": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"message": "No comment with such an ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentCreateSerializer(
            data=request.data,
            context={'submission': submission}
        )
        if serializer.is_valid():
            comment = serializer.save(author=request.user, parent=parent_comment)
            response_serializer = CommentSerializer(comment)  # Serializar la respuesta
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)

class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # Edit a comment
    @swagger_auto_schema(
        tags=['Comment'],
        operation_description="Edit a comment",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, description="Text of the comment"),
            },
            required=['text'],
            example={
                'text': "Comentario editado."
            }
        ),
        responses={
            200: CommentSerializer,
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden: You don't have permission to edit this comment."),
            404: openapi.Response(description="Not Found")
        }
    )
    def put(self, request, submission_id, comment_id):
        self.check_permissions(request)
        try:
            submission = Submission.objects.get(id=submission_id)
            comment = Comment.objects.get(id=comment_id, submission=submission)
        except Submission.DoesNotExist:
            return Response({"message": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"message": "No comment with such an ID."}, status=status.HTTP_404_NOT_FOUND)

        if comment.author != request.user:
            return Response({"message": "You do not have permission to edit this comment."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = CommentUpdateSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            updated_comment = serializer.save()
            response_serializer = CommentSerializer(updated_comment)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete a comment
    @swagger_auto_schema(
        tags=['Comment'],
        operation_description="Delete a comment",
        responses={
            200: openapi.Response(
                description="Comment deleted successfully",
                examples={
                    "application/json": {
                        "message": "Comment deleted successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "Invalid request."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"detail": "Invalid token."},
                        {"detail": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
            403: openapi.Response(
                description="Forbidden",
                examples={
                    "application/json": {
                        "message": "You do not have permission to delete this comment."
                    }
                }
            ),
             404: openapi.Response(
                description="Not Found (Submission)",
                examples={
                    "application/json": {
                        "message": "Submission not found"
                    }
                }
            ),
            404: openapi.Response(
                description="Not Found (Comment)",
                examples={
                    "application/json": {
                        "message": "No comment with such an ID."
                    }
                }
            )
        }
    )
    def delete(self, request, submission_id, comment_id):
        self.check_permissions(request)
        try:
            submission = Submission.objects.get(id=submission_id)
            comment = Comment.objects.get(id=comment_id, submission=submission)
        except Submission.DoesNotExist:
            return Response({"message": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"message": "No comment with such an ID."}, status=status.HTTP_404_NOT_FOUND)
        
        if comment.author != request.user:
            return Response({"message": "You do not have permission to delete this comment."},
                            status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({'message': 'Comment deleted successfully.'}, status=status.HTTP_200_OK)
    
    # Obtener un comentario y sus replies
    @swagger_auto_schema(
        tags=['Comment'],
        operation_description="Get a comment with all its replies",
        responses={
            200: CommentSerializer,
            404: openapi.Response(description="Not Found")
        }
    )

    def get(self, request, submission_id, comment_id):
        # Buscar la Submission y el Comment por sus ID
        try:
            submission = Submission.objects.get(id=submission_id)
            comment = Comment.objects.get(id=comment_id, submission=submission)
        except Submission.DoesNotExist:
            return Response({"message": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"message": "No comment with such an ID."}, status=status.HTTP_404_NOT_FOUND)

        replies = comment.replies.all()  

        comment_data = CommentSerializer(comment).data
        replies_data = CommentSerializer(replies, many=True).data

        comment_data['replies'] = replies_data

        return Response(comment_data, status=status.HTTP_200_OK)

    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)


class SubmissionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    #get submission with the given id
    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Get a submission",
        responses={
            200: SubmissionSerializer,
            404: "No submission with such an ID."
        }
    )
    def get(self, request, id):
        try:
            submission = get_object_or_404(Submission, id=id)
        except Http404:
            return Response({'message': 'No submission with such an ID.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubmissionSerializer(submission)
        return Response(serializer.data)

    #update a submission
    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Update a submission",
        #request_body=SubmissionUpdateSerializer,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the submission')
            },
            example={
                "title": "Title Updated"
            }
        ),
        responses={
            200: SubmissionSerializer,
            400: openapi.Response(
                description="Validation errors",
                examples={
                    "application/json": {
                        "title": ["A submission with this title already exists."]
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"detail": "Invalid token."},
                        {"detail": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "message": "No submission with such an ID."
                    }
                }
            )
        }
    )
    def put(self, request, id):
        self.check_permissions(request)
        try:
            submission = get_object_or_404(Submission, id=id)
        except Http404:
            return Response({'message': 'No submission with such an ID.'}, status=status.HTTP_404_NOT_FOUND)
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

    #delete a submission
    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Delete a submission",
        responses={
            200: openapi.Response(
                description="Submission deleted successfully",
                examples={
                    "application/json": {
                        "message": "Submission deleted successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": "Invalid request."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"detail": "Invalid token."},
                        {"detail": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "message": "No submission with such an ID."
                    }
                }
            )
        }
    )
    def delete(self, request, id):
        self.check_permissions(request)
        try:
            submission = get_object_or_404(Submission, id=id)
        except Http404:
            return Response({'message': 'No submission with such an ID.'}, status=status.HTTP_404_NOT_FOUND)
        # Check if the request user is the author of the submission
        if submission.author != request.user:
            return Response({'message': 'You do not have permission to delete this submission.'},
                            status=status.HTTP_403_FORBIDDEN)
        submission.delete()
        return Response({'message': 'Submission deleted successfully.'}, status=status.HTTP_200_OK)

    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)

class ThreadView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get(self, request):
        comments = Comment.objects.filter(author=request.user,parent__isnull=True).order_by('-created_at')
        serializer = ThreadSerializer(comments, many=True)
        return Response(serializer.data)

class AskView(APIView):
    def get(self, request):
        asks = Submission_ASK.objects.all()
        serializer = SubmissionSerializer(asks, many=True)
        return Response(serializer.data)

class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        tags=['User'],
        operation_description="Get user profile",
        responses={
            200: openapi.Response(
                description="Profile retrieved successfully",
                schema=ProfileSerializer
            ),
            404: openapi.Response(
                description="Profile not found",
                examples={
                    "application/json": { "detail": "No Profile matches the given query."}
                }
            ),
            500: openapi.Response(description="Internal Server Error")
        }
    )
    def get(self, request,id):
        profile = get_object_or_404(Profile, user_id=id)
        serializer = ProfileSerializer(profile)
        response_data = serializer.data
        if request.user.id == id:
            token = Token.objects.filter(user_id=id).values_list('key', flat=True).first()
            response_data = { **serializer.data, 'token': token }
        return Response(response_data)

    @swagger_auto_schema(
        tags=['User'],
        operation_description="Update user profile",
        request_body=ProfileUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                schema=ProfileUpdateSerializer
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"detail": "Invalid token."},
                        {"detail": "Authentication credentials were not provided."}
                    ]
                }
            ),
            403: openapi.Response(
                description="Forbidden",
                examples={
                    "application/json": {"message": "You do not have permission to edit this profile."}
                }
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": { "message": "No profile with such ID." }
                }
            )
        }
    )
    def put(self, request, id):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        try:
            profile = get_object_or_404(Profile, user_id=id)
        except Http404:
            return Response({'message': 'No profile with such ID.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.id != id:
            return Response({'message': 'You do not have permission to edit this profile.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSubmissions(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        submissions = Submission.objects.filter(author=user)
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

class UserCommentsAPIView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        comments = Comment.objects.filter(author_id=user_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

class UserHiddenSubmissions(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get(self, request, user_id):
        if request.user.id != user_id:
            return Response(
                {"error": "You do not have permission to view other users' hidden submissions."}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        hidden_submissions_ids = HiddenSubmission.objects.filter(user=request.user).values_list('submission', flat=True)
        submissions = Submission.objects.filter(id__in=hidden_submissions_ids).order_by('-created')
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

class UserFavoriteSubmissions(APIView):
    @swagger_auto_schema(
        tags=['User'],
        operation_description="Get user's favorite submissions",
        responses={
            200: SubmissionSerializer(many=True),
            404: "User not found"
        }
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        favorite_submissions_ids = Favorite_submission.objects.filter(user=user).values_list('submission', flat=True)
        submissions = Submission.objects.filter(id__in=favorite_submissions_ids).order_by('-created')
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

class UserFavoriteComments(APIView):
    @swagger_auto_schema(
        tags=['User'],
        operation_description="Get user's favorite comments",
        responses={
            200: CommentSerializer(many=True),
            404: "User not found"
        }
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        favorite_comments_ids = Favorite_comment.objects.filter(user=user).values_list('comment', flat=True)
        comments = Comment.objects.filter(id__in=favorite_comments_ids).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

class UserUpvotedSubmissions(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    @swagger_auto_schema(
        tags=['User'],
        operation_description="Get user's upvoted submissions",
        responses={
            200: SubmissionSerializer(many=True),
            403: "You can only view your own upvoted submissions",
            404: "User not found"
        }
    )
    def get(self, request, user_id):
        if request.user.id != user_id:
            return Response(
                {"error": "You can only view your own upvoted submissions"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        upvoted_submissions_ids = UpvotedSubmission.objects.filter(user=request.user).values_list('submission', flat=True)
        submissions = Submission.objects.filter(id__in=upvoted_submissions_ids).order_by('-created')
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

class UserUpvotedComments(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    @swagger_auto_schema(
        tags=['User'],
        operation_description="Get user's upvoted comments",
        responses={
            200: CommentSerializer(many=True),
            403: "Forbidden - Can only view your own upvoted comments",
            404: "User not found"
        }
    )
    def get(self, request, user_id):
        if request.user.id != user_id:
            return Response(
                {"error": "You can only view your own upvoted comments"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        upvoted_comments_ids = UpvotedComment.objects.filter(user=request.user).values_list('comment', flat=True)
        comments = Comment.objects.filter(id__in=upvoted_comments_ids).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)         

class Comment_VoteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # Vote a comment
    @swagger_auto_schema(
        tags=['Comment'],
        operation_description="Vote a comment",
        responses={
            200: openapi.Response(
                description="Comment voted successfully",
                examples={
                    "application/json": {
                        "message": "Comment voted successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "message": "You have already voted for this comment."
                    }
                }
            ),
            403: openapi.Response(
                description="Forbidden",
                examples={
                    "application/json": {
                        "message": "You cannot vote for your own comment."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"message": "Invalid token."},
                        {"message": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
             404: openapi.Response(
                description="Not Found (Submission)",
                examples={
                    "application/json": {
                        "message": "Submission not found"
                    }
                }
            ),
            404: openapi.Response(
                description="Not Found (Comment)",
                examples={
                    "application/json": {
                        "message": "No comment with such an ID."
                    }
                }
            )
        }
    )
    def post(self, request, submission_id, comment_id):
        self.check_permissions(request)

        try:
            submission = Submission.objects.get(id=submission_id)
            comment = Comment.objects.get(id=comment_id, submission=submission)
        except Submission.DoesNotExist:
            return Response({"message": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"message": "No comment with such an ID."}, status=status.HTTP_404_NOT_FOUND)

        if UpvotedComment.objects.filter(user=request.user, comment=comment).exists():
            return Response({'message': 'You have already voted for this comment.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if comment.author == request.user:
            return Response({'message': 'You cannot vote for your own comment.'}, status=status.HTTP_403_FORBIDDEN)

        UpvotedComment.objects.create(user=request.user, comment=comment)
        comment.add_point(1) 

        return Response({'message': 'Comment voted successfully.'}, status=status.HTTP_200_OK)
    
    # Unvote a comment
    @swagger_auto_schema(
        tags=['Comment'],
        operation_description="Delete a vote from a comment",
        responses={
            200: openapi.Response(
                description="Vote removed successfully",
                examples={
                    "application/json": {
                        "message": "Comment unvoted successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "message": "You have not voted for this comment yet."
                    }
                }
            ),
            403: openapi.Response(
                description="Forbidden",
                examples={
                    "application/json": {
                        "message": "You cannot unvote your own comment."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"message": "Invalid token."},
                        {"message": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
             404: openapi.Response(
                description="Not Found (Submission)",
                examples={
                    "application/json": {
                        "message": "Submission not found"
                    }
                }
            ),
            404: openapi.Response(
                description="Not Found (Comment)",
                examples={
                    "application/json": {
                        "message": "No comment with such an ID."
                    }
                }
            )
        }
    )
    
    def delete(self, request, submission_id, comment_id):
        self.check_permissions(request)

        try:
            submission = Submission.objects.get(id=submission_id)
            comment = Comment.objects.get(id=comment_id, submission=submission)
        except Submission.DoesNotExist:
            return Response({"message": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"message": "No comment with such an ID."}, status=status.HTTP_404_NOT_FOUND)

        upvoted_comment = UpvotedComment.objects.filter(user=request.user, comment=comment).first()
        if not upvoted_comment:
            return Response({'message': 'You have not voted for this comment yet.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if comment.author == request.user:
            return Response({'message': 'You cannot unvote your own comment.'}, status=status.HTTP_403_FORBIDDEN)

        upvoted_comment.delete()
        comment.subtract_point(1)  

        return Response({'message': 'Comment unvoted successfully.'}, status=status.HTTP_200_OK)
    
    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)

class Submission_VoteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    #Vote a submission
    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Vote a submission",
        responses={
            200: openapi.Response(
                description="Submission voted successfully",
                examples={
                    "application/json": {
                        "message": "Submission voted successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "message": "You have already voted for this submission."
                    }
                }
            ),
            403: openapi.Response(
                description="Forbidden",
                examples={
                    "application/json": {
                        "message": "You cannot vote for your own submission."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"message": "Invalid token."},
                        {"message": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "message": "No submission with such an ID."
                    }
                }
            )
        }
    )
    def post(self, request, id):
        self.check_permissions(request)
        try:
            submission = get_object_or_404(Submission, id=id)
        except Http404:
            return Response({'message': 'No submission with such an ID.'}, status=status.HTTP_404_NOT_FOUND)
        if UpvotedSubmission.objects.filter(user=request.user, submission=submission).exists():
            return Response({'message': 'You have already voted for this submission.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if submission.author == request.user:
            return Response({'message': 'You cannot vote for your own submission.'}, status=status.HTTP_403_FORBIDDEN)
        UpvotedSubmission.objects.create(user=request.user, submission=submission)
        submission.add_point()
        return Response({'message': 'Submission voted successfully.'}, status=status.HTTP_200_OK)

    # Unvote a submission
    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Delete a vote from a submission",
        responses={
            200: openapi.Response(
                description="Vote removed successfully",
                examples={
                    "application/json": {
                        "message": "Submission unvoted successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "message": "You have not voted for this submission yet."
                    }
                }
            ),
            403: openapi.Response(
                description="Forbidden",
                examples={
                    "application/json": {
                        "message": "You cannot unvote your own submission."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"message": "Invalid token."},
                        {"message": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "message": "No submission with such an ID."
                    }
                }
            )
        }
    )
    def delete(self, request, id):
        self.check_permissions(request)
        try:
            submission = get_object_or_404(Submission, id=id)
        except Http404:
            return Response({'message': 'No submission with such an ID.'}, status=status.HTTP_404_NOT_FOUND)
        upvoted_submission = UpvotedSubmission.objects.filter(user=request.user, submission=submission).first()
        if not upvoted_submission:
            return Response({'message': 'You have not voted for this submission yet.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if submission.author == request.user:
            return Response({'message': 'You cannot unvote your own submission.'}, status=status.HTTP_403_FORBIDDEN)
        upvoted_submission = get_object_or_404(UpvotedSubmission, user=request.user, submission=submission)
        upvoted_submission.delete()
        submission.subtract_point()
        return Response({'message': 'Submission unvoted successfully.'}, status=status.HTTP_200_OK)

    def check_permissions(self, request):
        if request.method in ['POST', 'PUT', 'DELETE']:
            super().check_permissions(request)


class Submission_FavoriteAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Favorite a submission
    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Favorite a submission",
        responses={
            200: openapi.Response(
                description="Submission favorited successfully",
                examples={
                    "application/json": {
                        "message": "Submission favorited successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "message": "You have already favorited this submission."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"message": "Invalid token."},
                        {"message": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "message": "No submission with such an ID."
                    }
                }
            )
        }
    )
    def post(self, request, id):
        self.check_permissions(request)
        try:
            submission = get_object_or_404(Submission, id=id)
        except Http404:
            return Response({'message': 'No submission with such an ID.'}, status=status.HTTP_404_NOT_FOUND)
        if Favorite_submission.objects.filter(user=request.user, submission=submission).exists():
            return Response({'message': 'You have already favorited this submission.'},
                            status=status.HTTP_400_BAD_REQUEST)
        Favorite_submission.objects.create(user=request.user, submission=submission)
        return Response({'message': 'Submission favorited successfully.'}, status=status.HTTP_200_OK)

    # Unfavorite a submission
    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Unfavorite a submission",
        responses={
            200: openapi.Response(
                description="Submission unfavorited successfully",
                examples={
                    "application/json": {
                        "message": "Submission unfavorited successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "message": "You have not favorited this submission yet."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"message": "Invalid token."},
                        {"message": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "message": "No submission with such an ID."
                    }
                }
            )
        }
    )
    def delete(self, request, id):
        self.check_permissions(request)
        try:
            submission = get_object_or_404(Submission, id=id)
        except Http404:
            return Response({'message': 'No submission with such an ID.'}, status=status.HTTP_404_NOT_FOUND)
        favorite_submission = Favorite_submission.objects.filter(user=request.user, submission=submission).first()
        if not favorite_submission:
            return Response({'message': 'You have not favorited this submission yet.'},
                            status=status.HTTP_400_BAD_REQUEST)
        # Remove the submission from the user's favorites
        favorite_submission.delete()
        return Response({'message': 'Submission unfavorited successfully.'}, status=status.HTTP_200_OK)

    def check_permissions(self, request):
        if request.method in ['POST', 'DELETE']:
            super().check_permissions(request)

class Comment_FavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # Favorite a comment
    @swagger_auto_schema(
        tags=['Comment'],
        operation_description="Favorite a comment",
        responses={
            200: openapi.Response(
                description="Comment favorited successfully",
                examples={
                    "application/json": {
                        "message": "Comment favorited successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "message": "You have already favorited this comment."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"message": "Invalid token."},
                        {"message": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
             404: openapi.Response(
                description="Not Found (Submission)",
                examples={
                    "application/json": {
                        "message": "Submission not found"
                    }
                }
            ),
            404: openapi.Response(
                description="Not Found (Comment)",
                examples={
                    "application/json": {
                        "message": "No comment with such an ID."
                    }
                }
            )
        }
    )
    def post(self, request, submission_id, comment_id):
        self.check_permissions(request)
        
        try:
            submission = Submission.objects.get(id=submission_id)
            comment = Comment.objects.get(id=comment_id, submission=submission)
        except Submission.DoesNotExist:
            return Response({"message": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"message": "No comment with such an ID."}, status=status.HTTP_404_NOT_FOUND)

        if Favorite_comment.objects.filter(user=request.user, comment=comment).exists():
            return Response({'message': 'You have already favorited this comment.'},
                            status=status.HTTP_400_BAD_REQUEST)

        Favorite_comment.objects.create(user=request.user, comment=comment)
        return Response({'message': 'Comment favorited successfully.'}, status=status.HTTP_200_OK)
    
    # Unfavorite a comment
    @swagger_auto_schema(
        tags=['Comment'],
        operation_description="Unfavorite a comment",
        responses={
            200: openapi.Response(
                description="Comment unfavorited successfully",
                examples={
                    "application/json": {
                        "message": "Comment unfavorited successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "message": "You have not favorited this comment yet."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"message": "Invalid token."},
                        {"message": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
             404: openapi.Response(
                description="Not Found (Submission)",
                examples={
                    "application/json": {
                        "message": "Submission not found"
                    }
                }
            ),
            404: openapi.Response(
                description="Not Found (Comment)",
                examples={
                    "application/json": {
                        "message": "No comment with such an ID."
                    }
                }
            )
        }
    )
    def delete(self, request, submission_id, comment_id):
        self.check_permissions(request)

        try:
            submission = Submission.objects.get(id=submission_id)
            comment = Comment.objects.get(id=comment_id, submission=submission)
        except Submission.DoesNotExist:
            return Response({"message": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"message": "No comment with such an ID."}, status=status.HTTP_404_NOT_FOUND)

        favorite_comment = Favorite_comment.objects.filter(user=request.user, comment=comment).first()
        if not favorite_comment:
            return Response({'message': 'You have not favorited this comment yet.'},
                            status=status.HTTP_400_BAD_REQUEST)

        favorite_comment.delete()
        return Response({'message': 'Comment unfavorited successfully.'}, status=status.HTTP_200_OK)
    
    def check_permissions(self, request):
        if request.method in ['POST', 'DELETE']:
            super().check_permissions(request)

class Submission_HideAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # Hide a submission
    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Hide a submission",
        responses={
            200: openapi.Response(
                description="Submission hidden successfully",
                examples={
                    "application/json": {
                        "message": "Submission hidden successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "message": "You have already hidden this submission."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"message": "Invalid token."},
                        {"message": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "message": "No submission with such an ID."
                    }
                }
            )
        }
    )
    def post(self, request, id):
        self.check_permissions(request)
        try:
            submission = get_object_or_404(Submission, id=id)
        except Http404:
            return Response({'message': 'No submission with such an ID.'}, status=status.HTTP_404_NOT_FOUND)
        if HiddenSubmission.objects.filter(user=request.user, submission=submission).exists():
            return Response({'message': 'You have already hidden this submission.'},
                            status=status.HTTP_400_BAD_REQUEST)
        HiddenSubmission.objects.create(user=request.user, submission=submission)
        return Response({'message': 'Submission hidden successfully.'}, status=status.HTTP_200_OK)

    # Unhide a submission
    @swagger_auto_schema(
        tags=['Submission'],
        operation_description="Unhide a submission",
        responses={
            200: openapi.Response(
                description="Submission unhidden successfully",
                examples={
                    "application/json": {
                        "message": "Submission unhidden successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "message": "This submission is not hidden."
                    }
                }
            ),
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": [
                        {"message": "Invalid token."},
                        {"message": "Invalid token header. No credentials provided."}
                    ]
                }
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "message": "No submission with such an ID."
                    }
                }
            )
        }
    )
    def delete(self, request, id):
        self.check_permissions(request)
        try:
            submission = get_object_or_404(Submission, id=id)
        except Http404:
            return Response({'message': 'No submission with such an ID.'}, status=status.HTTP_404_NOT_FOUND)
        hidden_submission = HiddenSubmission.objects.filter(user=request.user, submission=submission).first()
        if not hidden_submission:
            return Response({'message': 'This submission is not hidden.'}, status=status.HTTP_400_BAD_REQUEST)
        hidden_submission.delete()
        return Response({'message': 'Submission unhidden successfully.'}, status=status.HTTP_200_OK)

    def check_permissions(self, request):
        if request.method in ['POST', 'DELETE']:
            super().check_permissions(request)
