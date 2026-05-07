from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.core.paginator import Paginator
from .models import User
from .forms import RegisterForm, LoginForm, UserEditForm, ChangePasswordForm


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'users/register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('projects:project_list')


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(self.request, email=email, password=password)
        if user:
            login(self.request, user)
            return redirect('projects:project_list')
        else:
            form.add_error(None, 'Неверный имейл или пароль')
            return self.form_invalid(form)


class LogoutView(LoginRequiredMixin, FormView):
    def get(self, request):
        logout(request)
        return redirect('projects:project_list')


class UserListView(ListView):
    model = User
    template_name = 'users/participants.html'
    context_object_name = 'participants'
    paginate_by = 12

    def get_queryset(self):
        queryset = User.objects.filter(is_active=True).order_by('-id')
        filter_param = self.request.GET.get('filter')
        if filter_param and self.request.user.is_authenticated:
            if filter_param == 'owners-of-favorite-projects':
                # Authors of favorite projects
                favorite_projects = self.request.user.favorites.all()
                author_ids = favorite_projects.values_list('owner', flat=True).distinct()
                queryset = queryset.filter(id__in=author_ids)
            elif filter_param == 'owners-of-participating-projects':
                # Authors of projects where user participates
                participated_projects = self.request.user.participated_projects.all()
                author_ids = participated_projects.values_list('owner', flat=True).distinct()
                queryset = queryset.filter(id__in=author_ids)
            elif filter_param == 'interested-in-my-projects':
                # Users who have user's projects in favorites
                user_projects = self.request.user.owned_projects.all()
                liker_ids = user_projects.values_list('interested_users', flat=True).distinct()
                queryset = queryset.filter(id__in=liker_ids)
            elif filter_param == 'participants-of-my-projects':
                # Participants in user's projects
                user_projects = self.request.user.owned_projects.all()
                participant_ids = user_projects.values_list('participants', flat=True).distinct()
                queryset = queryset.filter(id__in=participant_ids)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_filter'] = self.request.GET.get('filter')
        return context


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user-details.html'
    context_object_name = 'user'


class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'users/edit_profile.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('users:user_detail', kwargs={'pk': self.request.user.pk})


class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = ChangePasswordForm
    template_name = 'users/change_password.html'

    def form_valid(self, form):
        user = self.request.user
        if user.check_password(form.cleaned_data['old_password']):
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            login(self.request, user)
            return redirect('users:user_detail', pk=user.pk)
        else:
            form.add_error('old_password', 'Неверный пароль')
            return self.form_invalid(form)
