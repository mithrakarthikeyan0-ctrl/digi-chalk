import pytest
import json
from channels.testing import WebsocketCommunicator
from config.asgi import application
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from accounts.models import User
from sessions.models import ClassSession
from schools.models import School
from academics.models import ClassRoom, Enrollment, StudentProfile

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestBoardConsumer:
    async def get_token(self, user):
        return str(AccessToken.for_user(user))

    async def test_websocket_unauthorized_rejection(self):
        # Without token, should be rejected if they try to send an event
        communicator = WebsocketCommunicator(application, "ws/sessions/fake-id/board/")
        connected, subprotocol = await communicator.connect()
        assert connected

        await communicator.send_json_to({"type": "stroke"})
        response = await communicator.receive_json_from()
        assert response["type"] == "error"
        assert response["message"] == "Must authenticate first"
        await communicator.disconnect()

    async def test_websocket_valid_auth(self, admin_user):
        school = await School.objects.acreate(name="WS School")
        classroom = await ClassRoom.objects.acreate(school=school, name="Class WS", grade_level=5)
        session = await ClassSession.objects.acreate(
            classroom=classroom,
            teacher=admin_user,
            status=ClassSession.Status.RECORDING
        )
        token = await self.get_token(admin_user)
        
        communicator = WebsocketCommunicator(application, f"ws/sessions/{session.id}/board/")
        connected, subprotocol = await communicator.connect()
        assert connected

        await communicator.send_json_to({
            "type": "authenticate",
            "token": token
        })
        
        response = await communicator.receive_json_from()
        assert response["type"] == "connected"
        assert response["role"] == admin_user.role
        
        await communicator.disconnect()
        
    async def test_teacher_can_broadcast_stroke(self, teacher_user):
        school = await School.objects.acreate(name="WS School")
        classroom = await ClassRoom.objects.acreate(school=school, name="Class WS", grade_level=5)
        session = await ClassSession.objects.acreate(
            classroom=classroom,
            teacher=teacher_user,
            status=ClassSession.Status.RECORDING
        )
        token = await self.get_token(teacher_user)
        
        communicator = WebsocketCommunicator(application, f"ws/sessions/{session.id}/board/")
        await communicator.connect()
        await communicator.send_json_to({"type": "authenticate", "token": token})
        await communicator.receive_json_from() # connected

        stroke_payload = {
            "type": "stroke",
            "strokeId": "s1",
            "points": [
                {"x": 10.5, "y": 20.0, "dt": 0.0, "color": "#ffffff"}
            ]
        }
        await communicator.send_json_to(stroke_payload)
        
        # Teacher should receive their own broadcast
        response = await communicator.receive_json_from()
        assert response["type"] == "stroke"
        assert response["strokeId"] == "s1"
        
        await communicator.disconnect()
        
    async def test_student_read_only(self, teacher_user, student_user):
        school = await School.objects.acreate(name="WS School")
        classroom = await ClassRoom.objects.acreate(school=school, name="Class WS", grade_level=5)
        profile = await StudentProfile.objects.acreate(user=student_user, school=school, admission_number="WS101")
        await Enrollment.objects.acreate(student=profile, classroom=classroom)
        
        session = await ClassSession.objects.acreate(
            classroom=classroom,
            teacher=teacher_user,
            status=ClassSession.Status.RECORDING
        )
        token = await self.get_token(student_user)
        
        communicator = WebsocketCommunicator(application, f"ws/sessions/{session.id}/board/")
        await communicator.connect()
        await communicator.send_json_to({"type": "authenticate", "token": token})
        await communicator.receive_json_from() # connected

        stroke_payload = {
            "type": "stroke",
            "strokeId": "s1",
            "points": [
                {"x": 10.5, "y": 20.0, "dt": 0.0, "color": "#ffffff"}
            ]
        }
        await communicator.send_json_to(stroke_payload)
        
        # Student shouldn't get their own broadcast back because they are read-only
        assert await communicator.receive_nothing()
        
        await communicator.disconnect()

    async def test_invalid_stroke_rejected(self, teacher_user):
        school = await School.objects.acreate(name="WS School")
        classroom = await ClassRoom.objects.acreate(school=school, name="Class WS", grade_level=5)
        session = await ClassSession.objects.acreate(
            classroom=classroom, teacher=teacher_user, status=ClassSession.Status.RECORDING
        )
        token = await self.get_token(teacher_user)
        
        communicator = WebsocketCommunicator(application, f"ws/sessions/{session.id}/board/")
        await communicator.connect()
        await communicator.send_json_to({"type": "authenticate", "token": token})
        await communicator.receive_json_from() # connected

        # Missing points
        stroke_payload = {
            "type": "stroke",
            "strokeId": "s1"
        }
        await communicator.send_json_to(stroke_payload)
        assert await communicator.receive_nothing()
        
        await communicator.disconnect()
