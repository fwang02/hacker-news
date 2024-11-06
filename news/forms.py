from django import forms
from .models import Submission

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

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        text = cleaned_data.get('text')

        if not url and not text:
            raise forms.ValidationError("At least one of URL or text must be provided.")
        return cleaned_data