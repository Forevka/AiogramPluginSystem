from datetime import datetime
import typing
import asyncio
from uuid import UUID
import aiohttp
from loguru import logger


from .db_controller import BroadcastingDBworker
from .rmq_controller import RabbitMQ


class EventMonitor:
    def __init__(self, db: BroadcastingDBworker, rmq: RabbitMQ, bot_token: str, rmq_workers_url: str,):
        self.db: BroadcastingDBworker = db
        self.rmq: RabbitMQ = rmq
        self.bot_token = bot_token
        self.rmq_workers_url = rmq_workers_url
        self.worker_count = 5
        self.user_list = (383492784, 383492784,
                          383492784, 383492784, 383492784)

    async def check_events(self):
        events = await self.db.get_latest_events()
        logger.info(events)
        if events:
            logger.info('Found events')
            for event in events:
                await self.rmq.create_queue(event.event_id)
                status = await self.start_new_pool(event.event_id, worker_count=self.worker_count)
                if status == 200:
                    msgs: typing.List = [
                            self.rmq.message_to_queue(data={
                                'chat_id': user_id,
                                'text': event.text
                            }, event_id = str(event.event_id)) for user_id in self.user_list
                        ]
                    # appending 5 stop msg for every worker
                    msgs.extend(
                        [
                            self.rmq.message_to_queue(data={
                                    'end': True
                                }, event_id = str(event.event_id)) for i in range(self.worker_count)
                        ]
                    )
                    # noqa
                    asyncio.gather(*msgs)
                    await self.db.update_event_status_by_id(event.event_id, 2, -1)
                elif status == 404:
                    logger.warning("RabbitMQ Worker service doesnt work")
                else:
                    logger.warning("Smth went wrong")
        
        #await asyncio.sleep(self.sleep_time, self.check_events())
                
    
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

        return await self._fetch(f'{self.rmq_workers_url}/pool/{event_id}', 'post', data = data)


                


def create_event_monitor(db: BroadcastingDBworker, rmq: RabbitMQ, config: dict):
    monitor = EventMonitor(db, rmq, config['bot_token'], config['rmq_workers_url'])
    return monitor
