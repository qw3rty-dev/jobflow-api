import json
import asyncio

from pathlib import Path

from src.database import sessionLocal
from .notification_service import send_notifications

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

NOTIFICATION_INTERVAL = config["notification_interval"]


async def notification_worker():

    while True:
        db= sessionLocal()

        try:
            await asyncio.to_thread(send_notifications,db)
        except Exception as e:
            print("Notification worker error",e)
        finally:
           db.close()

        await asyncio.sleep(NOTIFICATION_INTERVAL)

