import random
from io import BytesIO

from django.core.files.base import ContentFile
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from PIL import Image, ImageDraw, ImageFont

from .constants import AVATAR_BG_COLORS
from .models import User
from .utils import AVATAR_SIZE


def generate_avatar(user: User) -> None:
    """Генерирует аватар для пользователя на основе первой буквы имени."""
    letter = (user.first_name or "?").strip()[:1].upper() or "?"
    bg_color = random.choice(AVATAR_BG_COLORS)

    size = AVATAR_SIZE
    img = Image.new("RGB", (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - w) / 2, (size - h) / 2),
        letter,
        fill="#FFFFFF",
        font=font,
    )

    buf = BytesIO()
    img.save(buf, format="PNG")
    filename = f"user_{user.pk}_avatar.png"
    user.avatar.save(filename, ContentFile(buf.getvalue()), save=False)


@receiver(post_save, sender=User)
def create_avatar_for_new_user(sender, instance, created, **kwargs):
    """Создаёт аватар при создании пользователя, если он не был загружен."""
    if created and not instance.avatar:
        generate_avatar(instance)
        instance.save(update_fields=["avatar"])


@receiver(pre_save, sender=User)
def delete_old_avatar_on_update(sender, instance, **kwargs):
    """Удаляет старый файл аватара при его замене."""
    if not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_avatar = old_instance.avatar
    new_avatar = instance.avatar
    if old_avatar and old_avatar != new_avatar:
        old_avatar.delete(save=False)