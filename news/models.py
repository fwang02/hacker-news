from django.db import models

class Submission(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/news/{self.id}"

    def save(self, *args, **kwargs):
        if self.url:
            self.__class__ = Submission_URL
        else:
            self.__class__ = Submission_ASK
        super(Submission, self).save(*args, **kwargs)

class Submission_URL(Submission):
    pass

class Submission_ASK(Submission):
    pass