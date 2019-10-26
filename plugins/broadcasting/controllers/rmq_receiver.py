import asyncio
from datetime import datetime
import json
from multiprocessing import Pool, Process
from uuid import UUID

import aio_pika
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.payload import (
    generate_payload, prepare_arg, prepare_attachment, prepare_file)
from loguru import logger

#import config


class WorkerPool():
    def __init__(self, worker_count: int = 5, token: str = '', connection_string: str = '', channel: str = ''):
        #self.event_id = str(event_id)
        self.worker_list = {}
        self.worker_count = worker_count
        self.token = token
        self.connection_string = connection_string
        self.channel = channel
        #self.up_workers()

    def up_workers(self, event_id: str,) -> bool:
        if self.worker_list:
            logger.warning('Can`t create new workers while old dont disposed')
            return False

        for i in range(0, self.worker_count, 1):
            p = Process(target=start_consumer, args = (i, event_id, self.token, self.connection_string,))
            p.start()
            self.worker_list[i]=p
            logger.debug("worker {} - READY".format(i+1))
        print(self.worker_list)
        return True
    
    def dispose_workers(self):
        logger.debug('start disposing workers')
        for wid, worker in self.worker_list.items():
            worker.terminate()
            logger.debug(f'disposed {wid} worker')
        logger.debug('succesfully disposed workers')


async def worker(loop, token, connection_string, my_id, event_id):
    print(f"[{my_id}] Starting worker")
    connection = await aio_pika.connect_robust(
        connection_string, loop=loop,
    )

    bot = Bot(token=token)

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Declaring queue if no exist
        queue = await channel.declare_queue(
            event_id, auto_delete=False
        )

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    now = datetime.now()
                    logger.debug(
                        f"[{my_id}] - Worker received at {now} - {message.body}")

                    body = json.loads(message.body)
                    files = body.get('files')
                    if files:
                        files = {file["attach"]: types.InputFile(
                            file["file_name"]) for file in files}

                    await bot.request(body['method'],
                                      data=body.get('data'),
                                      files=files)
                    logger.debug(
                        f"[{my_id}] - Worker sent at {datetime.now()} time spend {datetime.now() - now}")
                    #await asyncio.sleep(1)


def start_consumer(my_id: int, event_id: str, token: str, connection_string: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        worker(loop, token, connection_string, my_id, event_id)
    )
    loop.close()

if __name__ == '__main__':
    wp = WorkerPool(token='631844699:AAENUxQKbXeXMq1IVPKGuqL9JSPdWvRiJ90', connection_string='amqp://test:test@194.67.198.163', channel='')
    wp.up_workers(event_id='e42a62f3-6e17-4edd-b9be-5d0f6544e110')