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


class OperationViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.list_url = reverse('operation_list')
        self.mongo_list_url = reverse('mongo_list')
        self.mongo_create_url = reverse('mongo_create')

    def test_main_page_loads(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'operation_list.html')

    @patch('operations.views.get_collection_handle')
    def test_mongo_list_loads(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.find.return_value = []
        mock_get_collection.return_value = mock_collection

        response = self.client.get(self.mongo_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mongo_list.html')

    @patch('operations.views.get_collection_handle')
    def test_mongo_create_post_success(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        data = {
            "enterprise": "Test Firm",
            "op_type": "Import",
            "product": "Fuel",
            "amount": "500.00"
        }

        response = self.client.post(self.mongo_create_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(mock_collection.insert_one.called)
        args, _ = mock_collection.insert_one.call_args
        inserted_data = args[0]
        self.assertEqual(inserted_data['enterprise'], "Test Firm")
        self.assertEqual(inserted_data['amount'], 500.0)

    def test_mongo_create_post_fail_invalid_data(self):
        data = {
            "enterprise": "Test Firm",
            "op_type": "Import",
            "product": "Fuel",
            "amount": "not_a_number"
        }
        with self.assertRaises(ValueError):
            self.client.post(self.mongo_create_url, data)
