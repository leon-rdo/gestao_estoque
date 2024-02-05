from django.urls import path
from .views import *

app_name = 'inventory_management'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('categorias/', CategoryListView.as_view(), name='category_list'),
    path('categorias/<slug:slug>/', CategoryItemsView.as_view(), name='category_items'),
    path('categorias/<slug:category_slug>/produto/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('categorias/<slug:category_slug>/produto/<slug:product_slug>/unidade/<slug:slug>/', ProductUnitDetailView.as_view(), name='product_unit_detail'),
    path('escanearQR/', ScanQRView.as_view(), name='scan_qr'),
    path('get_product_location/<slug:slug>', GetProductLocationView.as_view(), name='get_product_location'),
]
