from django.shortcuts import render


import os
from django.views import generic
from django.conf import settings
from operations.models import Operation
from decimal import Decimal

class OperationList(generic.ListView):
    model = Operation
    context_object_name = 'operations'
    template_name = 'operation_list.html'

    def get(self, request, *args, **kwargs):
        Operation.objects.all().delete()
        try:
            file_path = os.path.join(settings.BASE_DIR, 'test_data')
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')

                    if len(parts) == 3:
                        Operation.objects.get_or_create(
                            op_type=parts[0].strip(),
                            category=parts[1].strip(),
                            date=parts[2].strip(),
                            defaults={'amount': 0, 'partner_country': '-'} 
                        )
        except Exception as e:
            print(f"Помилка: {e}")

        return super().get(request, *args, **kwargs)
