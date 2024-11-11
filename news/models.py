from django.db import models
from django.contrib.auth.models import User

class Submission(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class Submission_URL(Submission):
    pass

class Submission_ASK(Submission):
    pass

class HiddenSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return f"/news/{self.id}"
    
class Comment(models.Model):
    submission = models.ForeignKey(Submission, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "self.text"
    class Meta:
        ordering = ['created']

    def save(self, commit=True):
        comment = super().save(commit=False)
        comment.author = self.user  # Establecer el autor del comentario
        if commit:
            comment.save()
        return comment

