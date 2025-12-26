import os
from django.views import generic
from django.conf import settings
from operations.models import Operation
from decimal import Decimal
from django.shortcuts import render, redirect
from .utils import get_collection_handle
from datetime import datetime
from bson.objectid import ObjectId

class OperationList(generic.ListView):
    model = Operation
    context_object_name = 'operations'
    template_name = 'operation_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_years'] = Operation.objects.dates('date', 'year')

        all_dates_qs = Operation.objects.dates('date', 'month')

        selected_year = self.request.GET.get('year')

        if selected_year:
            context['available_months'] = all_dates_qs.filter(date__year=selected_year)
        else:
            unique_months = []
            seen_months = set()
            for d in all_dates_qs:
                if d.month not in seen_months:
                    unique_months.append(d)
                    seen_months.add(d.month)
            unique_months.sort(key=lambda x: x.month)
            context['available_months'] = unique_months

        base_qs = Operation.objects.all()
        base_qs = Operation.objects.all()

        if self.request.GET.get('year'):
            base_qs = base_qs.filter(date__year=self.request.GET.get('year'))
        if self.request.GET.get('month'):
            base_qs = base_qs.filter(date__month=self.request.GET.get('month'))

        context['operations'] = base_qs.filter(op_type__in=['Export', 'Import'])
        context['top_export_countries'] = base_qs.filter(op_type='TopExport').order_by('-amount')
        context['top_import_countries'] = base_qs.filter(op_type='TopImport').order_by('-amount')

        context['zap_stal'] = base_qs.filter(op_type='Zaporizhstal')
        context['zap_koks'] = base_qs.filter(op_type='Zaporizhkoks')
        context['motor'] = base_qs.filter(op_type='MotorSich')
        context['dnipro'] = base_qs.filter(op_type='DniproSpec')

        context['selected_year'] = self.request.GET.get('year')
        context['selected_month'] = self.request.GET.get('month')
        return context

    def get(self, request, *args, **kwargs):
        Operation.objects.all().delete()
        try:
            file_path = os.path.join(settings.BASE_DIR, 'test_data')
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) == 4:
                        Operation.objects.create(
                            op_type=parts[0].strip(),
                            category=parts[1].strip(),
                            partner_country='-',
                            amount=Decimal(parts[2].strip()),
                            date=parts[3].strip()
                        )
                    elif len(parts) == 5:
                        Operation.objects.create(
                            op_type=parts[0].strip(),
                            category='-',
                            partner_country=parts[2].strip(),
                            amount=Decimal(parts[3].strip()),
                            date=parts[4].strip()
                        )

        except Exception as e:
            print(f"Помилка: {e}")
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
