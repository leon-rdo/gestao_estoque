from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.urls import path

from django.shortcuts import redirect
#

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
    list_display = ('name', 'category', 'quantity', 'custom_display')
    search_fields = ('name',)
    list_filter = ('category',)
    
    def custom_display(self, obj):
        if "liso" in obj.name.lower():
            return obj.color
        elif "estampado" in obj.name.lower():
            return obj.pattern 
        else:
            return "N/A"
    custom_display.short_description = "Liso/Estampado" 
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj and form.base_fields.get('color'):
            form.base_fields['color'].widget = forms.HiddenInput()
        elif not obj and form.base_fields.get('pattern'):
            form.base_fields['pattern'].widget = forms.HiddenInput()
        return form

def download_qr_codes(modeladmin, request, queryset):
    item_ids = ','.join(str(item.id) for item in queryset)
    url = reverse('inventory_management:generate_qr_codes') + f'?selected_items={item_ids}'
    return redirect(url)
    

download_qr_codes.short_description = "Baixar QR Codes"


def write_off_products(modeladmin, request, queryset):
    for product_unit in queryset:
        if not product_unit.write_off:
            product_unit.write_off = True
            product_unit.save()
write_off_products.short_description = "Dar baixa em produtos selecionados"

def write_on_products(modeladmin, request, queryset):
    for product_unit in queryset:
        if product_unit.write_off:
            product_unit.write_off = False
            product_unit.save()
write_on_products.short_description = "Retornar ao estoque os produtos selecionados"

class ClothConsumptionInline(admin.TabularInline):
    model = ClothConsumption
    readonly_fields = ('weight_length_before','weight_length_after',)
    extra = 1

@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    list_display = ('product', 'location', 'weight_length_with_measure', 'purchase_date', 'write_off')
    search_fields = ('product__name', 'location__name', 'id', 'code')
    list_filter = ('product' ,'purchase_date', 'location', 'write_off')
    actions = [download_qr_codes, write_off_products, write_on_products]
    inlines = [ClothConsumptionInline]

    
    def  weight_length_with_measure(self, obj):
        product_measure = obj.product.get_measure_display()
        return f"{obj. weight_length} {product_measure}"
    weight_length_with_measure.short_description = 'Tamanho / Peso'
    

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['quantity'].widget = forms.HiddenInput()
            form.base_fields['weight_length'].disabled = True
        else:
            pass
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('location',)
        return self.readonly_fields

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('customize_qr_codes/', self.customize_qr_codes),
        ]
        return my_urls + urls

    def customize_qr_codes(self, request):
        return download_qr_codes(self, request, None)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_custom_qr_button'] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_custom_qr_button'] = True
        return super().add_view(request, form_url, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_custom_qr_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

    def get_inline_instances(self, request, obj=None):
        if obj:
            return [inline(self.model, self.admin_site) for inline in self.inlines]
        else:
            return []

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'transfer_date')
    search_fields = ('product_unit__product__name', 'origin__name', 'destination__name')
    list_filter = ('transfer_date', 'origin', 'destination')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('product_unit', 'origin', 'destination', 'transfer_date')
        return self.readonly_fields

    class Media:
        js = ('admin/autocomplete_origin.js',)

@admin.register(Write_off)
class WriteOffAdmin(admin.ModelAdmin):
    list_display = ('product_unit', 'write_off_date')
    search_fields = ('product_unit__product__name', 'product_unit__location__name')
    list_filter = ('write_off_date',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('product_unit', 'write_off_date')
        return self.readonly_fields

class RoomInline(admin.StackedInline):
    model = Room
    
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1 

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'cep', 'street', 'number', 'complement', 'neighborhood', 'city', 'state')
    search_fields = ('name', 'cep', 'street', 'number', 'complement', 'neighborhood', 'city', 'state')
    list_filter = ('street', 'neighborhood', 'city')
    inlines = [
        RoomInline,
    ]
    
    class Media:
        js = ('admin/autocomplete_address.js',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    
    def change_view(self, request, object_id):
        room = self.get_object(request, object_id)
        building_id = room.building.id
        building_change_url = reverse('admin:inventory_management_building_change', args=[building_id])
        return HttpResponseRedirect(building_change_url)
    
    def has_view_permission(self, request):
        return False
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request):
        return False

@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    pass

@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    pass

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    pass

@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    pass