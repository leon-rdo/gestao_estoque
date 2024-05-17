# Generated by Django 5.0.1 on 2024-05-03 05:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0026_remove_productunit_returned_write_off'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='write_off',
            options={},
        ),
        migrations.AddField(
            model_name='write_off',
            name='employee',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Funcionário'),
            preserve_default=False,
        ),
    ]