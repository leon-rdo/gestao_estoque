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
from datetime import timedelta
from django.db.models import Count, Sum
import pandas as pd
from django.db.models import F, ExpressionWrapper, DecimalField
import matplotlib.pyplot as plt
import io
import base64
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import Max, Sum
from django.core.paginator import Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404

class IndexView(TemplateView):
    template_name = 'index.html'
    

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__startswith=search)
        return queryset.order_by('name')
    


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        write_off = self.request.GET.get('write_off')
        product_units = product.productunit_set.all() 
        search = self.request.GET.get('search')
        
        if search:
            product_units = product_units.filter(id__contains=search)
        
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
        context['transfer_areas'] = TransferAreas.objects.all()
        context['buildings'] = Building.objects.all()
        context['rooms'] = Room.objects.all()
        context['halls'] = Hall.objects.all()
        context['shelves'] = Shelf.objects.exclude(pk=self.get_object().location.id)
        context['consumptions'] = ClothConsumption.objects.filter(product_unit=self.get_object())
        context['write_offs'] = Write_off.objects.filter(product_unit=self.get_object())
        context['write_off_destinations'] = WriteOffDestinations.objects.all()
        
        return context
        
    def post(self, request, *args, **kwargs):
        product_unit = self.get_object()

        if 'write_off' in request.POST:
            product_unit.write_off = True
            write_off_destination_id = request.POST.get('write_off_destination')
            write_off_destination = WriteOffDestinations.objects.get(pk=write_off_destination_id)
            
            if product_unit.shelf:
                Write_off.objects.create(
                    product_unit=product_unit,
                    origin= product_unit.shelf,
                    transfer_area= TransferAreas.objects.get_or_create(name="Baixa")[0],
                    write_off_date=timezone.now(),
                    observations= "Baixa de produto",
                    write_off_destination = write_off_destination
                )
            else:
                Write_off.objects.create(
                    product_unit=product_unit,
                    origin= product_unit.location,
                    transfer_area= TransferAreas.objects.get_or_create(name="Baixa")[0],
                    write_off_date=timezone.now(),
                    observations= "Baixa de produto",
                    write_off_destination =write_off_destination
                )    
            
        elif request.POST.get('back_to_stock') == 'True':
            product_unit.write_off = False
            last_write_off = Write_off.objects.filter(product_unit=product_unit).aggregate(last_write_off_date=Max('write_off_date'))
            last_write_off_date = last_write_off.get('last_write_off_date')

            if last_write_off_date:
                last_write_off = Write_off.objects.filter(product_unit=product_unit, write_off_date=last_write_off_date).first()
                write_off_destination = last_write_off.write_off_destination if last_write_off.write_off_destination else None
            else:
                write_off_destination = None

            location_id = request.POST.get('location')
            location = TransferAreas.objects.get(pk=location_id)
            building_id = request.POST.get('building')
            room_id = request.POST.get('room')
            hall_id = request.POST.get('hall')
            shelf_id = request.POST.get('shelf')
            

            if shelf_id:
                building = Building.objects.get(pk=building_id)
                room = Room.objects.get(pk=room_id)
                hall = Hall.objects.get(pk=hall_id)
                shelf = Shelf.objects.get(pk=shelf_id)

                # Crie o objeto Write_off com os campos preenchidos
                Write_off.objects.create(
                    product_unit=product_unit,
                    origin=TransferAreas.objects.get_or_create(name="Baixa")[0],
                    recomission_transfer_area=TransferAreas.objects.get(pk=location_id),
                    recomission_building=building,
                    recomission_room=room,
                    recomission_hall=hall,
                    recomission_shelf=shelf,
                    write_off_date=timezone.now(),
                    observations="Retorno ao estoque",
                    write_off_destination=None,
                )

                # Atualize os campos da product_unit
                product_unit.location_id = location_id
                product_unit.building_id = building_id
                product_unit.room_id = room_id
                product_unit.hall_id = hall_id
                product_unit.shelf_id = shelf_id
            else:
                # Caso não haja shelf selecionada
                Write_off.objects.create(
                    product_unit=product_unit,
                    origin=TransferAreas.objects.get_or_create(name="Baixa")[0],
                    recomission_transfer_area=TransferAreas.objects.get(pk=location_id),
                    write_off_date=timezone.now(),
                    observations="Retorno ao estoque",
                    write_off_destination=None,
                )

                # Atualize apenas a localização da product_unit
                product_unit.location_id = location_id
                product_unit.building = None
                product_unit.room = None
                product_unit.hall = None
                product_unit.shelf = None
        else:
            destination_id = request.POST.get('location')
            building_id = request.POST.get('building')
            room_id = request.POST.get('room')
            hall_id = request.POST.get('hall')
            shelf_id = request.POST.get('shelf')
            observations = request.POST.get('observations')
            
            origin = product_unit.location
            destination = TransferAreas.objects.get(pk=destination_id)

            if not product_unit.shelf or not shelf_id :
                
                StockTransfer.objects.create(
                    product_unit=product_unit,
                    origin_transfer_area=origin,
                    destination_transfer_area=destination,
                    transfer_date=date.today(),
                    observations=observations,
                )
                
                product_unit.location = destination

            else:
                building = Building.objects.get(pk=building_id)
                room = Room.objects.get(pk=room_id)
                hall = Hall.objects.get(pk=hall_id)
                shelf = Shelf.objects.get(pk=shelf_id)
                
                StockTransfer.objects.create(
                    product_unit=product_unit,
                    origin_transfer_area=origin,
                    destination_transfer_area=destination,
                    transfer_date=date.today(),
                    origin_shelf=product_unit.shelf,
                    destination_building=building,
                    destination_room=room,
                    destination_hall=hall,
                    destination_shelf=shelf,
                    observations=observations,
                )

                product_unit.building = building
                product_unit.room = room
                product_unit.hall = hall
                product_unit.shelf = shelf
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


