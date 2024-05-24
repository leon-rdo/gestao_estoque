from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_transfer_area(sender, **kwargs):
    from .models import TransferAreas
    TransferAreas.objects.get_or_create(name='Loja')
    TransferAreas.objects.get_or_create(name='Depósito')
    TransferAreas.objects.get_or_create(name='Baixa')

class InventoryManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory_management'
    verbose_name = 'Gestão de Estoque'

    def ready(self):
        post_migrate.connect(create_transfer_area, sender=self)