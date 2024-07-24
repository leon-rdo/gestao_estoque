# Generated by Django 5.0.1 on 2024-04-24 18:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory_management", "0014_remove_room_shelf_hall_shelf"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hall",
            name="shelf",
        ),
        migrations.RemoveField(
            model_name="room",
            name="hall",
        ),
        migrations.AddField(
            model_name="hall",
            name="room",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="inventory_management.room",
                verbose_name="Sala",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="shelf",
            name="hall",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="inventory_management.hall",
                verbose_name="Corredor",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="productunit",
            name="location",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="inventory_management.shelf",
                verbose_name="Localização",
            ),
        ),
    ]