class GetProductLocationShelfView(View):
    def get(self, request, *args, **kwargs):
        product_unit_id = kwargs.get('product_unit_id')
        try:
            product_unit = ProductUnit.objects.get(id=product_unit_id)
            return JsonResponse({'location': product_unit.location_id, 'shelf': product_unit.shelf_id})
        except ProductUnit.DoesNotExist:
            return JsonResponse({}, status=404)
    
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
                    item.mark_qr_code_generated()

                
                local_now = timezone.localtime(timezone.now())
                timestamp = local_now.strftime("%d-%m-%Y_%H%M%S")

               
                unique_products = set(product_unit.product.name for product_unit in queryset)


                products_str = '_'.join(unique_products)

                filename = f"qr_codes_{products_str}_{timestamp}.pdf"

                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=letter)

                x_offset = 50
                qr_size = get_qr_size(size_preset) 
                page_width, page_height = letter
                if size_preset == 'pequeno':
                    columns = 4
                elif size_preset == 'medio':
                    columns = 3
                elif size_preset == 'grande':
                    columns = 2

                items_per_page = calculate_items_per_page(page_width, page_height, qr_size, columns)

                for idx, qr in enumerate(qr_codes):
                    row = idx // columns  
                    col = idx % columns  
                    page_idx = idx // items_per_page 
                    
                    # Coordenadas para o texto do nome da unidade de produto

                  

                    if size_preset == 'pequeno':
                        y_coordinate = page_height - 200 - (row % (items_per_page // columns)) * (qr_size + 20)
                        x_coordinate = 27 + x_offset + col * (qr_size + 20)
                        text_x_coordinate = x_coordinate + 25
                        text_y_coordinate = y_coordinate + qr_size + 10  
                    elif size_preset == 'medio':
                        y_coordinate = page_height - 200- (row % (items_per_page // columns)) * (qr_size + 20)
                        x_coordinate = 13 + x_offset + col * (qr_size + 20)
                        text_x_coordinate = x_coordinate + 50
                        text_y_coordinate = y_coordinate + qr_size + 10  
                    elif size_preset == 'grande':
                        y_coordinate = page_height - 250 - (row % (items_per_page // columns)) * (qr_size + 20)
                        x_coordinate = 50 + x_offset + col * (qr_size + 20)
                        text_x_coordinate = x_coordinate + 75
                        text_y_coordinate = y_coordinate + qr_size + 10  

                   

                    # Desenhar o nome da unidade de produto
                    c.drawString(text_x_coordinate, text_y_coordinate, item.product.name)    

                    # Se necessário, adicione aqui o código para iniciar uma nova página

                    c.drawInlineImage(qr, x_coordinate, y_coordinate, width=qr_size, height=qr_size)
                c.showPage()

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
        return 100  
    elif size_preset == 'medio':
        return 150  
    elif size_preset == 'grande':
        return 200  

@method_decorator(login_required, name='dispatch')
class WorkSpaceView(ListView):
    template_name = 'workspace.html'
    model = WorkSpace

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
        
    def post(self, request, *args, **kwargs):
        if 'clean' in request.POST:
            WorkSpace.objects.filter(user=request.user).delete()
            return HttpResponseRedirect(reverse('inventory_management:workspace'))
        
        product_id = request.POST.get('product_id')
        remove = request.POST.get('remove')

        if remove:
            try:
                product_id = request.POST.get('remove')
                WorkSpace.objects.filter(user=request.user, product_id=product_id).delete()
                return JsonResponse({'success': 'Produto removido da área de trabalho', 'reload': True}, status=200)
            except ProductUnit.DoesNotExist:
                return JsonResponse({'error': 'Produto nao encontrado'}, status=400)
            
        if product_id:
            try:
                product = ProductUnit.objects.get(pk=product_id)
                if WorkSpace.objects.filter(user=request.user, product=product).exists():
                    return JsonResponse({'error': 'Produto ja adicionado a area de trabalho', 'reload' : True}, status=400)
                else:
                    WorkSpace.objects.create(
                        user=request.user,
                        product=product
                    )
                    return JsonResponse({'success': 'Produto adicionado a area de trabalho', 'reload': True}, status=200)
            except ProductUnit.DoesNotExist:
                return JsonResponse({'error': 'Produto nao encontrado'}, status=400)
            

def get_rooms(request):
    building_id = request.GET.get('building_id')
    rooms = Room.objects.filter(building_id=building_id)
    data = [{'id': room.id, 'name': room.name} for room in rooms]
    return JsonResponse(data, safe=False)

def get_halls(request):
    room_id = request.GET.get('room_id')
    halls = Hall.objects.filter(room_id=room_id)
    data = [{'id': hall.id, 'name': hall.name} for hall in halls]
    return JsonResponse(data, safe=False)

def get_shelves(request):
    hall_id = request.GET.get('hall_id')
    shelves = Shelf.objects.filter(hall_id=hall_id)
    data = [{'id': shelf.id, 'name': shelf.name} for shelf in shelves]
    return JsonResponse(data, safe=False)

def get_write_off_status(request, product_unit_id):
    product_unit = get_object_or_404(ProductUnit, id=product_unit_id)
    return JsonResponse({'write_off': product_unit.write_off})class DashboardView(TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calcular a quantidade total de produtos no estoque ao longo do tempo
        stock_quantity_over_time = []
        today = timezone.now().date()
        for i in range(30):  # Considerar os últimos 30 dias
            date = today - timedelta(days=i)
            total_quantity = ProductUnit.objects.filter(purchase_date=date).aggregate(total_quantity=Sum('quantity'))['total_quantity']
            stock_quantity_over_time.append({'date': date, 'total_quantity': total_quantity or 0})

        product_quantity_by_category = Category.objects.annotate(total_quantity=Count('product')).values('name', 'total_quantity')
       
        stock_transfers = StockTransfer.objects.all()
        
        # Converter os dados em um DataFrame do Pandas
        df = pd.DataFrame(list(stock_transfers.values()))
        
        # Converter a coluna 'transfer_date' para o tipo datetime
        df['transfer_date'] = pd.to_datetime(df['transfer_date'])
        
        # Calcular o número de movimentos de estoque por mês, trimestre, semestre e ano
        df['year'] = df['transfer_date'].dt.strftime('%Y')
        df['quarter'] = df['transfer_date'].dt.quarter
        df['semester'] = df['transfer_date'].apply(lambda x: (x.month-1)//6 + 1)
        
        
        movements_per_month = df.groupby(df['transfer_date'].dt.strftime('%Y-%m'))['id'].count()
        movements_per_quarter = df.groupby(['year', 'quarter'])['id'].count()
        movements_per_semester = df.groupby(['year', 'semester'])['id'].count()
        movements_per_year = df.groupby('year')['id'].count()

        category_slug = self.request.GET.get('category_slug')
        product_slug = self.request.GET.get('product_slug')
        
        # Inicializar um dicionário para armazenar os valores de estoque por categoria, produto e o valor total geral
        total_stock_values = {}
        overall_value = 0
        
        # Obter todas as categorias
        categories = Category.objects.all()
        
        for category in categories:
            # Calcular o valor total para a categoria atual
            category_total = 0
            
            # Obter todos os produtos dentro da categoria atual
            products = Product.objects.filter(category=category)
            
            category_products = {}
            
            for product in products:
                # Calcular o valor total para o produto atual
                product_units = ProductUnit.objects.filter(product=product)
                product_value = sum(unit.meters * unit.product.price for unit in product_units)
                category_products[product] = product_value
                category_total += product_value
            
            # Adicionar o valor total da categoria ao dicionário total_stock_values
            total_stock_values[category] = {'total': category_total, 'products': category_products}
            
            # Adicionar o valor total da categoria ao valor geral
            overall_value += category_total
        

        write_off_products = ProductUnit.objects.filter(write_off=True)

        total_write_off_value = write_off_products.annotate(
            total_value=ExpressionWrapper(F('meters') * F('product__price'), output_field=DecimalField())
        ).aggregate(total=Sum('total_value'))['total']

        product_write_off_counts = write_off_products.values('product__name').annotate(total=Count('id')).order_by('-total')[:5]
        category_write_off_counts = write_off_products.values('product__category__name').annotate(total=Count('id')).order_by('-total')[:5]
        
        # Preparar dados para o gráfico de barras horizontais
        product_labels = [item['product__name'] for item in product_write_off_counts]
        product_counts = [item['total'] for item in product_write_off_counts]
        category_labels = [item['product__category__name'] for item in category_write_off_counts]
        category_counts = [item['total'] for item in category_write_off_counts]
        
        # Gerar gráfico de barras horizontais para produtos
        fig, ax = plt.subplots()
        ax.barh(product_labels, product_counts)
        ax.set_xlabel('Número de Baixas')
        ax.set_ylabel('Produtos')
        ax.set_title('Produtos com Mais Baixas')
        
        # Converter o gráfico em formato base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        products = Product.objects.all()

        # Calcular o total de metros para cada produto
        for product in products:
            total_meters = ProductUnit.objects.filter(product=product).aggregate(total=Sum('meters'))['total']
            product.total_meters = total_meters or 0
        
        context['products'] = products
        context['product_chart'] = chart_data
        context['product_write_off_counts'] = product_write_off_counts
        context['category_write_off_counts'] = category_write_off_counts
        context['total_write_off_value'] = total_write_off_value or 0
        context['total_stock_values'] = total_stock_values
        context['overall_value'] = overall_value
        context['movements_per_month'] = movements_per_month
        context['movements_per_quarter'] = movements_per_quarter
        context['movements_per_semester'] = movements_per_semester
        context['movements_per_year'] = movements_per_year
        context['product_quantity_by_category'] = product_quantity_by_category    
        context['stock_quantity_over_time'] = stock_quantity_over_time[::-1]
        return context