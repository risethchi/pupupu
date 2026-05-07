from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Project
from .forms import ProjectForm


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        return Project.objects.all()


class FavoriteProjectsView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/favorite_projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return self.request.user.favorites.all()


class CreateProjectView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()
        project.participants.add(self.request.user)  # Owner is participant
        return redirect(project.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'


class EditProjectView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def get_queryset(self):
        return self.request.user.owned_projects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class CompleteProjectView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = []

    def get_queryset(self):
        return self.request.user.owned_projects.filter(status='open')

    def form_valid(self, form):
        project = form.save(commit=False)
        project.status = 'closed'
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})


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
        return JsonResponse({'status': 'ok'})


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
        return JsonResponse({'status': 'ok', 'favorited': favorited})
