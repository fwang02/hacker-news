from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProfileForm
from news.models import Submission  # Assuming you have a Submission model in the news app

def profile(request):
    user_id = request.GET.get('id')
    user = get_object_or_404(User, username=user_id) if user_id else request.user

    if request.user == user:
        if request.method == 'POST':
            form = ProfileForm(request.POST, instance=user.profile)
            if form.is_valid():
                form.save()
                return redirect('users:profile')
        else:
            form = ProfileForm(instance=user.profile)
        return render(request, 'profile.html', {'form': form, 'username': user.username, 'logged_in_username': request.user.username})
    else:
        return render(request, 'profile_public.html', {'user': user, 'logged_in_username': request.user.username})

def submissions(request):
    user_id = request.GET.get('id')
    user = get_object_or_404(User, username=user_id)
    submissions = Submission.objects.filter(author=user)  # Usa el nombre correcto del campo
    return render(request, 'submissions.html', {'submissions': submissions, 'username': user.username})