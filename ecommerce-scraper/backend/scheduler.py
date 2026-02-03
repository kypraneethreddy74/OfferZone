"""
Background Scheduler for Alert Engine
Runs alert checks every 30 minutes
"""

import schedule
import time
from datetime import datetime
from alert_engine import run_alert_engine


def job():
    """Scheduled job to run alert engine"""
    print(f"\n⏰ Scheduled run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        run_alert_engine()
    except Exception as e:
        print(f"❌ Scheduler error: {e}")


def run_scheduler():
    """Start the scheduler"""
    print("=" * 60)
    print("🚀 Starting OfferZone Alert Scheduler")
    print("   Running every 30 minutes")
    print("=" * 60)
    
    # Run immediately on start
    job()
    
    # Schedule to run every 30 minutes
    schedule.every(30).minutes.do(job)
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    run_scheduler()