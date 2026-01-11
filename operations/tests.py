from django.test import TestCase, Client
from django.urls import reverse
from operations.models import Operation
from unittest.mock import patch, MagicMock
from decimal import Decimal
import datetime

class OperationModelTest(TestCase):

    def setUp(self):
        self.operation = Operation.objects.create(
            op_type='Export',
            category='Grain',
            partner_country='Poland',
            amount=Decimal('1000.50'),
            date=datetime.date(2023, 5, 20)
        )

    def test_model_fields(self):
        saved_op = Operation.objects.get(id=self.operation.id)
        self.assertEqual(saved_op.op_type, 'Export')
        self.assertEqual(saved_op.amount, Decimal('1000.50'))
        self.assertEqual(saved_op.partner_country, 'Poland')

    def test_string_representation(self):
        self.assertEqual(str(self.operation), "Export - Grain")
