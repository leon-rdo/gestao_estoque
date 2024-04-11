import os
import tempfile
import zipfile
import qrcode
from django import forms
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

def generate_qr_code_to_pdf(data, file_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Crie um arquivo PDF usando o ReportLab
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawInlineImage(img, 100, 200)  # Altere as coordenadas conforme necessário
    c.save()

def download_qr_codes(modeladmin, request, queryset):
    temp_dir = tempfile.TemporaryDirectory()
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for product_unit in queryset:
            # Construir a URL absoluta do item
            absolute_url = request.build_absolute_uri(product_unit.get_absolute_url())
            qr_code_path = os.path.join(temp_dir.name, f"{slugify(product_unit.product.name)}_{product_unit.slug}.pdf")
            generate_qr_code_to_pdf(absolute_url, qr_code_path)
            zip_file.write(qr_code_path, os.path.basename(qr_code_path))

    temp_dir.cleanup()

    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="qr_codes.zip"'
    return response

download_qr_codes.short_description = "Baixar QR Codes"

@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    list_display = ('product', 'location', 'purchase_date')
    search_fields = ('product__name', 'location__name')
    actions = [download_qr_codes]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['quantity'].widget = forms.HiddenInput()
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('location',)
        return self.readonly_fields


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'transfer_date')
    search_fields = ('product_unit__product__name', 'origin__name', 'destination__name')
    list_filter = ('transfer_date',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('product_unit', 'origin', 'destination', 'transfer_date')
        return self.readonly_fields

    class Media:
        js = ('admin/autocomplete_origin.js',)

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
    inlines = [
        RoomInline,
    ]

    class Media:
        js = ('admin/autocomplete_address.js',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'building')
    search_fields = ('name', 'building__name')
    readonly_fields = [field.name for field in Room._meta.fields]
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request):
        return False
    
    def has_change_permission(self, request):
        return False


