from urllib.parse import urlparse

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


def validate_login_credentials(request, email: str, password: str):
    user = authenticate(request, username=email, password=password)
    if user is None:
        raise ValidationError("Неверный имейл или пароль")
    return user


def validate_github_url(url: str) -> str:
    if not url:
        return url
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if host.endswith("github.com"):
        return url
    raise ValidationError("Ссылка должна вести на GitHub.")


AVATAR_SIZE = 256


def validate_github_url(url: str) -> str:
    if not url:
        return url
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if host.endswith("github.com"):
        return url
    raise ValidationError("Ссылка должна вести на GitHub.")


AVATAR_SIZE = 256
