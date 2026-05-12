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
    model = Project
    template_name = PROJECT_LIST_VIEW
    context_object_name = "projects"
    paginate_by = USER_LIST_PAGINATE_BY

    def get_queryset(self):
        return Project.objects.all()


class FavoriteProjectsView(LoginRequiredMixin, ListView):
    model = Project
    template_name = PROJECT_FAVORITE_VIEW
    context_object_name = "projects"

    def get_queryset(self):
        return self.request.user.favorites.all()


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


class EditProjectView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = PROJECT_CREATE_VIEW

    def get_queryset(self):
        return self.request.user.owned_projects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context


class CompleteProjectView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = []

    def get_queryset(self):
        return self.request.user.owned_projects.filter(status="open")

    def form_valid(self, form):
        project = form.save(commit=False)
        project.status = "closed"
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})


class ToggleParticipateView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = []

    def form_valid(self, form):
        project = form.instance
        user = self.request.user
        if user in project.participants.all():
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
        if user in project.interested_users.all():
            project.interested_users.remove(user)
            favorited = False
        else:
            project.interested_users.add(user)
            favorited = True
        return JsonResponse({"status": "ok", "favorited": favorited})
