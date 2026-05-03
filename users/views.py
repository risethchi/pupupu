from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from .forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm
from .models import User


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/users/login/")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            auth_login(request, form.user)
            return redirect("/projects/list")
    else:
        form = LoginForm(request=request)
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    return redirect("/projects/list")


@require_GET
def user_detail_view(request, user_id: int):
    user = get_object_or_404(User.objects.prefetch_related("owned_projects"), pk=user_id)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f"/users/{request.user.id}")
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f"/users/{request.user.id}")
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, "users/change_password.html", {"form": form})


@require_GET
def participants_list_view(request):
    qs = User.objects.all().order_by("-id")
    active_filter = ""

    if request.user.is_authenticated:
        requested = (request.GET.get("filter") or "").strip()
        if requested:
            active_filter = requested
            if requested == "owners-of-favorite-projects":
                qs = qs.filter(owned_projects__in=request.user.favorites.all())
            elif requested == "owners-of-participating-projects":
                qs = qs.filter(owned_projects__in=request.user.participated_projects.all())
            elif requested == "interested-in-my-projects":
                qs = qs.filter(favorites__in=request.user.owned_projects.all())
            elif requested == "participants-of-my-projects":
                qs = qs.filter(participated_projects__in=request.user.owned_projects.all())
            qs = qs.distinct()

    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "users/participants.html",
        {"participants": page, "active_filter": active_filter},
    )
