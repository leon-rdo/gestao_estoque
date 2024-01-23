from django.urls import path
from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path(),
    path('produto/<uuid:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('produto/unidade/<uuid:pk>/', ProductUnitDetailView.as_view(), name='product_unit_detail')
]
