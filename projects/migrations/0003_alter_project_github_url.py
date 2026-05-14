# Generated migration to make github_url required

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="github_url",
            field=models.URLField(
                validators=[django.core.validators.URLValidator()],
                verbose_name="Ссылка на GitHub",
            ),
        ),
    ]
