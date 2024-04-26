# Generated by Django 5.0.1 on 2024-04-26 20:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory_management", "0017_productunit_meters_productunit_ncm"),
    ]

    operations = [
        migrations.AddField(
            model_name="productunit",
            name="color",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Cor"
            ),
        ),
        migrations.AddField(
            model_name="productunit",
            name="pattern",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Estampa"
            ),
        ),
        migrations.AddField(
            model_name="productunit",
            name="type",
            field=models.CharField(
                choices=[
                    ("none", "Nenhum"),
                    ("liso", "Liso"),
                    ("estampado", "Estampado"),
                ],
                default="none",
                max_length=10,
                verbose_name="Tipo",
            ),
        ),
    ]