from django import forms
from django.core.exceptions import ValidationError

from .models import Submission
from .models import Comment

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['title', 'url', 'text']
        labels = {
            'title': 'title',
            'url': 'url',
            'text': 'text',  # Cambia este texto
        }

    def __init__(self, *args, **kwargs):
        super(SubmissionForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label_suffix = ''  # Remove the colon

    def clean_url(self):
        url = self.cleaned_data.get('url')
        if url:
            existing_submission = Submission.objects.filter(url=url).first()
            if existing_submission:
                raise ValidationError(f"URL already exists:{existing_submission.id}")
        return url

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        text = cleaned_data.get('text')

        if not url and not text:
            raise forms.ValidationError("At least one of URL or text must be provided.")
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # Usamos el campo 'text' del modelo
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Your Comment'})  # Añades un widget para el campo 'text'
        }

class EditSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['title']