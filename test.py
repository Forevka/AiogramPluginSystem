import asyncio
from plugins.ticket_system.ticket_system_config import config
from plugins.ticket_system.controllers.db_controller import create_db

async def main():
    db = await create_db(**config['db_ticket_settings'])
    t = await db.find_ticket('d1e5aa07-18f3-48e4-9392-0fe82469624d')
    print(t)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    