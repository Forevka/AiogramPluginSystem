import asyncio
from datetime import datetime
import json
from multiprocessing import Pool, Process, Event
from uuid import UUID

import aio_pika
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.payload import (
    generate_payload, prepare_arg, prepare_attachment, prepare_file)
from loguru import logger
import time

class WorkerPool():
    def __init__(self, event_id: str, worker_count: int = 5, token: str = '', connection_string: str = ''):
        self.event_id = event_id
        self.worker_count = worker_count
        self.token = token
        self.connection_string = connection_string
        self.procs = []
        self.start_flag = Event()

    def up_workers(self,) -> bool:
        if self.procs:
            logger.warning('Can`t create new workers while old dont disposed')
            return False
        
        for i in range(0, self.worker_count, 1):
            p = Process(target=start_consumer, args = (i, self.event_id, self.connection_string, self.token,))
            p.start()
            logger.debug("worker {} - READY".format(i+1))
        time.sleep(5) # wait until all worker start
        return True
    
    def dispose_workers(self):
        logger.debug('start disposing workers')
        '''for wid, worker in self.worker_list.items():
            worker.terminate()
            logger.debug(f'disposed {wid} worker')'''
        logger.debug('succesfully disposed workers')
        

async def start(loop, my_id, event_id, connection_string, token,):
    print(f"[{my_id}] - starting worker")

    bot = Bot(token=token)

    connection = await aio_pika.connect_robust(
        connection_string, loop=loop,
    )

    channel = await connection.channel()
    queue = await channel.declare_queue(event_id, auto_delete=False)

    print(f'[{my_id}] - connected')

    print(f"[{my_id}] - run")
    async with connection:
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    now = datetime.now()
                    logger.debug(
                        f"[{my_id}] - Worker received at {now} - {message.body}")

                    body = json.loads(message.body)
                    if body['data'].get('end', False):
                        logger.debug(
                            f"[{my_id}] - Worker received END stopping.")
                        exit()
                    files = body.get('files')
                    if files:
                        files = {file["attach"]: types.InputFile(
                            file["file_name"]) for file in files}

                    await bot.request(body['method'],
                                    data=body['data'],
                                    files=files)
                    logger.debug(
                        f"[{my_id}] - Worker sent at {datetime.now()} time spend {datetime.now() - now}")


def start_consumer(my_id, event_id, connection_string, token,):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        start(loop, my_id, event_id, connection_string, token,)
    )
    loop.close()
