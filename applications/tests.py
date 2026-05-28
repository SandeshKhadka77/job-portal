from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from jobs.models import Job
from accounts.models import Resume
from .models import Application
from django.test import RequestFactory, override_settings
from django.contrib.admin.sites import AdminSite
from .admin import ApplicationAdmin
from django.contrib.messages.storage.fallback import FallbackStorage


class ApplyFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', email='alice@example.com', password='password')
        self.job = Job.objects.create(
            title='Test Job', company_name='TestCo', description='Test', location='Kathmandu, Nepal'
        )

    def create_test_file(self, filename='test.pdf'):
        return SimpleUploadedFile(filename, b'pdf-content', content_type='application/pdf')

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

    def test_withdraw_application(self):
        app = Application.objects.create(user=self.user, job=self.job, full_name='Alice', email='alice@example.com', cover_letter='Hi')

        self.client.force_login(self.user)
        withdraw_url = reverse('withdraw_application', args=[app.pk])
        resp = self.client.post(withdraw_url)

        app.refresh_from_db()
        self.assertEqual(app.status, Application.STATUS_WITHDRAWN)
        self.assertEqual(resp.status_code, 302)

    def test_apply_with_resume(self):
        """Test applying with a selected resume"""
        # Create a resume
        resume = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('alice-resume.pdf'),
            name='Alice Resume',
            is_default=True
        )

        self.client.force_login(self.user)
        apply_url = reverse('apply_job', args=[self.job.pk])
        resp = self.client.post(apply_url, {
            'full_name': 'Alice',
            'email': 'alice@example.com',
            'cover_letter': 'Application with resume',
            'resume_id': resume.id,
        })

        # Application should be created with the resume
        app = Application.objects.get(user=self.user, job=self.job)
        self.assertEqual(app.resume, resume)
        self.assertEqual(resp.status_code, 302)

    def test_apply_shows_user_resumes(self):
        """Test that apply page shows user's resumes"""
        resume1 = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('resume1.pdf'),
            name='Resume 1',
            is_default=True
        )
        resume2 = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('resume2.pdf'),
            name='Resume 2'
        )

        self.client.force_login(self.user)
        apply_url = reverse('apply_job', args=[self.job.pk])
        resp = self.client.get(apply_url)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Resume 1')
        self.assertContains(resp, 'Resume 2')
        # Default resume should be pre-selected
        self.assertContains(resp, 'selected')

    def test_owner_can_download_resume(self):
        # Create a resume and application
        resume = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('download.pdf'),
            name='Download Resume'
        )
        app = Application.objects.create(user=self.user, job=self.job, full_name='Alice', email='alice@example.com', cover_letter='Hi', resume=resume)

        self.client.force_login(self.user)
        url = reverse('download_resume', args=[app.pk])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        # Content type should be application/pdf
        self.assertIn('application/pdf', resp['Content-Type'])

    def test_other_user_cannot_download_resume(self):
        other = User.objects.create_user(username='bob', email='bob@example.com', password='password')
        resume = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('download2.pdf'),
            name='Download Resume 2'
        )
        app = Application.objects.create(user=self.user, job=self.job, full_name='Alice', email='alice@example.com', cover_letter='Hi', resume=resume)

        self.client.force_login(other)
        url = reverse('download_resume', args=[app.pk])
        resp = self.client.get(url)

        # Should redirect due to permission
        self.assertEqual(resp.status_code, 302)

    def test_admin_can_download_resume(self):
        admin = User.objects.create_user(username='admin', email='admin@example.com', password='password', is_staff=True)
        resume = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('download3.pdf'),
            name='Download Resume 3'
        )
        app = Application.objects.create(user=self.user, job=self.job, full_name='Alice', email='alice@example.com', cover_letter='Hi', resume=resume)

        self.client.force_login(admin)
        url = reverse('download_resume', args=[app.pk])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('application/pdf', resp['Content-Type'])

    def test_admin_download_exceeds_file_limit(self):
        admin = User.objects.create_user(username='admin2', email='admin2@example.com', password='password', is_staff=True)
        # create two resumes
        resume1 = Resume.objects.create(user=self.user, file=self.create_test_file('a.pdf'), name='A')
        resume2 = Resume.objects.create(user=self.user, file=self.create_test_file('b.pdf'), name='B')
        app1 = Application.objects.create(user=self.user, job=self.job, full_name='A', email='a@example.com', cover_letter='x', resume=resume1)
        app2 = Application.objects.create(user=self.user, job=self.job, full_name='B', email='b@example.com', cover_letter='x', resume=resume2)

        rf = RequestFactory()
        request = rf.post('/admin/applications/application/')
        request.user = admin

        admin_site = AdminSite()
        admin_instance = ApplicationAdmin(Application, admin_site)
        # avoid messages middleware requirement in tests
        admin_instance.message_user = lambda *a, **k: None
        with override_settings(RESUME_DOWNLOAD_MAX_FILES=1):
            result = admin_instance.download_resumes(request, Application.objects.filter(pk__in=[app1.pk, app2.pk]))
            self.assertIsNone(result)

    def test_admin_download_exceeds_size_limit(self):
        admin = User.objects.create_user(username='admin3', email='admin3@example.com', password='password', is_staff=True)
        # create one large resume (> limit)
        large_content = b'a' * 2048  # 2 KB
        resume = Resume.objects.create(user=self.user, file=SimpleUploadedFile('large.pdf', large_content, content_type='application/pdf'), name='Large')
        app = Application.objects.create(user=self.user, job=self.job, full_name='Large', email='l@example.com', cover_letter='x', resume=resume)

        rf = RequestFactory()
        request = rf.post('/admin/applications/application/')
        request.user = admin

        admin_site = AdminSite()
        admin_instance = ApplicationAdmin(Application, admin_site)
        admin_instance.message_user = lambda *a, **k: None
        # set tiny limit to trigger size exceeded
        with override_settings(RESUME_DOWNLOAD_MAX_TOTAL_MB=0.00001):
            result = admin_instance.download_resumes(request, Application.objects.filter(pk=app.pk))
            self.assertIsNone(result)


