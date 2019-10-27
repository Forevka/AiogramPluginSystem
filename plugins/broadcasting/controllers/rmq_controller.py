import json
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.bot import api
from aiogram.utils.payload import generate_payload, prepare_arg, prepare_attachment, prepare_file
from uuid import UUID

import aio_pika
import config
from loguru import logger

def convert_to_dict(key, obj):
    # Populate the dictionary with object meta data
    obj_dict = {
        "attach": key,
        "file_name": obj.file.name
    }

    return obj_dict

class RabbitMQ:
    def __init__(self, queue_name: str, connection_string: str,):
        self.connection_string = connection_string
        self.queue_name = queue_name
        self.queue = None
        self.connection = None
        self.channel = None
    
    async def connect(self,):
        self.connection = await aio_pika.connect_robust(self.connection_string)
        self.channel = await self.connection.channel()
        
    
    async def create_queue(self, event_id: UUID):
        self.queue = await self.channel.declare_queue(
            str(event_id), auto_delete=False
        )
    
    async def message_to_queue(self, event_id, method = 'sendMessage', data: dict = {}, files = {}, **kwargs):
        # Available methods
        # https://github.com/aiogram/aiogram/blob/dev-2.x/aiogram/bot/api.py#L146
        logger.debug(method)
        if files:
            files = [convert_to_dict(key, item) for key, item in files.items()]


        await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body = json.dumps({
                        'method': method,
                        'data': data,
                        'files': files
                    }).encode('utf-8')
                ),
                routing_key=event_id
            )
        return True