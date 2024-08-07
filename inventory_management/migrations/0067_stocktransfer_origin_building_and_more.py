# Generated by Django 5.0.1 on 2024-06-24 06:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0066_rooms_alter_productunit_room_alter_shelf_room_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocktransfer',
            name='origin_building',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stocktransfer_origin_building', to='inventory_management.building', verbose_name='Depósito de Origem'),
        ),
        migrations.AddField(
            model_name='stocktransfer',
            name='origin_hall',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stocktransfer_origin_hall', to='inventory_management.hall', verbose_name='Corredor de Origem'),
        ),
        migrations.AddField(
            model_name='stocktransfer',
            name='origin_room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stocktransfer_origin_room', to='inventory_management.rooms', verbose_name='Sala de Origem'),
        ),
    ]
