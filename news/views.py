from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Submission, HiddenSubmission, UpvotedSubmission
from .models import Submission_URL, Submission_ASK
from .forms import SubmissionForm


def news(request):
    if request.user.is_authenticated:
        hidden_submissions = HiddenSubmission.objects.filter(user=request.user).values_list('submission', flat=True)
        submissions = Submission.objects.exclude(id__in=hidden_submissions).order_by('title')
        voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)
        return render(request, 'news.html', {'submissions': submissions, 'voted_submissions': voted_submissions})
    else:
        submissions = Submission.objects.all().order_by('title')
        return render(request, 'news.html', {'submissions': submissions})


@login_required
def submit(request):
    if request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission_data = form.save(commit=False)
            submission_data.author = request.user  # Link the submission with the current user
            if submission_data.url:
                Submission_URL.objects.create(
                    title=submission_data.title,
                    url=submission_data.url,
                    text=submission_data.text,
                    author=submission_data.author
                )
            else:
                Submission_ASK.objects.create(
                    title=submission_data.title,
                    text=submission_data.text,
                    author=submission_data.author
                )
            return redirect('news:news')  # Redirect to the main page
    else:
        form = SubmissionForm()
    return render(request, 'submit.html', {'form': form})

def newest(request):
    voted_submissions = []
    if request.user.is_authenticated:
        hidden_submissions = HiddenSubmission.objects.filter(user=request.user).values_list('submission', flat=True)
        submissions = Submission.objects.exclude(id__in=hidden_submissions).order_by('-created')
        voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)
    else:
        submissions = Submission.objects.all().order_by('-created')
    return render(request, 'news.html', {'submissions': submissions, 'voted_submissions': voted_submissions})

def ask(request):
    submissions = Submission_ASK.objects.all()
    logged_in_username = request.user.username if request.user.is_authenticated else None
    return render(request, 'ask.html', {'submissions': submissions, 'logged_in_username': logged_in_username})

def detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    return render(request, 'detail.html', {'submission': submission})

@login_required
def hide_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    HiddenSubmission.objects.get_or_create(user=request.user, submission=submission)
    return redirect('news:news')

#eliminar submission propia
@login_required
def delete_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if submission.author == request.user:
        submission.delete()
    return redirect('news:news')

#busqueda
def search(request):
    query = request.GET.get('q')
    if query:
        results = Submission.objects.filter(title__icontains=query)
    else:
        results = Submission.objects.none()
    return render(request, 'search_results.html', {'results': results})