from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from jobs.models import Job
from .models import Application

# tests for application flow
class ApplyFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', email='alice@example.com', password='password')
        self.job = Job.objects.create(
            title='Test Job', company_name='TestCo', description='Test', location='Kathmandu, Nepal'
        )

    def test_prevent_duplicate_active_application(self):
        # create an active application
        Application.objects.create(user=self.user, job=self.job, full_name='Alice', email='alice@example.com', cover_letter='Hi')

        self.client.force_login(self.user)
        apply_url = reverse('apply_job', args=[self.job.pk])
        resp = self.client.post(apply_url, {
            'full_name': 'Alice',
            'email': 'alice@example.com',
            'cover_letter': 'Second try',
        })

        # should redirect to existing application detail (no new application created)
        self.assertEqual(Application.objects.filter(user=self.user, job=self.job).count(), 1)
        self.assertEqual(resp.status_code, 302)

# test that users can reapply after withdrawing or being rejected
    def test_allow_reapply_after_withdrawn(self):
        # create withdrawn application
        Application.objects.create(user=self.user, job=self.job, full_name='Alice', email='alice@example.com', cover_letter='First', status=Application.STATUS_WITHDRAWN)

        self.client.force_login(self.user)
        apply_url = reverse('apply_job', args=[self.job.pk])
        resp = self.client.post(apply_url, {
            'full_name': 'Alice',
            'email': 'alice@example.com',
            'cover_letter': 'Reapply',
        })

        # new application should be created
        self.assertEqual(Application.objects.filter(user=self.user, job=self.job).count(), 2)
        self.assertEqual(resp.status_code, 302)

# withdrawing application
    def test_withdraw_application(self):
        app = Application.objects.create(user=self.user, job=self.job, full_name='Alice', email='alice@example.com', cover_letter='Hi')

        self.client.force_login(self.user)
        withdraw_url = reverse('withdraw_application', args=[app.pk])
        resp = self.client.post(withdraw_url)

        app.refresh_from_db()
        self.assertEqual(app.status, Application.STATUS_WITHDRAWN)
        self.assertEqual(resp.status_code, 302)
from django.test import TestCase

