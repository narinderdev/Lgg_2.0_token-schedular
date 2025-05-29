from apscheduler.schedulers.background import BackgroundScheduler
from token_manager import refresh_access_token
import asyncio

def start_scheduler(interval_seconds=82800):  # default to 23 hours
    scheduler = BackgroundScheduler()

    scheduler.add_job(lambda: asyncio.run(refresh_access_token()), 'interval', seconds=interval_seconds)
    
    scheduler.start()
    print(f"🔁 Scheduler started for refreshing token every {interval_seconds // 3600} hours ({interval_seconds} seconds).", flush=True)
