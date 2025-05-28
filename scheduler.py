from apscheduler.schedulers.background import BackgroundScheduler
from token_manager import refresh_access_token
import asyncio

def start_scheduler():
    scheduler = BackgroundScheduler()

    # Refresh every 23 hours (82800 seconds)
    scheduler.add_job(lambda: asyncio.run(refresh_access_token()), 'interval', seconds=82800)
    
    scheduler.start()
    print("🔁 Scheduler started for refreshing token every 23 hours.")
