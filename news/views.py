from django.shortcuts import render, redirect, get_object_or_404
from .models import Submission, Comment
from .forms import SubmissionForm, CommentForm

def news(request):
    submissions = Submission.objects.all().order_by('-created')
    return render(request, 'news.html', {'submissions': submissions})

def submit(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('news')
    else:
        form = SubmissionForm()
    return render(request, 'submit.html', {'form': form})

def newest(request):
    submissions = Submission.objects.all().order_by('-created')
    return render(request, 'newest.html', {'submissions': submissions})

def submission_details(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    comments = submission.comments.all()  
    print("Comentarios:", comments)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.submission = submission 
            comment.save()
            return redirect(f'/news/{submission_id}#comments')
    else:
        form = CommentForm()
    return render(request, 'submission_details.html', {'submission': submission, 'comments': comments, 'form': form})