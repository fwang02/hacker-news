from django.shortcuts import render, redirect
from .models import Submission
from .forms import SubmissionForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib import messages


def news(request):
    submissions = Submission.objects.all().order_by('-created')
    return render(request, 'news.html', {'submissions': submissions})

def login(request):
    return render(request, 'login.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Corrected function call
            return redirect('/news')
        else:
            messages.error(request, 'Bad login')
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
        try:
            user = User.objects.create_user(username=username, password=password)
            auth_login(request, user)
            return redirect('news')
        except Exception as e:
            return render(request, 'create_account.html', {'error': str(e)})
    return render(request, 'create_account.html')

def logout(request):
    auth_logout(request)
    return redirect('news')