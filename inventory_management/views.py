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
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import Max, Sum
from django.core.paginator import Paginator, PageNotAnInteger


class IndexView(TemplateView):
    template_name = 'index.html'


class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = super().get_queryset()
        filtro = self.request.GET.get('search')

        if filtro:
            queryset = queryset.filter(name__icontains=filtro)
            
        return queryset


class CategoryItemsView(ListView):
    model = Product
    template_name = 'category_items.html'
    paginate_by = 6
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        filtro = self.request.GET.get('search')
        category = Category.objects.get(slug=self.kwargs['slug'])

        if filtro:
            queryset = queryset.filter(name__icontains=filtro, category=category)
        else:
            queryset = queryset.filter(category=category)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(slug=self.kwargs['slug'])
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
        write_off = self.request.GET.get('write_off')
        product_units = product.productunit_set.all() 
        
        if write_off == 'baixados':
            product_units = product_units.filter(write_off=True)
        elif write_off == 'todos':
            pass 
        else:
            product_units = product_units.filter(write_off=False)
        
        paginator = Paginator(product_units, 8)
        page = self.request.GET.get('page')
        try:
            product_units_page = paginator.page(page)
        except PageNotAnInteger:
            product_units_page = paginator.page(1)
        
        total_meters = product_units.aggregate(total_meters=Sum('weight_length'))['total_meters']
        context['total_meters'] = total_meters if total_meters else 0
        context['product_units'] = product_units_page 
        context['page_obj'] = product_units_page 
        
        return context

class ProductUnitDetailView(DetailView):
    model = ProductUnit
    template_name = 'product_unit_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transfer_areas'] = Destinations.objects.all()
        context['shelves'] = Shelf.objects.exclude(pk=self.get_object().location.id)
        context['consumptions'] = ClothConsumption.objects.filter(product_unit=self.get_object())
        context['write_offs'] = Write_off.objects.filter(product_unit=self.get_object())
        context['employees'] = Employee.objects.all()
        
        return context
        
    def post(self, request, *args, **kwargs):
        product_unit = self.get_object()

        if 'write_off' in request.POST:
            product_unit.write_off = True
            employee_id = request.POST.get('employee')
            employee = Employee.objects.get(pk=employee_id)
            
            if product_unit.shelf:
                Write_off.objects.create(
                    product_unit=product_unit,
                    origin= product_unit.shelf,
                    transfer_area= Destinations.objects.get_or_create(name="Baixa")[0],
                    write_off_date=timezone.now(),
                    observations= "Baixa de produto",
                    employee = employee
                )
            else:
                Write_off.objects.create(
                    product_unit=product_unit,
                    origin= product_unit.location,
                    transfer_area= Destinations.objects.get_or_create(name="Baixa")[0],
                    write_off_date=timezone.now(),
                    observations= "Baixa de produto",
                    employee = employee
                )    
            
        elif request.POST.get('back_to_stock') == 'True':
            product_unit.write_off = False
            last_write_off = Write_off.objects.filter(product_unit=product_unit).aggregate(last_write_off_date=Max('write_off_date'))
            last_write_off_date = last_write_off.get('last_write_off_date')

            if last_write_off_date:
                last_write_off = Write_off.objects.filter(product_unit=product_unit, write_off_date=last_write_off_date).first()
                employee = last_write_off.employee if last_write_off.employee else None
            else:
                employee = None

            location_id = request.POST.get('location')
            location = Destinations.objects.get(pk=location_id)
            shelf_id = request.POST.get('shelf')

            if shelf_id != None:
                shelf = Shelf.objects.get(pk=shelf_id)

            
                Write_off.objects.create(
                        product_unit=product_unit,
                        origin=Destinations.objects.get_or_create(name="Baixa")[0],
                        transfer_area=location,
                        destination=shelf,
                        write_off_date=timezone.now(),
                        observations="Retorno ao estoque",
                        employee=employee, 
                )
                product_unit.location = location
                product_unit.shelf = shelf
            else:
                Write_off.objects.create(
                    product_unit=product_unit,
                    origin=Destinations.objects.get_or_create(name="Baixa")[0],
                    transfer_area=location,
                    write_off_date=timezone.now(),
                    observations="Retorno ao estoque",
                    employee=employee, 
                )
                product_unit.location = location
                product_unit.shelf = None
        else:
            destination_id = request.POST.get('destination')
            observations = request.POST.get('observations')
            
            origin = product_unit.location
            destination = Shelf.objects.get(pk=destination_id)
            
            StockTransfer.objects.create(
                product_unit=product_unit,
                origin=origin,
                destination=destination,
                transfer_date=date.today(),
                observations=observations
            )
            
            product_unit.location = destination

        consumption = request.POST.get('remainder')
        if consumption:
                consumption_decimal = Decimal(consumption)

                if consumption_decimal > product_unit.weight_length:
                    return JsonResponse({'remainder': "O consumo não pode ser maior que o peso/tamanho antes da subtração."}, status=400)
                
                remainder = consumption_decimal
                if remainder < 0:
                    return JsonResponse({'remainder': "O peso/tamanho depois da subtração não pode ser negativo."}, status=400)
                
                try:
                    ClothConsumption.objects.create(
                        product_unit=product_unit,
                        weight_length_before=product_unit.weight_length,
                        remainder= consumption_decimal
                    )
                except ValidationError as e:
                    return JsonResponse({'remainder': e.message}, status=400)


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
    
