from __future__ import annotations

import random
import re
from io import BytesIO

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.files.base import ContentFile
from django.core.validators import URLValidator
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from .utils import AVATAR_SIZE


def avatar_upload_path(instance, filename: str) -> str:
    extension = filename.split('.')[-1].lower() if '.' in filename else 'png'
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
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True)
    phone = models.CharField(max_length=12, unique=True, blank=True, null=True)
    github_url = models.URLField(blank=True, validators=[URLValidator()])
    about = models.CharField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    def clean(self):
        super().clean()
        self.email = (self.email or "").lower().strip()
        self.phone = normalize_phone(self.phone)

    def save(self, *args, **kwargs):
        self.email = (self.email or "").lower().strip()
        self.phone = normalize_phone(self.phone)
        creating = self._state.adding
        old_avatar = None
        if not creating:
            existing = self.__class__.objects.filter(pk=self.pk).only("avatar").first()
            if existing and existing.avatar and self.avatar and existing.avatar.name != self.avatar.name:
                old_avatar = existing.avatar
        if old_avatar:
            old_avatar.delete(save=False)
        super().save(*args, **kwargs)
        if creating and not self.avatar:
            self._generate_avatar()

    def _generate_avatar(self):
        letter = (self.name or "?").strip()[:1].upper() or "?"
        bg_colors = [
            "#3F51B5",
            "#009688",
            "#607D8B",
            "#795548",
            "#673AB7",
            "#2196F3",
        ]
        bg = random.choice(bg_colors)
        size = AVATAR_SIZE
        img = Image.new("RGB", (size, size), bg)
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - w) / 2, (size - h) / 2), letter, fill="#FFFFFF", font=font)

        buf = BytesIO()
        img.save(buf, format="PNG")
        filename = f"user_{self.pk}_avatar.png"
        self.avatar.save(filename, ContentFile(buf.getvalue()), save=True)
