from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse
from django.views import View
from .models import *
from django.shortcuts import redirect
from datetime import date


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