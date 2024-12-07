from operator import is_not

from rest_framework import serializers
from users.models import Profile
from news.models import Submission, Comment, Submission_ASK, Submission_URL


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at', 'level', 'point', 'submission', 'parent', 'author', 'replies']

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.parent is None:
            representation.pop('parent')
        return representation


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'title', 'url', 'domain', 'text', 'point', 'comment_count', 'created', 'author']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.url:
            representation.pop('url')
            representation.pop('domain')
        return representation

class SubmissionDetailSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ['id', 'title', 'url', 'domain', 'text', 'point', 'comment_count', 'created', 'author', 'comments']

    def get_comments(self, obj):
        # Serializamos solo los comentarios raíz (sin padre)
        root_comments = obj.comments.filter(parent__isnull=True)
        return CommentSerializer(root_comments, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.url:
            representation.pop('url')
            representation.pop('domain')
        return representation

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

    def validate_url(self, value):
        #Ensure the title is unique.
        if Submission.objects.filter(url=value).exists():
            raise serializers.ValidationError("A submission with this url already exists.")
        return value


class SubmissionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['title']

    def validate_title(self, value):
        if Submission.objects.filter(title=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A submission with this title already exists.")
        return value

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = ['user_id', 'username', 'karma', 'about', 'banner', 'avatar']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['about']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text', 'parent']  # El serializer ya no incluye 'submission', lo pasamos en la vista

    def create(self, validated_data):
        # Obtener el ID de la Submission desde el contexto
        submission = self.context.get('submission')  # El 'submission' se pasa desde la vista

        # Asignar la 'submission' al comentario
        validated_data['submission'] = submission
        
        # Si el comentario tiene un 'parent', ajustamos su nivel
        parent = validated_data.get('parent')
        if parent:
            validated_data['level'] = parent.level + 1

        return super().create(validated_data)

    def validate(self, data):
        # Validar que el campo 'text' esté presente
        if not data.get('text'):
            raise serializers.ValidationError("The 'text' field is required.")
        return data


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']  

    def validate_text(self, value):
        # Validar que el texto no esté vacío
        if not value.strip(): 
            raise serializers.ValidationError("The 'text' field cannot be empty.")
        
        return value