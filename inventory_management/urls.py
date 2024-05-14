from django.urls import path
from .views import *
from . import views

app_name = 'inventory_management'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('produtos/', ProductListView.as_view(), name='product_list'),
    path('produto/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('produto/<slug:product_slug>/unidade/<slug:slug>/', ProductUnitDetailView.as_view(), name='product_unit_detail'),
    path('escanearQR/', ScanQRView.as_view(), name='scan_qr'),
    path('sobre/', AboutView.as_view(), name='about'),
    path('enderecos/', AdressesView.as_view(), name='adresses'),
    path('enderecos/<slug:slug>/', AddressDetailView.as_view(), name='address_detail'),
    path('get_product_location/<slug:slug>', GetProductLocationView.as_view(), name='get_product_location'),
    path('generate_qr_codes', views.generate_qr_codes, name='generate_qr_codes'),
    path('area_trabalho/', WorkSpaceView.as_view(), name='workspace'),
]
