from rest_framework import serializers
from news.models import Submission, Comment

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at', 'level', 'point', 'submission', 'parent', 'author']


class CommentSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at', 'level', 'point', 'submission', 'parent', 'author', 'replies']


class SubmissionSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ['id', 'title', 'url', 'domain', 'text', 'point', 'comment_count', 'created', 'author', 'comments']

    def get_comments(self, obj):
        # Serializamos solo los comentarios raíz (sin padre)
        root_comments = obj.comments.filter(parent__isnull=True)
        return CommentSerializer(root_comments, many=True).data
