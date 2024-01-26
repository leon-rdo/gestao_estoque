from django.urls import path
from .views import *

app_name = 'inventory_management'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('categorias/', CategoryListView.as_view(), name='category_list'),
    path('categorias/<slug:slug>/', CategoryItemsView.as_view(), name='category_items'),
    path('produto/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('produto/unidade/<uuid:pk>/', ProductUnitDetailView.as_view(), name='product_unit_detail')
]
