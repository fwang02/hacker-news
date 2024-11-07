from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProfileForm
from news.models import Submission, HiddenSubmission  # Assuming you have a Submission model in the news app


def profile(request):
    user_id = request.GET.get('id')
    # `user` es el perfil consultado, mientras que `logged_in_user` es el usuario autenticado
    user = get_object_or_404(User, username=user_id) if user_id else request.user
    logged_in_user = request.user  # Usuario autenticado, siempre será el mismo

    if logged_in_user == user:
        if request.method == 'POST':
            form = ProfileForm(request.POST, instance=user.profile)
            if form.is_valid():
                form.save()
                return redirect('users:profile')
        else:
            form = ProfileForm(instance=user.profile)
        return render(request, 'profile.html', {
            'form': form,
            'user': user,  # El perfil visualizado
            'logged_in_user': logged_in_user  # El usuario autenticado
        })
    else:
        return render(request, 'profile_public.html', {
            'user': user,
            'logged_in_user': logged_in_user  # El usuario autenticado
        })





def submissions(request):
    user_id = request.GET.get('id')
    user = get_object_or_404(User, username=user_id)
    submissions = Submission.objects.filter(author=user)  # Usa el nombre correcto del campo
    return render(request, 'submissions.html', {'submissions': submissions, 'username': user.username})


@login_required
def hidden_submissions(request):
    hidden_submissions_ids = HiddenSubmission.objects.filter(user=request.user).values_list('submission', flat=True)
    submissions = Submission.objects.filter(id__in=hidden_submissions_ids)
    return render(request, 'hidden.html', {'submissions': submissions, 'username': request.user.username})

@login_required
def unhide_submission(request, submission_id):
    HiddenSubmission.objects.filter(user=request.user, submission_id=submission_id).delete()
    return redirect('users:hidden_submissions')