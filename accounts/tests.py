from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from accounts.models import Resume
import io


class ResumeModelTests(TestCase):
    """Tests for Resume model"""

    def setUp(self):
        """Create a test user for resume testing"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def create_test_file(self, filename='test.pdf', content=b'test pdf content', size=None):
        """Helper to create test file"""
        if size:
            content = b'x' * size
        return SimpleUploadedFile(
            filename,
            content,
            content_type='application/pdf'
        )

    def test_resume_creation(self):
        """Test creating a basic resume"""
        resume_file = self.create_test_file('resume.pdf')
        resume = Resume.objects.create(
            user=self.user,
            file=resume_file,
            name='Main Resume'
        )
        self.assertEqual(resume.user, self.user)
        self.assertEqual(resume.name, 'Main Resume')
        self.assertFalse(resume.is_default)

    def test_default_resume_per_user(self):
        """Test that only one default resume per user is enforced"""
        resume1 = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('resume1.pdf'),
            name='Resume 1',
            is_default=True
        )
        self.assertTrue(resume1.is_default)

        # Create second resume and set as default
        resume2 = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('resume2.pdf'),
            name='Resume 2',
            is_default=True
        )

        # Refresh from DB and check that only resume2 is default
        resume1.refresh_from_db()
        self.assertFalse(resume1.is_default)
        self.assertTrue(resume2.is_default)

    def test_resume_ordering(self):
        """Test resumes are ordered by default first, then by creation date"""
        resume1 = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('resume1.pdf'),
            name='Resume 1'
        )
        resume2 = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('resume2.pdf'),
            name='Resume 2',
            is_default=True
        )

        resumes = Resume.objects.filter(user=self.user)
        self.assertEqual(resumes.first(), resume2)  # Default first
        self.assertEqual(resumes.last(), resume1)

    def test_resume_get_file_size_mb(self):
        """Test file size calculation"""
        size_bytes = int(1024 * 1024 * 2.5)  # 2.5 MB
        resume = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('resume.pdf', size=size_bytes),
            name='Resume'
        )
        self.assertEqual(resume.get_file_size_mb(), 2.5)

    def test_resume_str_representation(self):
        """Test string representation of resume"""
        resume = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('resume.pdf'),
            name='My Resume'
        )
        expected = f"My Resume ({self.user.email})"
        self.assertEqual(str(resume), expected)

    def test_multiple_users_have_independent_defaults(self):
        """Test that default resume is per-user"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )

        resume1 = Resume.objects.create(
            user=self.user,
            file=self.create_test_file('resume1.pdf'),
            is_default=True
        )
        resume2 = Resume.objects.create(
            user=user2,
            file=self.create_test_file('resume2.pdf'),
            is_default=True
        )

        # Both should be default for their respective users
        self.assertTrue(resume1.is_default)
        self.assertTrue(resume2.is_default)


class ResumeProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)

    def create_test_file(self, filename='resume.pdf'):
        return SimpleUploadedFile(filename, b'pdf-content', content_type='application/pdf')

    def test_profile_shows_uploaded_resumes(self):
        Resume.objects.create(
            user=self.user,
            file=self.create_test_file('profile-resume.pdf'),
            name='Profile Resume',
            is_default=True
        )

        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Resumes')
        self.assertContains(response, 'Profile Resume')

    def test_profile_resume_upload_creates_resume(self):
        upload = self.create_test_file('new-resume.pdf')
        response = self.client.post('/accounts/profile/', {
            'form_type': 'resume_upload',
            'name': 'New Resume',
            'is_default': 'on',
            'file': upload,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Resume.objects.filter(user=self.user).count(), 1)
        resume = Resume.objects.get(user=self.user)
        self.assertEqual(resume.name, 'New Resume')
        self.assertTrue(resume.is_default)

