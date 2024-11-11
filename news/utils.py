from urllib.parse import urlparse

def get_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    domain_parts = domain.split('.')
    if len(domain_parts) > 2:
        domain = '.'.join(domain_parts[-2:])
    return domain