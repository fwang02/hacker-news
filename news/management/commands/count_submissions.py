from django.core.management.base import BaseCommand
from news.models import Submission, Submission_URL, Submission_ASK

class Command(BaseCommand):
    help = 'Count the number of Submissions, Submission_URL, and Submission_ASK'

    def handle(self, *args, **kwargs):
        total_submissions = Submission.objects.count()
        total_urls = Submission_URL.objects.count()
        total_asks = Submission_ASK.objects.count()

        self.stdout.write(f'Total Submissions: {total_submissions}')
        self.stdout.write(f'Total Submission_URL: {total_urls}')
        self.stdout.write(f'Total Submission_ASK: {total_asks}')

        self.stdout.write('\nTitles of Submission_ASK:')
        for ask in Submission_ASK.objects.all():
            self.stdout.write(f'- {ask.title}')




"""
python manage.py count_submissions
"""