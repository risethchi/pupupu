from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError

from .models import Project


def validate_github_url(url: str) -> str:
    if not url:
        return url
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if host.endswith("github.com"):
        return url
    raise ValidationError("Ссылка должна вести на GitHub.")


class ProjectForm(forms.ModelForm):
    STATUS_RU_CHOICES = [
        (Project.STATUS_OPEN, "Открыт"),
        (Project.STATUS_CLOSED, "Закрыт"),
    ]

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название",
            "description": "Описание",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = self.STATUS_RU_CHOICES

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url", ""))

