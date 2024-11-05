from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Submission
from .models import Submission_URL, Submission_ASK
from .forms import SubmissionForm

def news(request):
    submissions = Submission.objects.all().order_by('title')
    return render(request, 'news.html', {'submissions': submissions})

@login_required
def submit(request):
    if request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            if submission.url:
                Submission_URL.objects.create(
                    title=submission.title,
                    url=submission.url,
                    text=submission.text,
                    created=submission.created
                )
            else:
                Submission_ASK.objects.create(
                    title=submission.title,
                    text=submission.text,
                    created=submission.created
                )
            return redirect('news')  # Redirigir a la página principal
    else:
        form = SubmissionForm()
    return render(request, 'submit.html', {'form': form})
"""TODO: Linkar con usuario"""

def newest(request):
    submissions = Submission.objects.all().order_by('-created')
    return render(request, 'newest.html', {'submissions': submissions})

def ask(request):
    submissions = Submission_ASK.objects.all()
    return render(request, 'news.html', {'submissions': submissions})