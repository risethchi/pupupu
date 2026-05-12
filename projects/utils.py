from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_github_url(url: str) -> str:
    if not url:
        return url
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if host.endswith("github.com"):
        return url
    raise ValidationError("Ссылка должна вести на GitHub.")