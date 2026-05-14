from django import forms

from .models import Project
from .utils import validate_github_url


class ProjectForm(forms.ModelForm):
    STATUS_RU_CHOICES = [
        (Project.Status.OPEN, "Открыт"),
        (Project.Status.CLOSED, "Закрыт"),
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
