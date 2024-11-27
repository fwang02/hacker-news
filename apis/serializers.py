from rest_framework import serializers
from news.models import Submission, Comment, Submission_ASK, Submission_URL

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

class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['title', 'url', 'text']

    def create(self, validated_data):
        if 'url' in validated_data and validated_data['url']:
            submission = Submission_URL.objects.create(**validated_data)
        else:
            submission = Submission_ASK.objects.create(**validated_data)
        return submission

    def validate(self, data):
        if not data.get('url') and not data.get('text'):
            raise serializers.ValidationError("Either 'url' or 'text' must be provided.")
        return data

    def validate_title(self, value):
        #Ensure the title is unique.
        if Submission.objects.filter(title=value).exists():
            raise serializers.ValidationError("A submission with this title already exists.")
        return value