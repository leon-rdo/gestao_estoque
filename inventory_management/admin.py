from django.contrib import admin

from .models import *


admin.site.site_header = 'Gestão de Estoque'
admin.site.site_title = 'Administração'
admin.site.index_title = 'Gestão de Estoque'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity')
    search_fields = ('name',)


@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    list_display = ('product', 'location', 'purchase_date')
    search_fields = ('product__name', 'location__name')


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'cep', 'street', 'number', 'complement', 'neighborhood', 'city', 'state')
    search_fields = ('name', 'cep', 'street', 'number', 'complement', 'neighborhood', 'city', 'state')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'building')
    search_fields = ('name', 'building__name')
