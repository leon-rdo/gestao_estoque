from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse
from django.views import View
from .models import *
from django.shortcuts import redirect
from datetime import date
from .forms import QRCodeForm
from django.http import HttpResponse
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.shortcuts import render
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Image, Spacer
from reportlab.lib.units import inch
import os
import tempfile


class IndexView(TemplateView):
    template_name = 'index.html'


class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'


class CategoryItemsView(ListView):
    model = Product
    template_name = 'category_items.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(slug=self.kwargs['slug'])
        context['products'] = Product.objects.filter(category=context['category'])
        return context


class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        if self.request.GET.get('write_off') == 'true':
            context['product_units'] = product.productunit_set.filter(write_off=True)
        elif self.request.GET.get('write_off') == 'todos':
            context['product_units'] = product.productunit_set.all()
        else:
            context['product_units'] = product.productunit_set.filter(write_off=False)
        return context

class ProductUnitDetailView(DetailView):
    model = ProductUnit
    template_name = 'product_unit_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = Room.objects.all()
        context['rooms'] = room.exclude(pk=self.get_object().location.id)
        return context
        
        
    def post(self, request, *args, **kwargs):
        destination_id = request.POST.get('destination')
        observations = request.POST.get('observations')
        
        origin_id = self.get_object().location.id
        product_unit = self.get_object()

        origin = Room.objects.get(pk=origin_id)
        destination = Room.objects.get(pk=destination_id)

        transfer = StockTransfer.objects.create(
            product_unit=product_unit,
            origin=origin,
            destination=destination,
            transfer_date=date.today(),
            observations=observations
        )
        
        product_unit.location = destination
        product_unit.save()

        return redirect(product_unit.get_absolute_url())
    
class ScanQRView(TemplateView):
    template_name = 'scan_qr.html'


class AboutView(TemplateView):
    template_name = 'about.html'


class AdressesView(ListView):
    model = Building
    template_name = 'adresses.html'
    context_object_name = 'adresses'


class AddressDetailView(DetailView):
    model = Building
    template_name = 'address.html'


class GetProductLocationView(View):
    def get(self, request, *args, **kwargs):
        product_unit = ProductUnit.objects.get(slug=self.kwargs.get('slug'))
        return JsonResponse({'location': str(product_unit.location.slug)})
    
def calculate_items_per_page(page_width, page_height, qr_size):
    available_width = page_width - 100  # Ajuste conforme necessário
    available_height = page_height - 200  # Ajuste conforme necessário

    max_rows = available_height // (qr_size + 20)
    max_columns = available_width // (qr_size + 20)

    return max_rows * max_columns
# views.py
def generate_qr_codes(request):
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            selected_items = request.GET.get('selected_items')
            size_preset = form.cleaned_data['size_preset']
            
            if selected_items and size_preset:
                selected_item_ids = selected_items.split(',')
                queryset = ProductUnit.objects.filter(id__in=selected_item_ids)

                qr_codes = []
                for item in queryset:
                    data = f"Tamanho: {size_preset}, Item: {item.id}"
                    qr = qrcode.make(data, box_size=get_qr_size(size_preset))
                    qr_codes.append(qr)

                # Gerar PDF com os códigos QR
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="qr_codes.pdf"'
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=letter)


                x_offset = 50
                qr_size = get_qr_size(size_preset)  # Tamanho do código QR em pixels
                page_width, page_height = letter
                items_per_page = calculate_items_per_page(page_width, page_height, qr_size)

                for idx, qr in enumerate(qr_codes):
                    row = idx // 3  # Linha dentro da página
                    col = idx % 3  # Coluna dentro da página
                    page_idx = idx // items_per_page  # Índice da página atual
                    y_coordinate = page_height - 150 - (row % (items_per_page // 3)) * (qr_size + 20)
                    x_coordinate = x_offset + col * (qr_size + 20)
                    if page_idx > 0:
                        # Ajustar y_coordinate para a segunda página em diante
                        y_coordinate -= (page_idx * (page_height - 650))

                    c.drawInlineImage(qr, x_coordinate, y_coordinate, width=qr_size, height=qr_size)

                    if (idx + 1) % items_per_page == 0 and idx != 0:
                        # Iniciar nova página após renderizar todos os QR codes da página atual
                        c.showPage()

                c.showPage()  # Garantir que a última página seja exibida

                c.save()
                pdf_data = buffer.getvalue()
                buffer.close()
                response.write(pdf_data)

                return response
    else:
        form = QRCodeForm()
    return render(request, 'admin/inventory_management/productunit/generate_qr_codes.html', {'form': form})

def get_qr_size(size_preset):
    if size_preset == 'pequeno':
        return 50  # Ajuste o valor conforme necessário
    elif size_preset == 'medio':
        return 70  # Ajuste o valor conforme necessário
    elif size_preset == 'grande':
        return 150  # Ajuste o valor conforme necessário

