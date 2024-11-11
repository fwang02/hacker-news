from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from users.utils import calculate_date
from .models import Submission, HiddenSubmission, UpvotedSubmission, Comment
from .models import Submission_URL, Submission_ASK
from .forms import SubmissionForm, CommentForm
from django.http import JsonResponse, Http404
from django.contrib import messages



def news(request):
    if request.user.is_authenticated:
        hidden_submissions = HiddenSubmission.objects.filter(user=request.user).values_list('submission', flat=True)
        submissions = Submission.objects.exclude(id__in=hidden_submissions).order_by('title')

        for submission in submissions:
            submission.comment_count = submission.comments.count()

        voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)
        return render(request, 'news.html', {'submissions': submissions, 'voted_submissions': voted_submissions})
    else:
        submissions = Submission.objects.all().order_by('title')

        for submission in submissions:
            submission.comment_count = submission.comments.count()
        return render(request, 'news.html', {'submissions': submissions})

    
    # Contar los comentarios asociados a cada publicación

    logged_in_username = request.user.username if request.user.is_authenticated else None
    return render(request, 'news.html', {'submissions': submissions, 'logged_in_username': logged_in_username})


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

    submissions = Submission.objects.all().order_by('-created')
    return render(request, 'newest.html', {'submissions': submissions})


def submission_details(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    comments = submission.comments.all()
    submission.comment_count = submission.comments.count()  # Actualiza el contador de comentarios

    # Procesar el formulario de comentarios
    if request.method == 'POST':
        if not request.user.is_authenticated:  # Verifica si el usuario no está autenticado
            messages.error(request, "Debes estar logueado para comentar.")  # Mensaje de error
            return redirect('news:submission_detail', submission_id=submission.id)

        form = CommentForm(request.POST)  # Instancia del formulario con los datos POST
        if form.is_valid():  # Verifica que el formulario sea válido
            comment = form.save(commit=False)
            comment.submission = submission  # Relaciona el comentario con la publicación
            comment.author = request.user  # Establece el autor del comentario como el usuario logueado
            comment.save()  # Guarda el comentario en la base de datos

            # Redirige para evitar que el comentario se reenvíe al actualizar la página
            return redirect('news:submission_detail', submission_id=submission.id)

    else:
        form = CommentForm()  # Si es un GET, el formulario estará vacío

    return render(request, 'submission_details.html', {'submission': submission, 'comments': comments, 'form': form})


@login_required
def confirm_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    submission = comment.submission
    if comment.author != request.user:
        return redirect('news:submission_detail', submission_id=comment.submission.id)

    if request.method == 'POST':
        comment.delete()
        return redirect('news:submission_detail', submission_id=comment.submission.id)

    return render(request, 'confirm_delete.html', {'comment': comment, 'submission': submission})

def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        raise Http404("You are not allowed to delete this comment.")

    comment.delete()
    return redirect('news:submission_detail', submission_id=comment.submission.id)

def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Verificar si el usuario es el autor del comentario
    if comment.author != request.user:
        messages.error(request, "You do not have permission to edit this comment.")
        return redirect('news:submission_detail', submission_id=comment.submission.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)  # Rellenar el formulario con los datos del comentario
        if form.is_valid():
            form.save()  # Guardar el comentario editado
            return redirect('news:submission_detail', submission_id=comment.submission.id)
    else:
        form = CommentForm(instance=comment)  # Si es un GET, mostrar el formulario con los datos del comentario

    return render(request, 'edit_comment.html', {'form': form, 'comment': comment})

def submissions_by_domain(request):
    domain = request.GET.get('domain')
    submissions = Submission.objects.filter(domain=domain)
    voted_submissions = []
    if request.user.is_authenticated:
        voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)
    return render(request, 'submissions_by_domain.html', {'submissions': submissions, 'domain': domain, 'voted_submissions': voted_submissions})

