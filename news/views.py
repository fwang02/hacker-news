from django.shortcuts import render, redirect
from .models import Submission
from .forms import SubmissionForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login


def news(request):
    submissions = Submission.objects.all().order_by('-created')
    return render(request, 'news.html', {'submissions': submissions})

def login(request):
    return render(request, 'login.html')

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


def create_account(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return render(request, 'create_account.html', {'error': 'That username is taken. Please choose another.'})
        user = User.objects.create_user(username=username, password=password)
        auth_login(request, user)
        return render(request, 'create_account.html', {'success': True})
    return render(request, 'create_account.html')