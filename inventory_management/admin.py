from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.urls import path
from django.shortcuts import redirect
from django.utils.safestring import mark_safe

import base64
from io import BytesIO
import qrcode
from django.contrib import admin
from .models import *

admin.site.site_header = 'Gestão de Estoque'
admin.site.site_title = 'Administração'
admin.site.index_title = 'Gestão de Estoque'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'custom_display', 'created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('name',)
    
    def custom_display(self, obj):
        if "liso" in obj.name.lower():
            return obj.color
        elif "estampado" in obj.name.lower():
            return obj.pattern 
        else:
            return "N/A"
    custom_display.short_description = "Liso/Estampado" 
    
    def save_model(self, request, obj, form, change):
        if not change:  
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


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
    readonly_fields = ('remainder','weight_length_before')
    extra = 1

class StockTransferInline(admin.TabularInline):
    model = StockTransfer
    readonly_fields = ('origin_transfer_area','origin_shelf','destination_transfer_area', 'destination_shelf', 'transfer_date', 'observations')
    extra = 0

    
@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    list_display = ('product', 'location','shelf_or_none','weight_length_with_measure', 'write_off' ,'purchase_date', "created_by", "created_at", "updated_by", "updated_at")
    search_fields = ('product__name', 'location__name', 'id')
    list_filter = ('product' ,'purchase_date', 'location', 'write_off')
    fields = ['product', 'location', 'building', 'room', 'hall', 'shelf', 'purchase_date', 'quantity', 'weight_length', 'imcoming', 'write_off']
    actions = [download_qr_codes, write_off_products, write_on_products]
    inlines = [ClothConsumptionInline, StockTransferInline]

    class Media:
        js = (
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'admin/product_unit_admin.js',
        )

    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            fieldsets.append(('QR Code', {'fields': ('qr_code_image',)}))
        return fieldsets
    
    def shelf_or_none(self, obj):
        if obj.shelf:
            return obj.shelf
        return "N/A"
    shelf_or_none.short_description = 'Prateleira'

    def weight_length_with_measure(self, obj):
        product_measure = obj.product.get_measure_display()
        return f"{obj.weight_length} {product_measure}"
    weight_length_with_measure.short_description = 'Tamanho / Peso'

    def qr_code_image(self, obj):
        if obj:
            absolute_url = f"http://localhost:8000{obj.get_absolute_url()}"
            qr = qrcode.make(absolute_url)
            qr_io = BytesIO()
            qr.save(qr_io, format='PNG')
            qr_io.seek(0)
            qr_base64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')
            return mark_safe(f'<img src="data:image/png;base64,{qr_base64}" width="250" height="250"/>')
        return "No QR code available"
    qr_code_image.short_description = 'QR Code'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['quantity'].widget = forms.HiddenInput()
            form.base_fields['weight_length'].disabled = True
        else:
            pass
        return form
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "location":
            kwargs["queryset"] = TransferAreas.objects.exclude(name = "Baixa")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('location', 'qr_code_image', 'building', 'room', 'hall', 'shelf', 'purchase_date',)
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
        
    def save_model(self, request, obj, form, change):
        if not change:  
            obj.created_by = request.user
        obj.updated_by = request.user
        
        super().save_model(request, obj, form, change)

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'transfer_date', 'created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('product_unit__product__name', 'origin__name', 'destination__name')
    list_filter = ('transfer_date', 'origin_shelf', 'destination_shelf')
    fields = ['product_unit', 'origin_transfer_area', 'origin_shelf', 'destination_transfer_area','destination_building', 'destination_room', 'destination_hall', 'destination_shelf', 'transfer_date', 'observations']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('product_unit', 'origin_transfer_area', 'origin_shelf','destination_transfer_area', 'destination_shelf', 'transfer_date')
        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "location":
            kwargs["queryset"] = TransferAreas.objects.exclude(name = "Baixa")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    class Media:
        js = ('admin/autocomplete_origin.js',)

    def save_model(self, request, obj, form, change):
        if not change:  
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Write_off)
class WriteOffAdmin(admin.ModelAdmin):
    list_display = ('product_unit', 'write_off_date', 'write_off_destination', 'created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('product_unit__product__name', 'product_unit__location__name')
    list_filter = ('write_off_date',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('product_unit', 'write_off_date')
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        if not change:  
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

class RoomInline(admin.StackedInline):
    model = Room
    
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1 

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'cep', 'street', 'number', 'complement', 'neighborhood', 'city', 'state', 'created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('name', 'cep', 'street', 'number', 'complement', 'neighborhood', 'city', 'state')
    list_filter = ('street', 'neighborhood', 'city')
    inlines = [
        RoomInline,
    ]
    
    class Media:
        js = ('admin/autocomplete_address.js',)

    def save_model(self, request, obj, form, change):
        if not change:  
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

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

@admin.register(WriteOffDestinations)
class WriteOffDestinationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TransferAreas)
class TransferAreasAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
        
@admin.register(WorkSpace)
class WorkSpaceAdmin(admin.ModelAdmin):
    pass

