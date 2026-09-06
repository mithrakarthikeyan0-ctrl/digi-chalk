import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User
from .models import ClassSession
from academics.models import Enrollment
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class BoardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'board_{self.session_id}'
        self.user = None
        
        # Accept connection first, but require an immediate auth message
        await self.accept()

    async def disconnect(self, close_code):
        if self.user:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get('type')
        
        # 1. Handle initial authentication
        if not self.user:
            if msg_type == 'authenticate':
                token = data.get('token')
                user = await self._authenticate_user(token)
                if not user:
                    await self.send(text_data=json.dumps({"type": "error", "message": "Invalid or expired token"}))
                    await self.close()
                    return
                
                # Check permissions
                has_perm = await self._check_session_permission(user, self.session_id)
                if not has_perm:
                    await self.send(text_data=json.dumps({"type": "error", "message": "Unauthorized for this session"}))
                    await self.close()
                    return
                
                self.user = user
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.send(text_data=json.dumps({"type": "connected", "role": self.user.role}))
            else:
                await self.send(text_data=json.dumps({"type": "error", "message": "Must authenticate first"}))
                await self.close()
            return

        # 2. Authorized user actions
        if self.user.role not in [User.Role.TEACHER, User.Role.ADMIN]:
            # Students are read-only
            return

        # Teacher commands
        if msg_type in ['stroke', 'bookmark_created', 'board_cleared', 'session_status']:
            # Validate stroke payload size and structure
            if msg_type == 'stroke':
                if not self._validate_stroke(data):
                    return
            
            # Broadcast to group
            data['type'] = msg_type  # Ensure type matches client expectation
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'board_message',
                    'message': data
                }
            )

    async def board_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def _authenticate_user(self, token_string):
        try:
            access_token = AccessToken(token_string)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None

    @database_sync_to_async
    def _check_session_permission(self, user, session_id):
        try:
            session = ClassSession.objects.get(id=session_id)
        except ClassSession.DoesNotExist:
            return False
            
        if user.role in [User.Role.ADMIN, User.Role.HEADMASTER]:
            return True
            
        if user.role == User.Role.TEACHER:
            return session.teacher_id == user.id
            
        if user.role == User.Role.STUDENT:
            return Enrollment.objects.filter(
                student__user=user, 
                classroom_id=session.classroom_id,
                active=True
            ).exists()
            
        return False

    def _validate_stroke(self, data):
        # Validate stroke ID
        if not data.get('strokeId'):
            return False
            
        # Validate points array
        points = data.get('points')
        if not points or not isinstance(points, list):
            return False
            
        # Limit payload size (e.g., max 500 points per chunk)
        if len(points) > 500:
            return False
            
        for pt in points:
            if not isinstance(pt.get('x'), (int, float)) or \
               not isinstance(pt.get('y'), (int, float)) or \
               not isinstance(pt.get('dt'), (int, float)):
                return False
            # Color should be string
            if not isinstance(pt.get('color'), str):
                return False
                
        return True
