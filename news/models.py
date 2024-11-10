from django.db import models
from django.contrib.auth.models import User

class Submission(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    point = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.author.profile.addKarma(1)
        super().save(*args, **kwargs)

    def add_point(self):
        self.point += 1
        self.author.profile.addKarma(1)
        self.save()

    def subtract_point(self):
        if self.point > 0:
            self.point -= 1
            self.author.profile.reduceKarma(1)
            self.save()

class Submission_URL(Submission):
    pass

class Submission_ASK(Submission):
    pass

class HiddenSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

class UpvotedSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'submission')