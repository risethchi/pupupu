from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from config import (
    PROJECT_CREATE_VIEW,
    PROJECT_DETAIL_VIEW,
    PROJECT_FAVORITE_VIEW,
    PROJECT_LIST_VIEW,
    USER_LIST_PAGINATE_BY,
)

from .forms import ProjectForm
from .models import Project


class ProjectListView(ListView):
    template_name = PROJECT_LIST_VIEW
    context_object_name = "projects"
    paginate_by = USER_LIST_PAGINATE_BY

    def get_queryset(self):
        return Project.objects.select_related("owner").prefetch_related("participants")


class FavoriteProjectsView(LoginRequiredMixin, ListView):
    template_name = PROJECT_FAVORITE_VIEW
    context_object_name = "projects"

    def get_queryset(self):
        return (
            self.request.user.favorites.select_related("owner").prefetch_related(
                "participants"
            )
        )


class CreateProjectView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = PROJECT_CREATE_VIEW

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()
        project.participants.add(self.request.user)  # Owner is participant
        return redirect(reverse("projects:project_detail", kwargs={"pk": project.pk}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = PROJECT_DETAIL_VIEW
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.select_related("owner").prefetch_related("participants")


class EditProjectView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = PROJECT_CREATE_VIEW

    def get_queryset(self):
        return self.request.user.owned_projects.select_related("owner").prefetch_related(
            "participants"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context


class CompleteProjectView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = []

    def get_queryset(self):
        return self.request.user.owned_projects.filter(status=Project.Status.OPEN)

    def form_valid(self, form):
        project = form.save(commit=False)
        project.status = Project.Status.CLOSED
        project.save()
        return JsonResponse(
            {"status": "ok", "project_status": Project.Status.CLOSED}
        )


class ToggleParticipateView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = []

    def form_valid(self, form):
        project = form.instance
        user = self.request.user
        if project.participants.filter(pk=user.pk).exists():
            project.participants.remove(user)
        else:
            project.participants.add(user)
        return JsonResponse({"status": "ok"})


class ToggleFavoriteView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = []

    def form_valid(self, form):
        project = form.instance
        user = self.request.user
        if project.interested_users.filter(pk=user.pk).exists():
            project.interested_users.remove(user)
            favorited = False
        else:
            project.interested_users.add(user)
            favorited = True
        return JsonResponse({"status": "ok", "favorited": favorited})
