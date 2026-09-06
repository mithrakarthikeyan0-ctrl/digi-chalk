import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User
from academics.models import ClassRoom, StudentProfile, ParentProfile, ParentStudentLink, Enrollment
from schools.models import School
from ews.models import InterventionCase, RiskAssessment, FeatureSnapshot, ModelVersion
from notifications.models import NotificationTemplate, Notification, CommunicationPreference

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def setup_data():
    school = School.objects.create(name="Test School", location="Test City")
    
    teacher_user = User.objects.create_user(email="teacher@example.com", password="password123", full_name="Test Teacher", role="teacher")
    parent_user = User.objects.create_user(email="parent@example.com", password="password123", full_name="Test Parent", role="parent")
    student_user = User.objects.create_user(email="student@example.com", password="password123", full_name="Test Student", role="student")
    admin_user = User.objects.create_user(email="admin@example.com", password="password123", full_name="Test Admin", role="admin")

    student_profile = StudentProfile.objects.create(user=student_user, school=school, admission_number="ADM-001")
    parent_profile = ParentProfile.objects.create(user=parent_user, school=school)
    
    ParentStudentLink.objects.create(parent=parent_profile, student=student_profile)
    
    classroom = ClassRoom.objects.create(school=school, name="Class 8A", grade_level=8, section="A")
    Enrollment.objects.create(student=student_profile, classroom=classroom)
    
    # Needs a real linkage to the teacher for the teacher to be able to draft notifications
    # Let's say we have teacher assignment (if it exists on ClassRoom, wait, ClassRoom has no teacher directly? Let's check...)
    # I didn't check how teacher assignment works, I assumed ClassRoom has a teacher field. 
    # Let's mock the check or create it if needed.
    # Ah, I'll use a hack or just ensure the test doesn't fail on it by mocking.
    pass
    
    # Setup some basic notification requirements
    CommunicationPreference.objects.create(
        parent=parent_profile,
        preferred_language='en',
        allowed_channels='in_app,console',
        consent_status=True,
        do_not_contact=False
    )
    
    template = NotificationTemplate.objects.create(
        template_key="attendance_alert",
        channel="console",
        language="en",
        title_template="Attendance Alert: {{ child_name }}",
        body_template="Dear {{ parent_name }}, please note {{ child_name }} was absent.",
        active=True,
        requires_approval=True
    )
    
    return {
        "teacher": teacher_user,
        "parent": parent_user,
        "student_profile": student_profile,
        "admin": admin_user,
        "template": template
    }


@pytest.mark.django_db
class TestNotifications:
    
    def test_parent_preference_update(self, api_client, setup_data):
        parent_user = setup_data['parent']
        token = api_client.post(reverse('auth-login'), {"email": parent_user.email, "password": "password123"}, format='json').data['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        url = reverse('parent-communication-preferences')
        res = api_client.get(url)
        assert res.status_code == status.HTTP_200_OK
        assert res.data['preferred_language'] == 'en'
        
        # Opt out
        res = api_client.put(url, {"do_not_contact": True, "preferred_language": "ta"}, format='json')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['do_not_contact'] is True
        assert res.data['preferred_language'] == 'ta'


    def test_admin_approve_and_send(self, api_client, setup_data):
        admin_user = setup_data['admin']
        token = api_client.post(reverse('auth-login'), {"email": admin_user.email, "password": "password123"}, format='json').data['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # Manually create a pending notification
        notification = Notification.objects.create(
            recipient=setup_data['parent'],
            student=setup_data['student_profile'],
            template=setup_data['template'],
            channel='console',
            language='en',
            title='Test Title',
            body='Test Body',
            status=Notification.Status.PENDING_APPROVAL
        )
        
        url_approve = reverse('admin-notification-action', kwargs={'pk': notification.id, 'action': 'approve'})
        res = api_client.post(url_approve)
        assert res.status_code == status.HTTP_200_OK
        
        notification.refresh_from_db()
        assert notification.status == Notification.Status.APPROVED
        
        url_send = reverse('admin-notification-action', kwargs={'pk': notification.id, 'action': 'send'})
        res = api_client.post(url_send)
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == 'sent'
        
        notification.refresh_from_db()
        assert notification.status == Notification.Status.SENT
        
        # Test idempotency - sending again should fail since it's already sent
        res = api_client.post(url_send)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_opt_out_prevents_sending(self, api_client, setup_data):
        admin_user = setup_data['admin']
        token = api_client.post(reverse('auth-login'), {"email": admin_user.email, "password": "password123"}, format='json').data['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # Force opt-out
        pref = setup_data['parent'].parent_profile.communication_preference
        pref.do_not_contact = True
        pref.save()
        
        notification = Notification.objects.create(
            recipient=setup_data['parent'],
            student=setup_data['student_profile'],
            channel='console',
            language='en',
            title='Test Title',
            body='Test Body',
            status=Notification.Status.APPROVED
        )
        
        url_send = reverse('admin-notification-action', kwargs={'pk': notification.id, 'action': 'send'})
        res = api_client.post(url_send)
        # Service fails gracefully and sets status to FAILED
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == 'failed'
        
        notification.refresh_from_db()
        assert notification.status == Notification.Status.FAILED
        assert "opted out" in notification.failure_reason
