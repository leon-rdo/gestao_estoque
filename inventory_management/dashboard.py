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
from inventory_management.models import ProductUnit, StockTransfer, Write_off, Product
from django.db.models.functions import TruncMonth
from django.db.models import ExpressionWrapper, DecimalField

sys.path.append('/home/erick/vscode/veloz/gestao_estoque')
os.environ['DJANGO_SETTINGS_MODULE'] = 'gestao_estoque.settings'
django.setup()

def load_data():
    product_id = st.sidebar.text_input("Product ID", "")

    product_units = ProductUnit.objects.all()
    if product_id:
        product_units = product_units.filter(product_id=product_id)

    stock_quantity_over_time = []
    today = timezone.localtime(timezone.now()).date()  # Obter a data local atual

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

    product_movements = []
    first_day_of_current_month = datetime(today.year, today.month, 1).date()  # Primeiro dia do mês atual

    for product_unit in product_units:
        movements = StockTransfer.objects.filter(product_unit=product_unit, transfer_date__gte=first_day_of_current_month).order_by('transfer_date')
        if movements.exists():
            dates = [movement.transfer_date.date() for movement in movements]  # Apenas a parte da data sem o horário
            quantities = [movement.product_unit.quantity for movement in movements]
            product_movements.append({
                'product_name': product_unit.product.name,
                'dates': dates,
                'quantities': quantities
            })

    total_quantities = ProductUnit.get_total_quantity()
    return {
        'total_meters': float(total_quantities['total_meters']),
        'total_kilograms': float(total_quantities['total_kilograms']),
        'stock_quantity_over_time': stock_quantity_over_time[::-1],
        'write_off_data': write_off_data,
        'products': Product.objects.all(),
        'product_movements': product_movements,
        'total_write_off_value': total_write_off_value,
        'write_off_products_number': product_units.filter(write_off=True).count(),
        'overall_value': overall_value,
    }

def main():
    st.title("Dashboard")
    context = load_data()

    st.sidebar.header("Filter")
    product_filter = st.sidebar.selectbox("Filter by Product:", ["Todos"] + [product.name for product in context['products']])
    st.sidebar.button("Filtrar")

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
        st.header("Movimentos de Estoque por Produto")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for product_movement in context['product_movements']:
            dates = product_movement['dates']
            quantities = product_movement['quantities']
            
            # Converter as datas para matplotlib date format
            dates = [mdates.date2num(date) for date in dates]
            
            ax.plot_date(dates, quantities, linestyle='-', marker=None, label=product_movement['product_name'])

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))  # Formato da data no eixo X
        ax.set_xlabel('Data da Transferência')
        ax.set_ylabel('Quantidade')
        ax.set_title('Movimentos de Estoque por Produto')
        ax.legend(loc='upper left')
        plt.xticks(rotation=45)
        st.pyplot(fig)

if __name__ == "__main__":
    main()
