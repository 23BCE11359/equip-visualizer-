from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.management import call_command
from .models import Dataset, Equipment
import io


class UploadAndSummaryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create a user for authenticated endpoints
        self.user = User.objects.create_user('tester', 't@example.com', 'password')

    def test_upload_csv_and_dataset_summary(self):
        # authenticate
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
Compressor-1,Compressor,95,8.4,95
"""
        fp = io.BytesIO(csv_content.encode())
        fp.name = 'test.csv'

        res = self.client.post('/api/upload/', {'file': fp}, format='multipart')
        self.assertEqual(res.status_code, 200)
        self.assertIn('dataset', res.data)
        ds_id = res.data['dataset']['id']
        self.assertTrue(Dataset.objects.filter(id=ds_id).exists())

        # Check dataset summary
        res2 = self.client.get(f'/api/datasets/{ds_id}/summary/')
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.data['equipment_count'], 2)
        self.assertAlmostEqual(res2.data['avg_flowrate'], (120+95)/2)

    def test_upload_requires_auth(self):
        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
"""
        fp = io.BytesIO(csv_content.encode())
        fp.name = 'noauth.csv'

        res = self.client.post('/api/upload/', {'file': fp}, format='multipart')
        self.assertIn(res.status_code, (401, 403))

    def test_upload_with_token(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
"""
        fp = io.BytesIO(csv_content.encode())
        fp.name = 'token.csv'
        res = self.client.post('/api/upload/', {'file': fp}, format='multipart')
        self.assertEqual(res.status_code, 200)
        self.assertIn('created', res.data)
        self.assertEqual(res.data['created'], 1)

    def test_pdf_requires_auth(self):
        # Upload dataset
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
"""
        fp = io.BytesIO(csv_content.encode())
        fp.name = 'pdftest.csv'
        res = self.client.post('/api/upload/', {'file': fp}, format='multipart')
        ds_id = res.data['dataset']['id']

        # Unauthenticated request should fail
        client2 = APIClient()
        res2 = client2.get(f'/api/datasets/{ds_id}/report/pdf/')
        self.assertIn(res2.status_code, (401, 403))

        # Authenticated should succeed or 501 if reportlab missing
        res3 = self.client.get(f'/api/datasets/{ds_id}/report/pdf/')
        self.assertIn(res3.status_code, (200, 501))

    def test_token_auth_endpoint(self):
        res = self.client.post('/api-token-auth/', {'username': 'tester', 'password': 'password'}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertIn('token', res.data)

    def test_load_sample_command(self):
        # Ensure sample command runs and creates at least one dataset
        call_command('load_sample')
        self.assertTrue(Dataset.objects.exists())

    def test_create_demo_user_command(self):
        from django.contrib.auth.models import User
        from rest_framework.authtoken.models import Token
        call_command('create_demo_user')
        self.assertTrue(User.objects.filter(username='demo').exists())
        u = User.objects.get(username='demo')
        self.assertTrue(Token.objects.filter(user=u).exists())

    def test_dataset_pdf_generation(self):
        # Ensure PDF endpoint returns PDF content
        from rest_framework.authtoken.models import Token
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # Ensure sample dataset exists
        call_command('load_sample')
        ds = Dataset.objects.first()
        res = self.client.get(f'/api/datasets/{ds.id}/report/pdf/')
        # Should return PDF or 501
        self.assertIn(res.status_code, (200, 501))
        if res.status_code == 200:
            self.assertTrue(res.content.startswith(b'%PDF'))

    def test_generate_report_command(self):
        call_command('load_sample')
        ds = Dataset.objects.first()
        out = 'backend/docs/test_report.pdf'
        # remove if exists
        import os
        if os.path.exists(out):
            os.remove(out)
        call_command('generate_report', '--dataset', str(ds.id), '--out', out)
        self.assertTrue(os.path.exists(out))
        # basic content check
        with open(out, 'rb') as fh:
            data = fh.read()
            self.assertTrue(data.startswith(b'%PDF'))




# Create your tests here.
