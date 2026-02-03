"""
Price Alert Engine
Checks prices and sends notifications
Run as: python alert_engine.py
Or schedule with cron/task scheduler
"""

import asyncio
from datetime import datetime, timezone
from sqlalchemy import text, and_
from sqlalchemy.orm import Session

from db import SessionLocal, engine
from models import PriceAlert, AlertNotification, User
from email_service import EmailService


class AlertEngine:
    """Price alert processing engine"""
    
    def __init__(self):
        self.db: Session = SessionLocal()
        self.alerts_checked = 0
        self.alerts_triggered = 0
        self.emails_sent = 0
    
    def close(self):
        self.db.close()
    
    def get_current_prices(self) -> dict:
        """Get current minimum prices for all products"""
        result = self.db.execute(text("""
            SELECT 
                model_id,
                MIN(sale_price) as min_price,
                (SELECT platform FROM tv_platform_latest_master t2 
                 WHERE t2.model_id = t.model_id 
                 ORDER BY sale_price ASC LIMIT 1) as best_platform,
                MIN(full_name) as product_name,
                MIN(product_url) as product_url
            FROM tv_platform_latest_master t
            WHERE sale_price > 0
            GROUP BY model_id
        """))
        
        prices = {}
        for row in result:
            prices[row.model_id] = {
                "min_price": float(row.min_price),
                "platform": row.best_platform,
                "product_name": row.product_name,
                "product_url": row.product_url
            }
        
        return prices
    
    def get_active_alerts(self):
        """Get all active alerts"""
        return self.db.query(PriceAlert).filter(
            PriceAlert.is_active == True
        ).all()
    
    def process_alert(self, alert: PriceAlert, price_data: dict):
        """Process a single alert"""
        self.alerts_checked += 1
        
        model_price = price_data.get(alert.model_id)
        if not model_price:
            return
        
        current_price = model_price["min_price"]
        
        # Update current price
        alert.current_price = current_price
        alert.last_checked_at = datetime.now(timezone.utc)
        
        # Check if price meets target
        if current_price <= alert.target_price:
            # Don't notify again for same price
            if alert.last_notified_price == current_price:
                return
            
            self.trigger_alert(alert, model_price)
    
    def trigger_alert(self, alert: PriceAlert, price_data: dict):
        """Trigger an alert and send notification"""
        self.alerts_triggered += 1
        
        # Update alert
        alert.is_triggered = True
        alert.trigger_count += 1
        alert.last_notified_at = datetime.now(timezone.utc)
        alert.last_notified_price = price_data["min_price"]
        
        # Get user
        user = self.db.query(User).filter(User.id == alert.user_id).first()
        if not user or not user.is_active:
            return
        
        # Create notification record
        notification = AlertNotification(
            alert_id=alert.id,
            user_id=alert.user_id,
            model_id=alert.model_id,
            target_price=alert.target_price,
            triggered_price=price_data["min_price"],
            platform=price_data["platform"]
        )
        self.db.add(notification)
        
        # Send email
        email_sent = self.send_alert_email(user, alert, price_data)
        notification.email_sent = email_sent
        if email_sent:
            notification.email_sent_at = datetime.now(timezone.utc)
            self.emails_sent += 1
    
    def send_alert_email(self, user: User, alert: PriceAlert, price_data: dict) -> bool:
        """Send price drop email"""
        return EmailService.send_price_alert_email(
            to_email=user.email,
            user_name=user.name,
            product_name=price_data["product_name"],
            model_id=alert.model_id,
            target_price=alert.target_price,
            current_price=price_data["min_price"],
            platform=price_data["platform"],
            product_url=price_data.get("product_url")
        )
    
    def run(self):
        """Run the alert engine"""
        print("\n" + "=" * 60)
        print("🔔 Starting Price Alert Engine")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Get current prices
            print("\n📊 Fetching current prices...")
            prices = self.get_current_prices()
            print(f"   Found prices for {len(prices)} products")
            
            # Get active alerts
            print("\n🔍 Fetching active alerts...")
            alerts = self.get_active_alerts()
            print(f"   Found {len(alerts)} active alerts")
            
            # Process each alert
            print("\n⚡ Processing alerts...")
            for alert in alerts:
                self.process_alert(alert, prices)
            
            # Commit changes
            self.db.commit()
            
            # Summary
            print("\n" + "=" * 60)
            print("✅ Alert Engine Complete!")
            print(f"   📋 Alerts checked: {self.alerts_checked}")
            print(f"   🎯 Alerts triggered: {self.alerts_triggered}")
            print(f"   📧 Emails sent: {self.emails_sent}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.db.rollback()
            raise
        finally:
            self.close()


def run_alert_engine():
    """Entry point for running alert engine"""
    engine = AlertEngine()
    engine.run()


if __name__ == "__main__":
    run_alert_engine()