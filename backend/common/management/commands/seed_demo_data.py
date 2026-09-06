from django.core.management.base import BaseCommand
from accounts.models import User
from schools.models import School
from academics.models import ClassRoom, StudentProfile, ParentProfile, ParentStudentLink, Enrollment
from lessons.models import Lesson
from quizzes.models import Quiz, QuizQuestion, QuizChoice

class Command(BaseCommand):
    help = 'Seeds safe demo data for local development (no real PII or production defaults)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting demo data seed...")

        # 1. School
        school, _ = School.objects.get_or_create(
            name="Demo Digichalk Academy",
            location="Localhostville"
        )
        
        # 2. Users (Safe generic passwords)
        # Headmaster
        if not User.objects.filter(email='admin@digichalk.local').exists():
            User.objects.create_superuser(
                email='admin@digichalk.local',
                password='demopassword123',
                full_name='Demo Admin',
                role='admin'
            )
            
        # Teacher
        teacher, _ = User.objects.get_or_create(
            email='teacher@digichalk.local',
            defaults={
                'full_name': 'Demo Teacher',
                'role': 'teacher'
            }
        )
        if not teacher.check_password('demopassword123'):
            teacher.set_password('demopassword123')
            teacher.save()

        # Parent
        parent, _ = User.objects.get_or_create(
            email='parent@digichalk.local',
            defaults={
                'full_name': 'Demo Parent',
                'role': 'parent'
            }
        )
        if not parent.check_password('demopassword123'):
            parent.set_password('demopassword123')
            parent.save()

        # Student
        student, _ = User.objects.get_or_create(
            email='student@digichalk.local',
            defaults={
                'full_name': 'Demo Student',
                'role': 'student'
            }
        )
        if not student.check_password('demopassword123'):
            student.set_password('demopassword123')
            student.save()

        # 3. Profiles and Links
        student_prof, _ = StudentProfile.objects.get_or_create(
            user=student,
            defaults={'school': school, 'admission_number': 'DEMO-001'}
        )
        parent_prof, _ = ParentProfile.objects.get_or_create(
            user=parent,
            defaults={'school': school}
        )
        ParentStudentLink.objects.get_or_create(parent=parent_prof, student=student_prof)

        # 4. Classroom and Enrollment
        classroom, _ = ClassRoom.objects.get_or_create(
            school=school,
            name="Demo Class 8A",
            grade_level=8,
            section="A"
        )
        Enrollment.objects.get_or_create(student=student_prof, classroom=classroom)

        # 5. Lesson and Quiz Demo Data
        lesson, _ = Lesson.objects.get_or_create(
            classroom=classroom,
            title="Demo Math Lesson: Algebra Basics",
            defaults={
                'teacher': teacher,
                'subject': 'Mathematics',
                'description': 'Introduction to algebra.',
                'status': 'published',
                'duration_seconds': 1800
            }
        )

        quiz, created = Quiz.objects.get_or_create(
            lesson=lesson,
            title="Algebra Basics Quiz",
            defaults={'allow_retry': True}
        )
        
        if created:
            q1 = QuizQuestion.objects.create(quiz=quiz, question_text="What is x in x + 2 = 5?", order=1)
            QuizChoice.objects.create(question=q1, choice_text="2", is_correct=False)
            QuizChoice.objects.create(question=q1, choice_text="3", is_correct=True)
            QuizChoice.objects.create(question=q1, choice_text="4", is_correct=False)

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data!'))
        self.stdout.write(self.style.SUCCESS('Users created:'))
        self.stdout.write('- admin@digichalk.local / demopassword123')
        self.stdout.write('- teacher@digichalk.local / demopassword123')
        self.stdout.write('- parent@digichalk.local / demopassword123')
        self.stdout.write('- student@digichalk.local / demopassword123')
