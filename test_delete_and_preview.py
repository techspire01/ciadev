#!/usr/bin/env python
"""
Test script to verify delete functionality and preview endpoints work correctly.
Tests all three delete scenarios:
1. Delete resume only
2. Delete attachment only
3. Delete entire application
"""

import os
import sys
import django
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

# Expose User model for tests (custom user)
User = get_user_model()

from app.models import Supplier
from portal.models import PortalJob, PortalInternship, JobApplication, InternshipApplication
from django.utils import timezone


class DeleteAndPreviewTests(TestCase):
    """Test delete and preview functionality for applications"""
    
    def setUp(self):
        """Create test data"""
        # Create a test user and supplier using the project's custom user model
        User = get_user_model()
        self.user = User.objects.create_user(
            email='employer@test.com',
            password='testpass123'
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Employer',
            user=self.user,
            email='employer@test.com',
        )
        
        # Create a test job (align fields with current PortalJob model)
        self.job = PortalJob.objects.create(
            title='Test Job',
            description='Test job description',
            supplier=self.supplier,
            posted_date=timezone.now(),
            salary='30000-50000',
            location='Test City',
        )
        
        # Create a test internship (align fields with current PortalInternship model)
        self.internship = PortalInternship.objects.create(
            title='Test Internship',
            description='Test internship description',
            supplier=self.supplier,
            posted_date=timezone.now(),
            duration='3 months',
            location='Test City',
            salary='Stipend'
        )
        
        # Create test files
        self.test_resume = SimpleUploadedFile(
            "test_resume.pdf",
            b"PDF test content",
            content_type="application/pdf"
        )
        
        self.test_attachment = SimpleUploadedFile(
            "test_attachment.pdf",
            b"PDF attachment content",
            content_type="application/pdf"
        )
        
        # Create a job application (align fields with current JobApplication model)
        self.job_app = JobApplication.objects.create(
            job=self.job,
            supplier=self.supplier,
            first_name='John',
            last_name='Doe',
            email='john@test.com',
            phone='1234567890',
            resume=self.test_resume,
            additional_attachment=self.test_attachment,
            applied_date=timezone.now()
        )
        
        # Create an internship application (align fields with current InternshipApplication model)
        self.internship_app = InternshipApplication.objects.create(
            internship=self.internship,
            supplier=self.supplier,
            first_name='Jane',
            last_name='Doe',
            email='jane@test.com',
            phone='0987654321',
            resume=SimpleUploadedFile("int_resume.pdf", b"PDF content"),
            additional_attachment=SimpleUploadedFile("int_attachment.pdf", b"PDF content"),
            applied_date=timezone.now()
        )
        
        # Create test client
        self.client = Client()
        
    def test_preview_job_resume(self):
        """Test preview endpoint for job application resume"""
        # Login as supplier (use email as username for custom user model)
        self.client.login(username='employer@test.com', password='testpass123')
        
        # Call preview endpoint
        response = self.client.get(
            f'/portal-admin/preview/job/{self.job_app.id}/resume/'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('url', data)
        self.assertIn('filename', data)
        self.assertEqual(data['file_type'], 'resume')
        print(f"✅ Preview job resume: {data['filename']}")
        
    def test_preview_internship_attachment(self):
        """Test preview endpoint for internship application attachment"""
        # Login as supplier (use email as username for custom user model)
        self.client.login(username='employer@test.com', password='testpass123')
        
        # Call preview endpoint
        response = self.client.get(
            f'/portal-admin/preview/internship/{self.internship_app.id}/attachment/'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('url', data)
        self.assertIn('filename', data)
        self.assertEqual(data['file_type'], 'attachment')
        print(f"✅ Preview internship attachment: {data['filename']}")
        
    def test_delete_resume_only_job(self):
        """Test deleting only resume from job application"""
        # Verify initial state
        self.assertTrue(self.job_app.resume)
        self.assertTrue(self.job_app.additional_attachment)
        initial_id = self.job_app.id
        
        # Login as supplier (use email as username for custom user model)
        self.client.login(username='employer@test.com', password='testpass123')
        
        # Send delete request
        response = self.client.post(
            f'/portal-admin/job/{self.job.id}/applicant/{self.job_app.id}/delete/',
            {'delete_resume_only': 'true'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verify application still exists but resume is deleted
        app = JobApplication.objects.get(id=initial_id)
        self.assertFalse(app.resume)
        self.assertTrue(app.additional_attachment)  # Attachment should remain
        print("✅ Delete resume only (job): Resume deleted, attachment preserved")
        
    def test_delete_attachment_only_internship(self):
        """Test deleting only attachment from internship application"""
        # Verify initial state
        self.assertTrue(self.internship_app.resume)
        self.assertTrue(self.internship_app.additional_attachment)
        initial_id = self.internship_app.id
        
        # Login as supplier (use email as username for custom user model)
        self.client.login(username='employer@test.com', password='testpass123')
        
        # Send delete request
        response = self.client.post(
            f'/portal-admin/internship/{self.internship.id}/applicant/{self.internship_app.id}/delete/',
            {'delete_attachment_only': 'true'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verify application still exists but attachment is deleted
        app = InternshipApplication.objects.get(id=initial_id)
        self.assertTrue(app.resume)  # Resume should remain
        self.assertFalse(app.additional_attachment)
        print("✅ Delete attachment only (internship): Attachment deleted, resume preserved")
        
    def test_delete_entire_application(self):
        """Test deleting entire application"""
        job_app_id = self.job_app.id
        
        # Login as supplier (use email for custom user model)
        self.client.login(username='employer@test.com', password='testpass123')
        
        # Send delete request (no specific flags = delete all)
        response = self.client.post(
            f'/portal-admin/job/{self.job.id}/applicant/{self.job_app.id}/delete/',
            {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verify application is deleted
        with self.assertRaises(JobApplication.DoesNotExist):
            JobApplication.objects.get(id=job_app_id)
        print("✅ Delete entire application: Application and all files deleted")
        
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot preview/delete"""
        # Create another supplier
        other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123'
        )
        other_supplier = Supplier.objects.create(
            name='Other Employer',
            user=other_user,
            email='other@test.com'
        )
        
        # Login as different supplier (use email for authentication)
        self.client.login(username='other@test.com', password='testpass123')
        
        # Try to preview
        response = self.client.get(
            f'/portal-admin/preview/job/{self.job_app.id}/resume/'
        )
        
        # Should fail
        self.assertEqual(response.status_code, 404)
        print("✅ Authorization check: Unauthorized users blocked")


if __name__ == '__main__':
    import unittest
    
    print("\n" + "="*60)
    print("Testing Delete and Preview Functionality")
    print("="*60 + "\n")
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(DeleteAndPreviewTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
        for failure in result.failures + result.errors:
            print(f"  - {failure[0]}")
    print("="*60 + "\n")
    
    sys.exit(0 if result.wasSuccessful() else 1)
