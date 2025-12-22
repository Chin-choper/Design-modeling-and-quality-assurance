import os
from django.views import generic
from django.conf import settings
from operations.models import Operation
from decimal import Decimal

class OperationList(generic.ListView):
    model = Operation
    context_object_name = 'operations'
    template_name = 'operation_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['available_years'] = Operation.objects.dates('date', 'year')
        context['available_months'] = Operation.objects.dates('date', 'month')
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
