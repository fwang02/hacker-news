from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProfileForm

@login_required
def profile(request):
    user_id = request.GET.get('id')
    user = get_object_or_404(User, username=user_id) if user_id else request.user

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user.profile)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=user.profile)

    return render(request, 'profile.html', {'form': form, 'username': user.username})