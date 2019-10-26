from datetime import datetime
import asyncio
from plugins.broadcasting.controllers.rmq_receiver import WorkerPool
from loguru import logger

from .db_controller import BroadcastingDBworker
from .rmq_controller import RabbitMQ


class EventMonitor:
    def __init__(self, db: BroadcastingDBworker, rmq: RabbitMQ, ):
        self.db: BroadcastingDBworker = db
        self.rmq: RabbitMQ = rmq
        self.user_list = (383492784, 383492784,
                          383492784, 383492784, 383492784)

    async def check_events(self):
        events = await self.db.get_latest_events()
        logger.info(events)
        if events:
            logger.info('Found events')
            for event in events:
                await self.rmq.create_queue(str(event.event_id))

                msgs = [
                        self.rmq.message_to_queue(data={
                            'chat_id': user_id,
                            'text': event.text
                        }, event_id = str(event.event_id)) for user_id in self.user_list
                    ]

                asyncio.gather(*msgs)

                


def create_event_monitor(db: BroadcastingDBworker, rmq: RabbitMQ, config: dict):
    monitor = EventMonitor(db, rmq)
    return monitor
