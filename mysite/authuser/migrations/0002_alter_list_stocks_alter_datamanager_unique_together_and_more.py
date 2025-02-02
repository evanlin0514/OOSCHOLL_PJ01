# Generated by Django 5.0.7 on 2024-08-30 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authuser", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="list",
            name="stocks",
            field=models.ManyToManyField(
                related_name="watchlists",
                through="authuser.DataManager",
                to="authuser.stock",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="datamanager", unique_together={("list", "stock")},
        ),
        migrations.AlterUniqueTogether(
            name="list", unique_together={("user", "name")},
        ),
    ]
