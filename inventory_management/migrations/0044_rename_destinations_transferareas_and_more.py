# Generated by Django 5.0.1 on 2024-05-15 01:38

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0043_remove_product_category_delete_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Destinations',
            new_name='TransferAreas',
        ),
        migrations.RemoveField(
            model_name='write_off',
            name='employee',
        ),
        migrations.AlterModelOptions(
            name='transferareas',
            options={'verbose_name': 'Área de Transferência', 'verbose_name_plural': 'Áreas de Transferência'},
        ),
        migrations.RemoveField(
            model_name='write_off',
            name='destination',
        ),
        migrations.AddField(
            model_name='productunit',
            name='hall',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_management.hall', verbose_name='Corredor'),
        ),
        migrations.AddField(
            model_name='productunit',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_management.room', verbose_name='Sala'),
        ),
        migrations.AddField(
            model_name='productunit',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_management.building', verbose_name='Loja'),
        ),
        migrations.AddField(
            model_name='write_off',
            name='recomission_destination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_management.shelf', verbose_name='Destino da Recomissão'),
        ),
        migrations.CreateModel(
            name='WriteOffDestinations',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Nome do Funcionário')),
                ('slug', models.SlugField(blank=True, editable=False, max_length=100, null=True, verbose_name='Slug')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Atualizado em')),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='writeoffdestinations_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('updated_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='writeoffdestinations_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Atualizado por')),
            ],
            options={
                'verbose_name': 'Destino de Baixa',
                'verbose_name_plural': 'Destinos de Baixa',
            },
        ),
        migrations.AddField(
            model_name='write_off',
            name='write_off_destination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory_management.writeoffdestinations', verbose_name='Destinatário da Baixa'),
        ),
        migrations.DeleteModel(
            name='Employee',
        ),
    ]
