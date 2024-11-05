from django import template
from urllib.parse import urlparse

register = template.Library()

@register.filter
def domain(url):
    parsed_uri = urlparse(url)
    return '{uri.netloc}'.format(uri=parsed_uri)