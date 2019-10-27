from datetime import datetime
import asyncio
from uuid import UUID
import aiohttp
from loguru import logger

from .db_controller import BroadcastingDBworker
from .rmq_controller import RabbitMQ


class EventMonitor:
    def __init__(self, db: BroadcastingDBworker, rmq: RabbitMQ, bot_token: str):
        self.db: BroadcastingDBworker = db
        self.rmq: RabbitMQ = rmq
        self.bot_token = bot_token
        self.user_list = (383492784, 383492784,
                          383492784, 383492784, 383492784)

    async def check_events(self):
        events = await self.db.get_latest_events()
        logger.info(events)
        if events:
            logger.info('Found events')
            for event in events:
                await self.rmq.create_queue(event.event_id)
                status = await self.start_new_pool(event.event_id)
                if status == 200:
                    msgs = [
                            self.rmq.message_to_queue(data={
                                'chat_id': user_id,
                                'text': event.text
                            }, event_id = str(event.event_id)) for user_id in self.user_list
                        ]

                    asyncio.gather(*msgs)
                elif status == 404:
                    logger.warning("RabbitMQ Worker service doesnt work")
                else:
                    logger.warning("Smth went wrong")
        

                
    
    async def _fetch(self, url, method, data={}):
        async with aiohttp.ClientSession() as session:
            try:
                if method == 'post':
                    async with session.post(url, json = data) as resp:
                        return resp.status
            except aiohttp.client_exceptions.ClientConnectorError:
                return 404

    async def start_new_pool(self, event_id: UUID, worker_count: int = 5,):
        data = {
            "token": self.bot_token,
            "connection_string": self.rmq.connection_string,
            "worker_count": worker_count
        }

        return await self._fetch(f'http://localhost:9999/pool/{event_id}', 'post', data = data)


                


def create_event_monitor(db: BroadcastingDBworker, rmq: RabbitMQ, config: dict):
    monitor = EventMonitor(db, rmq, config['bot_token'])
    return monitor
