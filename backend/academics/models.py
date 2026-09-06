from django.db import models
from django.conf import settings
from common.models import UUIDTimeStampedModel


class ClassRoom(UUIDTimeStampedModel):
    """
    Represents a specific classroom/cohort (e.g. Class 8B) within a school.
    """
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='classrooms'
    )
    name = models.CharField(max_length=100)
    grade_level = models.IntegerField()
    section = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Class Room'
        verbose_name_plural = 'Class Rooms'
        ordering = ['grade_level', 'section']
        unique_together = ('school', 'grade_level', 'section')

    def __str__(self):
        return f"{self.name} ({self.school.name})"


class StudentProfile(UUIDTimeStampedModel):
    """
    Profile extension for users with the student role.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='students'
    )
    admission_number = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'

    def __str__(self):
        return f"{self.user.full_name} ({self.admission_number})"


class ParentProfile(UUIDTimeStampedModel):
    """
    Profile extension for users with the parent role.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parent_profile'
    )
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='parents'
    )

    class Meta:
        verbose_name = 'Parent Profile'
        verbose_name_plural = 'Parent Profiles'

    def __str__(self):
        return f"Parent: {self.user.full_name}"


class ParentStudentLink(UUIDTimeStampedModel):
    """
    Links parents to their respective enrolled children.
    """
    parent = models.ForeignKey(
        ParentProfile,
        on_delete=models.CASCADE,
        related_name='child_links'
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='parent_links'
    )

    class Meta:
        unique_together = ('parent', 'student')
        verbose_name = 'Parent-Student Link'
        verbose_name_plural = 'Parent-Student Links'

    def __str__(self):
        return f"{self.parent.user.full_name} -> {self.student.user.full_name}"


class Enrollment(UUIDTimeStampedModel):
    """
    Tracks which classroom/cohort a student belongs to in a given academic year.
    """
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    academic_year = models.CharField(max_length=20, default='2026-2027')
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'classroom', 'academic_year')
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'

    def __str__(self):
        return f"{self.student.user.full_name} in {self.classroom.name} ({self.academic_year})"
