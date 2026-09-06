import pytest
from rest_framework.test import APIClient
from accounts.models import User
from schools.models import School
from academics.models import ClassRoom, StudentProfile, ParentProfile, ParentStudentLink, Enrollment
from sessions.models import ClassSession

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def school(db):
    return School.objects.create(name="Test School", location="Test Location")

@pytest.fixture
def classroom(db, school):
    return ClassRoom.objects.create(
        school=school, name="Class 8A", grade_level=8, section="A"
    )

@pytest.fixture
def teacher_user(db):
    return User.objects.create_user(
        email="teacher@example.com", full_name="Test Teacher", password="password123", role=User.Role.TEACHER
    )

@pytest.fixture
def student_user(db):
    return User.objects.create_user(
        email="student@example.com", full_name="Test Student", password="password123", role=User.Role.STUDENT
    )

@pytest.fixture
def parent_user(db):
    return User.objects.create_user(
        email="parent@example.com", full_name="Test Parent", password="password123", role=User.Role.PARENT
    )

@pytest.fixture
def headmaster_user(db):
    return User.objects.create_user(
        email="headmaster@example.com", full_name="Test Headmaster", password="password123", role=User.Role.HEADMASTER
    )

@pytest.fixture
def student_profile(db, student_user, school):
    return StudentProfile.objects.create(
        user=student_user, school=school, admission_number="ADM-001"
    )

@pytest.fixture
def parent_profile(db, parent_user, school):
    return ParentProfile.objects.create(
        user=parent_user, school=school
    )

@pytest.fixture
def enrollment(db, student_profile, classroom):
    return Enrollment.objects.create(
        student=student_profile, classroom=classroom, active=True
    )

@pytest.fixture
def parent_student_link(db, parent_profile, student_profile):
    return ParentStudentLink.objects.create(
        parent=parent_profile, student=student_profile
    )
