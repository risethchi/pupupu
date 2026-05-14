from __future__ import annotations

import re

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import URLValidator
from django.db import models

from .constants import (
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    ABOUT_MAX_LENGTH,
)


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


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH, verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH, verbose_name="Фамилия"
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path, blank=True, verbose_name="Аватар"
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Телефон",
    )
    github_url = models.URLField(
        blank=True, validators=[URLValidator()], verbose_name="GitHub"
    )
    about = models.CharField(
        max_length=ABOUT_MAX_LENGTH, blank=True, verbose_name="О себе"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")

    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Избранные проекты",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ["-id"]

    def __str__(self) -> str:
        return self.email

    def clean(self):
        super().clean()
        self.email = (self.email or "").lower().strip()
        self.phone = normalize_phone(self.phone)