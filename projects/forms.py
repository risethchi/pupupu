from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError

from .models import Project
from .utils import validate_github_url


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
