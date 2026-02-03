import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import FetchJob, Proxy

class JobConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.job_id = self.scope['url_route']['kwargs']['job_id']
        self.job_group_name = f'job_{self.job_id}'

        # Join job group
        await self.channel_layer.group_add(
            self.job_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave job group
        await self.channel_layer.group_discard(
            self.job_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming messages if needed
        pass

    # Receive message from job group
    async def job_update(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

class StatsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.stats_group_name = 'stats'

        # Join stats group
        await self.channel_layer.group_add(
            self.stats_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial stats
        stats = await self.get_stats()
        await self.send(text_data=json.dumps(stats))

    async def disconnect(self, close_code):
        # Leave stats group
        await self.channel_layer.group_discard(
            self.stats_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def get_stats(self):
        total_proxies = Proxy.objects.count()
        working_proxies = Proxy.objects.filter(is_working=True).count()
        
        return {
            'total_proxies': total_proxies,
            'working_proxies': working_proxies,
            'success_rate': (working_proxies / total_proxies * 100) if total_proxies > 0 else 0
        }

    # Receive message from stats group
    async def stats_update(self, event):
        stats = event['stats']

        # Send stats to WebSocket
        await self.send(text_data=json.dumps(stats))