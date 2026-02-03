# backend/test_email.py
from email_service import EmailService

# Test sending email directly
result = EmailService.send_price_alert_email(
    to_email="kpraneethreddy333@gmail.com",
    user_name="Test User",
    product_name="Sony Bravia 55 inch 4K TV",
    model_id="TEST123",
    target_price=55000,
    current_price=49999,
    platform="Amazon"
)

print(f"Email sent: {result}")