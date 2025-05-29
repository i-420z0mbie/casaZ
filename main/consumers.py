import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import Message


User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return

        self.room_group_name = f'chat_user_{user.id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope['user']
        room_group = f'chat_user_{user.id}'
        await self.channel_layer.group_discard(room_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        recipient_id = data.get('recipient')
        content = data.get('content')

        sender = self.scope['user']
        if not sender.is_authenticated or not recipient_id or not content:
            return

        # Modified to include username in the saved message
        message = await database_sync_to_async(self.save_message)(
            sender.id, 
            recipient_id, 
            content,
            sender.username  # Pass username here
        )

        # Send message with username to recipient
        await self.channel_layer.group_send(
            f'chat_user_{recipient_id}',
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'sender': sender.id,
                    'sender_username': sender.username,  # Add username
                    'recipient': recipient_id,
                    'content': message.content,
                    'timestamp': str(message.timestamp),
                    'is_read': message.is_read,
                }
            }
        )

        # Also send confirmation to sender with username
        await self.send(text_data=json.dumps({
            'message': {
                'id': message.id,
                'sender': sender.id,
                'sender_username': sender.username,
                'recipient': recipient_id,
                'content': message.content,
                'timestamp': str(message.timestamp),
                'is_read': message.is_read,
            }
        }))

    # Modified save_message to accept username
    def save_message(self, sender_id, recipient_id, content, sender_username):
        sender = User.objects.get(id=sender_id)
        recipient = User.objects.get(id=recipient_id)
        return Message.objects.create(
            sender=sender,
            recipient=recipient,
            content=content,
            sender_username=sender_username  # Store username in message
        )


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return

        self.group_name = f'notifications_{user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event):
        # Send notification payload
        await self.send(text_data=json.dumps(event['data']))