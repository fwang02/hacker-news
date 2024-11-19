from django import forms
from django.forms import ClearableFileInput
from .models import Profile

class CustomClearableFileInput(ClearableFileInput):
    template_name = 'custom_clearable_file_input.html'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar','banner','about']