def calculate_items_per_page(page_width, page_height, qr_size, columns):
    available_width = page_width - 100 
    available_height = page_height - 100  

    max_columns = columns
    max_rows = available_height // (qr_size + 20)
    items_per_page = max_rows * max_columns

    return items_per_page

def generate_qr_codes(request):
    host = request.get_host()
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
                    data = f"http://{host}{item.get_absolute_url()}"
                    qr = qrcode.make(data, box_size=get_qr_size(size_preset))
                    qr_codes.append(qr)

                # Gerar PDF com os códigos QR
                local_now = timezone.localtime(timezone.now())
                timestamp = local_now.strftime("%d-%m-%Y_%H%M%S")

                # Obtém os nomes dos produtos
                unique_products = set(product_unit.product.name for product_unit in queryset)

# Formata os nomes dos produtos para incluí-los no nome do arquivo
                products_str = '_'.join(unique_products)

                # Concatena o carimbo de data e hora e os nomes dos produtos ao nome do arquivo
                filename = f"qr_codes_{products_str}_{timestamp}.pdf"

                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=letter)

                x_offset = 50
                qr_size = get_qr_size(size_preset)  # Tamanho do código QR em pixels
                page_width, page_height = letter
                if size_preset == 'pequeno':
                    columns = 4
                elif size_preset == 'medio':
                    columns = 3
                elif size_preset == 'grande':
                    columns = 2

                items_per_page = calculate_items_per_page(page_width, page_height, qr_size, columns)

                for idx, qr in enumerate(qr_codes):
                    row = idx // columns  # Linha dentro da página
                    col = idx % columns  # Coluna dentro da página
                    page_idx = idx // items_per_page  # Índice da página atual
                   
                    if size_preset == 'pequeno':
                        y_coordinate = page_height - 200 - (row % (items_per_page // columns)) * (qr_size + 20)
                        x_coordinate = 27 + x_offset + col * (qr_size + 20)
                    elif size_preset == 'medio':
                        y_coordinate = page_height - 200- (row % (items_per_page // columns)) * (qr_size + 20)
                        x_coordinate = 13 + x_offset + col * (qr_size + 20)
                    elif size_preset == 'grande':
                        y_coordinate = page_height - 250 - (row % (items_per_page // columns)) * (qr_size + 20)
                        x_coordinate = 50 + x_offset + col * (qr_size + 20)

                    # Verificar se é necessário iniciar uma nova página
                    if idx > 0 and idx % items_per_page == 0:
                        c.showPage()

                    c.drawInlineImage(qr, x_coordinate, y_coordinate, width=qr_size, height=qr_size)

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
        return 100  # Ajuste o valor conforme necessário
    elif size_preset == 'medio':
        return 150  # Ajuste o valor conforme necessário
    elif size_preset == 'grande':
        return 200  # Ajuste o valor conforme necessário

