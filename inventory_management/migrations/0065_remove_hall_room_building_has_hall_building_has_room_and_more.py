# Generated by Django 5.0.1 on 2024-06-18 06:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0064_alter_productunit_write_off'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hall',
            name='room',
        ),
        migrations.AddField(
            model_name='building',
            name='has_hall',
            field=models.BooleanField(default=False, verbose_name='Possui Corredor?'),
        ),
        migrations.AddField(
            model_name='building',
            name='has_room',
            field=models.BooleanField(default=False, verbose_name='Possui Sala?'),
        ),
        migrations.AddField(
            model_name='building',
            name='has_shelf',
            field=models.BooleanField(default=False, verbose_name='Possui Gaveta?'),
        ),
        migrations.AddField(
            model_name='hall',
            name='building',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='inventory_management.building', verbose_name='Prédio'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room',
            name='hall',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_management.hall', verbose_name='Corredor'),
        ),
        migrations.AddField(
            model_name='shelf',
            name='building',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='inventory_management.building', verbose_name='Depósito'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shelf',
            name='room',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='inventory_management.room', verbose_name='Sala'),
            preserve_default=False,
        ),
    ]
