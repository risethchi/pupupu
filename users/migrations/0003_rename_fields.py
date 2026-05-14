# Generated migration to rename name -> first_name and surname -> last_name

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_user_phone"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="name",
            new_name="first_name",
        ),
        migrations.RenameField(
            model_name="user",
            old_name="surname",
            new_name="last_name",
        ),
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(max_length=124, verbose_name="Имя"),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(max_length=124, verbose_name="Фамилия"),
        ),
    ]
