import os
import pandas as pd
from django.views.generic import TemplateView
from django.conf import settings
from operations.models import Operation
from decimal import Decimal
from django.shortcuts import render, redirect
from .utils import get_collection_handle
from datetime import datetime
from bson.objectid import ObjectId
from .ml_forecast import create_forecast_graph

class OperationListView(TemplateView):
    model = Operation
    template_name = 'operation_list.html'
    context_object_name = 'operations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = self.request.GET.get('year') or '2023'
        month_param = self.request.GET.get('month') or '01'

        month_names = {
            '01': 'Січень', '02': 'Лютий', '03': 'Березень', '04': 'Квітень',
            '05': 'Травень', '06': 'Червень', '07': 'Липень', '08': 'Серпень',
            '09': 'Вересень', '10': 'Жовтень', '11': 'Листопад', '12': 'Грудень'
        }
        month_name = month_names.get(month_param, 'Січень')

        main_filename = f"main_operations_{year}_{month_param}.xlsx"
        goods_filename = f"goods_operations_{year}_{month_param}.xlsx"

        main_path = os.path.join(settings.BASE_DIR, 'main_xlsx', main_filename)
        goods_path = os.path.join(settings.BASE_DIR, 'goods_xlsx', goods_filename)

        operations_list = []
        goods_list = []
        top_export_countries = []
        top_import_countries = []

        if os.path.exists(main_path):
            try:
                df = pd.read_excel(main_path, engine='openpyxl')
                df.columns = [str(c).strip() for c in df.columns]

                column_mapping = {
                    'Країна-партнер': 'country',
                    'Товарообіг, USD': 'turnover',
                    'Експорт, USD': 'export',
                    'Імпорт, USD': 'import',
                    'Сальдо, USD': 'balance'
                }
                df = df.rename(columns=column_mapping)
                df['date'] = f"{month_name} {year}"

                numeric_cols = ['turnover', 'export', 'import', 'balance']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = (df[col].astype(str)
                                   .str.replace(r'\s+', '', regex=True)
                                   .str.replace(',', '.')
                                   .str.replace('$', '')
                                   )
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                if not df.empty:
                    top_ex_df = df.sort_values(by='export', ascending=False).head(5)
                    top_export_countries = [
                        {'country': row['country'], 'export_val': row['export']}
                        for _, row in top_ex_df.iterrows()
                    ]

                    top_im_df = df.sort_values(by='import', ascending=False).head(5)
                    top_import_countries = [
                        {'country': row['country'], 'import_val': row['import']}
                        for _, row in top_im_df.iterrows()
                    ]

                operations_list = df.to_dict('records')

            except Exception as e:
                print(f"Помилка основного файлу: {e}")

        if os.path.exists(goods_path):
            try:
                df_g = pd.read_excel(goods_path, engine='openpyxl')
                df_g.columns = [str(c).strip() for c in df_g.columns]

                mapping_g = {
                    'Група': 'product_goods',
                    'Товарообіг, USD': 'turnover_goods',
                    'Експорт, USD': 'export_goods',
                    'Імпорт, USD': 'import_goods',
                    'Сальдо, USD': 'balance_goods'
                }
                df_g = df_g.rename(columns=mapping_g)
                df_g['date'] = f"{month_name} {year}"

                numeric_g = ['turnover_goods', 'export_goods', 'import_goods', 'balance_goods']
                for col in numeric_g:
                    if col in df_g.columns:
                        df_g[col] = (df_g[col].astype(str)
                                     .str.replace(r'\s+', '', regex=True)
                                     .str.replace(',', '.')
                                     .str.replace('$', ''))
                        df_g[col] = pd.to_numeric(df_g[col], errors='coerce').fillna(0)

                goods_list = df_g.to_dict('records')
            except Exception as e:
                print(f"Помилка файлу товарів: {e}")

        context['forecast_image'] = create_forecast_graph()
        context['current_year'] = year
        context['current_month_name'] = month_names.get(month_param, 'Січень')

        context.update({
            'operations': operations_list,
            'top_export_countries': top_export_countries,
            'goods_operations': goods_list,
            'top_import_countries': top_import_countries,
            'selected_year': year,
            'selected_month': month_param,
            'current_month_name': month_name,
            'years': ['2017', '2018', '2019', '2020', '2021', '2022', '2023'],
            'months': [
                {'val': '01', 'name': 'Січень'}, {'val': '02', 'name': 'Лютий'},
                {'val': '03', 'name': 'Березень'}, {'val': '04', 'name': 'Квітень'},
                {'val': '05', 'name': 'Травень'}, {'val': '06', 'name': 'Червень'},
                {'val': '07', 'name': 'Липень'}, {'val': '08', 'name': 'Серпень'},
                {'val': '09', 'name': 'Вересень'}, {'val': '10', 'name': 'Жовтень'},
                {'val': '11', 'name': 'Листопад'}, {'val': '12', 'name': 'Грудень'}
            ]
        })

        print(f"Загружено строк: {len(operations_list)}")
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

def mongo_list(request):
    collection = get_collection_handle()
    operations = list(collection.find())
    for op in operations:
        op['id'] = str(op['_id'])
    return render(request, 'mongo_list.html', {'operations': operations})

def mongo_create(request):
    if request.method == 'POST':
        collection = get_collection_handle()

        new_operation = {
            "enterprise": request.POST.get("enterprise"),
            "op_type": request.POST.get("op_type"),
            "product": request.POST.get("product"),
            "amount": float(request.POST.get("amount")),
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        collection.insert_one(new_operation)

        return redirect('mongo_list')

    return render(request, 'mongo_create.html')


def mongo_edit(request, op_id):
    collection = get_collection_handle()
    operation = collection.find_one({"_id": ObjectId(op_id)})

    if request.method == 'POST':
        updated_data = {
            "enterprise": request.POST.get("enterprise"),
            "op_type": request.POST.get("op_type"),
            "product": request.POST.get("product"),
            "amount": float(request.POST.get("amount"))
        }
        collection.update_one(
            {"_id": ObjectId(op_id)},
            {"$set": updated_data}
        )
        return redirect('mongo_list')
    return render(request, 'mongo_edit.html', {'operation': operation})

def mongo_delete(request, op_id):
    collection = get_collection_handle()
    collection.delete_one({"_id": ObjectId(op_id)})
    return redirect('mongo_list')
