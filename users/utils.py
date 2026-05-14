import re
from urllib.parse import urlparse

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

def avatar_upload_path(instance, filename: str) -> str:
    extension = filename.split(".")[-1].lower() if "." in filename else "png"
    if instance.pk:
        return f"avatars/user_{instance.pk}_avatar.{extension}"
    return f"avatars/user_avatar.{extension}"


def normalize_phone(phone: str | None) -> str | None:
    phone = (phone or "").strip()
    if not phone:
        return None
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if re.fullmatch(r"8\d{10}", phone):
        return "+7" + phone[1:]
    if re.fullmatch(r"\+7\d{10}", phone):
        return phone
    return phone


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