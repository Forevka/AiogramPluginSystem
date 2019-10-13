import asyncio
from config import db_ticket_settings
from controllers.db_controller import create_db

async def main():
    db = await create_db(**db_ticket_settings)
    t = await db.find_ticket("d82821cb-f17a-41f6-bb64-78a8f5b4538d")
    print(t)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    