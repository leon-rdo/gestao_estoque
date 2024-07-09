import os
import sys
import django
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Sum, F, Count
from inventory_management.models import ProductUnit, StockTransfer, Write_off, Product, Building
from django.db.models.functions import TruncMonth
from django.db.models import ExpressionWrapper, DecimalField
import numpy as np

#Coloque o diretório do projeto no sys.path
sys.path.append('')
os.environ['DJANGO_SETTINGS_MODULE'] = 'gestao_estoque.settings'
django.setup()

def load_data(product_filter, building_filter):
    product_units = ProductUnit.objects.filter(write_off=False)
    if product_filter and product_filter != "Todos":
        product_units = product_units.filter(product__name=product_filter)

    stock_quantity_over_time = []
    today = timezone.localtime(timezone.now()).date()

    total_quantity = product_units.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    for i in range(30):
        date = today - timedelta(days=i)
        total_quantity_on_date = product_units.filter(purchase_date__lte=date).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        stock_quantity_over_time.append({'date': date, 'total_quantity': total_quantity_on_date})

    overall_value = float(product_units.aggregate(overall_value=Sum(F('weight_length') * F('product__price')))['overall_value'] or 0)

    total_write_off_value = float(product_units.filter(write_off=True).annotate(
        total_value=ExpressionWrapper(F('weight_length') * F('product__price'), output_field=DecimalField())
    ).aggregate(total=Sum('total_value'))['total'] or 0)

    write_off_data = Write_off.objects.filter(product_unit__in=product_units).annotate(
        month=TruncMonth('write_off_date')
    ).values('month').annotate(total=Count('id'))

    transfers = StockTransfer.objects.all().select_related(
        'product_unit', 'destination_building'
    ).values(
        'product_unit__product__name', 'destination_building__name'
    ).annotate(
        total=Count('id')
    )
    if building_filter and building_filter != "Todos":
        transfers = transfers.filter(destination_building__name=building_filter)

    stacked_data = {}
    for transfer in transfers:
        product_name = transfer['product_unit__product__name']
        destination_building = transfer['destination_building__name']
        if destination_building not in stacked_data:
            stacked_data[destination_building] = {}
        stacked_data[destination_building][product_name] = transfer['total']

    building_names = list(stacked_data.keys())
    product_names = list(set(item for sublist in [list(v.keys()) for v in stacked_data.values()] for item in sublist))
    product_names.sort()

    stacked_values = []
    for product_name in product_names:
        values = [stacked_data[building_name].get(product_name, 0) for building_name in building_names]
        stacked_values.append(values)

    all_transfers = StockTransfer.objects.all()

    today = timezone.localtime(timezone.now()).date()
    transfer_counts_over_time = []
    for i in range(30):
        date = today - timedelta(days=i)
        count_on_date = all_transfers.filter(transfer_date__date=date).count()
        transfer_counts_over_time.append({'date': date, 'count': count_on_date})

    total_quantities = ProductUnit.get_total_quantity()
    return {
        'total_meters': float(total_quantities['total_meters']),
        'total_kilograms': float(total_quantities['total_kilograms']),
        'stock_quantity_over_time': stock_quantity_over_time[::-1],
        'write_off_data': write_off_data,
        'products': Product.objects.all(),
        'buildings': Building.objects.all(),
        'total_write_off_value': total_write_off_value,
        'write_off_products_number': product_units.filter(write_off=True).count(),
        'overall_value': overall_value,
        'all_transfers': all_transfers,
        'transfer_counts_over_time': transfer_counts_over_time,
        'stacked_chart_data': {
            'product_names': product_names,
            'building_names': building_names,
            'stacked_values': np.array(stacked_values)
        },
    }

def main():
    st.title("Dashboard")
    context = load_data(None, None)  

    st.sidebar.header("Filtros")
    product_filter = st.sidebar.selectbox("Filtrar por Produto:", ["Todos"] + [product.name for product in context['products']])
    building_filter = st.sidebar.selectbox("Filtrar por Depósito:", ["Todos"] + [building.name for building in context['buildings']])
    if st.sidebar.button("Filtrar"):
        context = load_data(product_filter, building_filter)

    tabs = st.tabs(["Estoque", "Baixas", "Movimentos de Estoque"])

    with tabs[0]:
        st.header("Quantidade Total de Metros e Quilos")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Metros", f"{context['total_meters']}m")
        with col2:
            st.metric("Total de Quilos", f"{context['total_kilograms']}kg")

        st.header("Valor Total de Produtos em Estoque")
        st.metric("Valor Total", f"R$ {context['overall_value']}")

        st.header("Quantidade Total de Produtos no Estoque ao Longo do Tempo")
        stock_data = pd.DataFrame(context['stock_quantity_over_time'])
        st.line_chart(stock_data.set_index('date'))

    with tabs[1]:
        st.header("Quantidade de Produtos Baixados")
        st.metric("Quantidade", f"{context['write_off_products_number']} unidades")
        
        st.header("Valor Total de Produtos Baixados")
        st.metric("Valor Total", f"R$ {context['total_write_off_value']}")

    with tabs[2]:
        st.header("Transferências realizadas")
        st.metric("Total de Transferências", f"{context['all_transfers'].count()}")

        st.header("Quantidade de Transferências de Estoque ao Longo do Tempo")
        transfer_counts_data = pd.DataFrame(context['transfer_counts_over_time'])
        if not transfer_counts_data.empty:
            transfer_counts_data.set_index('date', inplace=True)
            st.line_chart(transfer_counts_data)

        st.header("Movimentos de Estoque por Depósito e Produto")

        stacked_chart_data = context['stacked_chart_data']
        building_names = stacked_chart_data['building_names']
        product_names = stacked_chart_data['product_names']
        stacked_values = stacked_chart_data['stacked_values']

        fig, ax = plt.subplots(figsize=(10, 8))

        ax.bar(building_names, stacked_values[0, :], label=product_names[0])
        for i in range(1, len(product_names)):
            ax.bar(building_names, stacked_values[i, :], bottom=np.sum(stacked_values[:i, :], axis=0), label=product_names[i])

        ax.set_ylabel('Quantidade de Movimentação')
        ax.set_xlabel('Depósito')
        ax.set_title('Movimentos de Estoque por Depósito e Produto')
        ax.legend()

        plt.xticks(rotation=45, ha='right')

        st.pyplot(fig)

if __name__ == "__main__":
    main()
