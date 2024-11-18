from urllib.parse import urlparse
from django.utils.timezone import now
from datetime import timedelta, datetime
from django.utils import timezone
import math

def get_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    domain_parts = domain.split('.')
    if len(domain_parts) > 2:
        domain = '.'.join(domain_parts[-2:])
    return domain

def calculate_account_age(date_joined):
    delta = now() - date_joined
    if delta < timedelta(hours=1):
        return f"{delta.seconds // 60} minutes ago"
    elif delta < timedelta(days=1):
        return f"{delta.seconds // 3600} hours ago"
    elif delta < timedelta(days=30):
        return f"{delta.days} days ago"
    elif delta < timedelta(days=365):
        return f"{delta.days // 30} months ago"
    else:
        return f"{delta.days // 365} years ago"


def calculate_score(submission, k=1):
    # Calcular el tiempo transcurrido en minutos
    age_in_minutes = (timezone.now() - submission.created).total_seconds() / 60

    # Fórmula para ajustar el puntaje: más reciente = más relevante, penaliza suavemente el tiempo
    adjusted_score = submission.point / (1 + (age_in_minutes / k))

    return adjusted_score