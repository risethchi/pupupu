from enum import Enum

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from config import (
    LOGIN_VIEW,
    PARTICIPANTS_VIEW,
    REGISTER_VIEW,
    USER_CHANGE_PASSWORD_VIEW,
    USER_DETAIL_VIEW,
    USER_EDIT_VIEW,
    USER_LIST_PAGINATE_BY,
)

from .forms import ChangePasswordForm, LoginForm, RegisterForm, UserEditForm
from .models import User


class UserFilter(Enum):
    OWNERS_OF_FAVORITE_PROJECTS = "owners-of-favorite-projects"
    OWNERS_OF_PARTICIPATING_PROJECTS = "owners-of-participating-projects"
    INTERESTED_IN_MY_PROJECTS = "interested-in-my-projects"
    PARTICIPANTS_OF_MY_PROJECTS = "participants-of-my-projects"


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = REGISTER_VIEW

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("projects:project_list")


class LoginView(FormView):
    form_class = LoginForm
    template_name = LOGIN_VIEW

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = authenticate(self.request, email=email, password=password)
        if not user:
            form.add_error(None, "Неверный имейл или пароль")
            return self.form_invalid(form)

        login(self.request, user)
        return redirect("projects:project_list")


class LogoutView(LoginRequiredMixin, FormView):
    def get(self, request):
        logout(request)
        return redirect("projects:project_list")


class UserListView(ListView):
    template_name = PARTICIPANTS_VIEW
    context_object_name = "participants"
    paginate_by = USER_LIST_PAGINATE_BY

    def get_queryset(self):
        # Сортировка задана в Meta модели User
        queryset = User.objects.filter(is_active=True)

        filter_param = self.request.GET.get("filter")
        if filter_param and self.request.user.is_authenticated:
            if filter_param == UserFilter.OWNERS_OF_FAVORITE_PROJECTS.value:
                favorite_projects = self.request.user.favorites.all()
                author_ids = favorite_projects.values_list("owner", flat=True).distinct()
                queryset = queryset.filter(id__in=author_ids)
            elif filter_param == UserFilter.OWNERS_OF_PARTICIPATING_PROJECTS.value:
                participated_projects = self.request.user.participated_projects.all()
                author_ids = participated_projects.values_list("owner", flat=True).distinct()
                queryset = queryset.filter(id__in=author_ids)
            elif filter_param == UserFilter.INTERESTED_IN_MY_PROJECTS.value:
                user_projects = self.request.user.owned_projects.all()
                liker_ids = user_projects.values_list("interested_users", flat=True).distinct()
                queryset = queryset.filter(id__in=liker_ids)
            elif filter_param == UserFilter.PARTICIPANTS_OF_MY_PROJECTS.value:
                user_projects = self.request.user.owned_projects.all()
                participant_ids = user_projects.values_list("participants", flat=True).distinct()
                queryset = queryset.filter(id__in=participant_ids)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_filter"] = self.request.GET.get("filter")
        return context


class UserDetailView(DetailView):
    model = User
    template_name = USER_DETAIL_VIEW
    context_object_name = "user"


class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = USER_EDIT_VIEW

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse("users:user_detail", kwargs={"pk": self.request.user.pk})


class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = ChangePasswordForm
    template_name = USER_CHANGE_PASSWORD_VIEW

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        if not user.check_password(form.cleaned_data["old_password"]):
            form.add_error("old_password", "Неверный пароль")
            return self.form_invalid(form)

        user.set_password(form.cleaned_data["new_password1"])
        user.save()
        login(self.request, user)
        return redirect("users:user_detail", pk=user.pk)