"""
Email Service for OfferZone
Handles all email sending functionality
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class EmailConfig:
    """Email configuration from environment"""
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@offerzone.com")
    FROM_NAME: str = os.getenv("FROM_NAME", "OfferZone")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Feature flag - disable emails in development
    EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "False").lower() == "true"


class EmailService:
    """Email sending service"""
    
    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str, text_content: str = "") -> bool:
        """
        Send an email using SMTP
        Returns True if successful, False otherwise
        """
        if not EmailConfig.EMAIL_ENABLED:
            print(f"📧 [DEV MODE] Email would be sent to: {to_email}")
            print(f"   Subject: {subject}")
            print(f"   Content: {text_content[:200]}...")
            return True
        
        if not EmailConfig.SMTP_USER or not EmailConfig.SMTP_PASSWORD:
            print("⚠️ Email credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{EmailConfig.FROM_NAME} <{EmailConfig.FROM_EMAIL}>"
            msg["To"] = to_email
            
            # Attach both plain text and HTML versions
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            # Send email
            with smtplib.SMTP(EmailConfig.SMTP_HOST, EmailConfig.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailConfig.SMTP_USER, EmailConfig.SMTP_PASSWORD)
                server.sendmail(EmailConfig.FROM_EMAIL, to_email, msg.as_string())
            
            print(f"✅ Email sent successfully to: {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    @classmethod
    def send_verification_email(cls, to_email: str, user_name: str, token: str) -> bool:
        """Send email verification link"""
        verification_url = f"{EmailConfig.FRONTEND_URL}/verify-email?token={token}"
        
        subject = "Verify your OfferZone account"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                <!-- Header -->
                <tr>
                    <td style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 40px 30px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: 700;">OfferZone</h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 14px;">TV Price Intelligence Platform</p>
                    </td>
                </tr>
                
                <!-- Content -->
                <tr>
                    <td style="padding: 40px 30px;">
                        <h2 style="color: #0b1c2d; margin: 0 0 20px 0; font-size: 24px;">Welcome, {user_name}! 👋</h2>
                        <p style="color: #555555; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                            Thank you for signing up for OfferZone. To complete your registration and start tracking the best TV deals, please verify your email address.
                        </p>
                        
                        <!-- CTA Button -->
                        <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                                <td style="text-align: center; padding: 30px 0;">
                                    <a href="{verification_url}" 
                                       style="display: inline-block; background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); 
                                              color: #ffffff; text-decoration: none; padding: 16px 40px; 
                                              border-radius: 8px; font-size: 16px; font-weight: 600;
                                              box-shadow: 0 4px 15px rgba(255, 152, 0, 0.4);">
                                        ✓ Verify My Email
                                    </a>
                                </td>
                            </tr>
                        </table>
                        
                        <p style="color: #777777; font-size: 14px; line-height: 1.6; margin: 20px 0 0 0;">
                            Or copy and paste this link in your browser:
                        </p>
                        <p style="color: #ff9800; font-size: 14px; word-break: break-all; margin: 10px 0 0 0;">
                            {verification_url}
                        </p>
                        
                        <p style="color: #999999; font-size: 13px; margin: 30px 0 0 0;">
                            ⏰ This link will expire in 24 hours.
                        </p>
                    </td>
                </tr>
                
                <!-- Footer -->
                <tr>
                    <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #eeeeee;">
                        <p style="color: #999999; font-size: 13px; margin: 0 0 10px 0;">
                            If you didn't create an account, you can safely ignore this email.
                        </p>
                        <p style="color: #bbbbbb; font-size: 12px; margin: 0;">
                            © {datetime.now().year} OfferZone. All rights reserved.
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to OfferZone, {user_name}!
        
        Please verify your email address by clicking the link below:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, you can safely ignore this email.
        
        - The OfferZone Team
        """
        
        return cls._send_email(to_email, subject, html_content, text_content)
    
    @classmethod
    def send_password_reset_email(cls, to_email: str, user_name: str, token: str) -> bool:
        """Send password reset link"""
        reset_url = f"{EmailConfig.FRONTEND_URL}/reset-password?token={token}"
        
        subject = "Reset your OfferZone password"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                <!-- Header -->
                <tr>
                    <td style="background: linear-gradient(135deg, #0b1c2d 0%, #1a3a5c 100%); padding: 40px 30px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: 700;">OfferZone</h1>
                        <p style="color: rgba(255,255,255,0.7); margin: 10px 0 0 0; font-size: 14px;">Password Reset Request</p>
                    </td>
                </tr>
                
                <!-- Content -->
                <tr>
                    <td style="padding: 40px 30px;">
                        <h2 style="color: #0b1c2d; margin: 0 0 20px 0; font-size: 24px;">Hi {user_name},</h2>
                        <p style="color: #555555; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                            We received a request to reset your password. Click the button below to create a new password.
                        </p>
                        
                        <!-- CTA Button -->
                        <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                                <td style="text-align: center; padding: 30px 0;">
                                    <a href="{reset_url}" 
                                       style="display: inline-block; background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); 
                                              color: #ffffff; text-decoration: none; padding: 16px 40px; 
                                              border-radius: 8px; font-size: 16px; font-weight: 600;
                                              box-shadow: 0 4px 15px rgba(255, 152, 0, 0.4);">
                                        🔐 Reset Password
                                    </a>
                                </td>
                            </tr>
                        </table>
                        
                        <p style="color: #777777; font-size: 14px; line-height: 1.6; margin: 20px 0 0 0;">
                            Or copy and paste this link in your browser:
                        </p>
                        <p style="color: #ff9800; font-size: 14px; word-break: break-all; margin: 10px 0 0 0;">
                            {reset_url}
                        </p>
                        
                        <p style="color: #999999; font-size: 13px; margin: 30px 0 0 0;">
                            ⏰ This link will expire in 1 hour.
                        </p>
                        
                        <div style="background-color: #fff3cd; border-radius: 8px; padding: 15px; margin-top: 30px;">
                            <p style="color: #856404; font-size: 14px; margin: 0;">
                                ⚠️ If you didn't request a password reset, please ignore this email or contact support if you have concerns.
                            </p>
                        </div>
                    </td>
                </tr>
                
                <!-- Footer -->
                <tr>
                    <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #eeeeee;">
                        <p style="color: #bbbbbb; font-size: 12px; margin: 0;">
                            © {datetime.now().year} OfferZone. All rights reserved.
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        text_content = f"""
        Hi {user_name},
        
        We received a request to reset your password. Click the link below to create a new password:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request a password reset, please ignore this email.
        
        - The OfferZone Team
        """
        
        return cls._send_email(to_email, subject, html_content, text_content)
    
    @classmethod
    def send_verification_success_email(cls, to_email: str, user_name: str) -> bool:
        """Send confirmation that email was verified"""
        subject = "Email verified successfully! 🎉"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                <!-- Header -->
                <tr>
                    <td style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 40px 30px; text-align: center;">
                        <div style="font-size: 60px; margin-bottom: 10px;">✅</div>
                        <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">Email Verified!</h1>
                    </td>
                </tr>
                
                <!-- Content -->
                <tr>
                    <td style="padding: 40px 30px; text-align: center;">
                        <h2 style="color: #0b1c2d; margin: 0 0 20px 0; font-size: 24px;">Welcome aboard, {user_name}! 🚀</h2>
                        <p style="color: #555555; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                            Your email has been verified successfully. You now have full access to all OfferZone features:
                        </p>
                        
                        <!-- Features -->
                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 30px;">
                            <tr>
                                <td style="padding: 10px; text-align: left;">
                                    <p style="color: #28a745; font-size: 15px; margin: 0;">✓ Add products to your wishlist</p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; text-align: left;">
                                    <p style="color: #28a745; font-size: 15px; margin: 0;">✓ Set price drop alerts</p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; text-align: left;">
                                    <p style="color: #28a745; font-size: 15px; margin: 0;">✓ Get notified on best deals</p>
                                </td>
                            </tr>
                        </table>
                        
                        <!-- CTA Button -->
                        <a href="{EmailConfig.FRONTEND_URL}/best-deals" 
                           style="display: inline-block; background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); 
                                  color: #ffffff; text-decoration: none; padding: 16px 40px; 
                                  border-radius: 8px; font-size: 16px; font-weight: 600;
                                  box-shadow: 0 4px 15px rgba(255, 152, 0, 0.4);">
                            🛒 Start Shopping
                        </a>
                    </td>
                </tr>
                
                <!-- Footer -->
                <tr>
                    <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #eeeeee;">
                        <p style="color: #bbbbbb; font-size: 12px; margin: 0;">
                            © {datetime.now().year} OfferZone. All rights reserved.
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome aboard, {user_name}!
        
        Your email has been verified successfully. You now have full access to all OfferZone features:
        
        ✓ Add products to your wishlist
        ✓ Set price drop alerts
        ✓ Get notified on best deals
        
        Start shopping: {EmailConfig.FRONTEND_URL}/best-deals
        
        - The OfferZone Team
        """
        
        return cls._send_email(to_email, subject, html_content, text_content)
    
    @classmethod
    def send_password_changed_email(cls, to_email: str, user_name: str) -> bool:
        """Send confirmation that password was changed"""
        subject = "Your password has been changed"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                <!-- Header -->
                <tr>
                    <td style="background: linear-gradient(135deg, #0b1c2d 0%, #1a3a5c 100%); padding: 40px 30px; text-align: center;">
                        <div style="font-size: 60px; margin-bottom: 10px;">🔐</div>
                        <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">Password Changed</h1>
                    </td>
                </tr>
                
                <!-- Content -->
                <tr>
                    <td style="padding: 40px 30px;">
                        <h2 style="color: #0b1c2d; margin: 0 0 20px 0; font-size: 24px;">Hi {user_name},</h2>
                        <p style="color: #555555; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                            Your password has been successfully changed. You can now use your new password to log in.
                        </p>
                        
                        <div style="background-color: #f8d7da; border-radius: 8px; padding: 15px; margin-top: 20px;">
                            <p style="color: #721c24; font-size: 14px; margin: 0;">
                                ⚠️ If you didn't make this change, please contact our support team immediately or reset your password.
                            </p>
                        </div>
                        
                        <!-- CTA Button -->
                        <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                                <td style="text-align: center; padding: 30px 0;">
                                    <a href="{EmailConfig.FRONTEND_URL}/login" 
                                       style="display: inline-block; background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); 
                                              color: #ffffff; text-decoration: none; padding: 16px 40px; 
                                              border-radius: 8px; font-size: 16px; font-weight: 600;">
                                        Login to OfferZone
                                    </a>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                
                <!-- Footer -->
                <tr>
                    <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #eeeeee;">
                        <p style="color: #bbbbbb; font-size: 12px; margin: 0;">
                            © {datetime.now().year} OfferZone. All rights reserved.
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        text_content = f"""
        Hi {user_name},
        
        Your password has been successfully changed. You can now use your new password to log in.
        
        If you didn't make this change, please contact our support team immediately.
        
        - The OfferZone Team
        """
        
        return cls._send_email(to_email, subject, html_content, text_content)
        
        
    @classmethod
    def send_price_alert_email(
        cls,
        to_email: str,
        user_name: str,
        product_name: str,
        model_id: str,
        target_price: float,
        current_price: float,
        platform: str,
        product_url: str = None
    ) -> bool:
        """Send price drop alert email"""
        
        savings = target_price - current_price if target_price > current_price else 0
        product_link = product_url or f"{EmailConfig.FRONTEND_URL}/compare/{model_id}"
        unsubscribe_link = f"{EmailConfig.FRONTEND_URL}/alerts"
        
        subject = f"🎉 Price Drop Alert: {product_name[:50]}..."
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                <!-- Header -->
                <tr>
                    <td style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); padding: 40px 30px; text-align: center;">
                        <div style="font-size: 60px; margin-bottom: 10px;">🎉</div>
                        <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">Price Drop Alert!</h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Your target price has been reached</p>
                    </td>
                </tr>
                
                <!-- Content -->
                <tr>
                    <td style="padding: 40px 30px;">
                        <p style="color: #555555; font-size: 16px; margin: 0 0 20px 0;">
                            Hi {user_name}! Great news! 🎊
                        </p>
                        
                        <!-- Product Card -->
                        <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; margin-bottom: 24px;">
                            <h2 style="color: #0b1c2d; margin: 0 0 12px 0; font-size: 18px;">
                                {product_name}
                            </h2>
                            
                            <table width="100%" cellpadding="8" cellspacing="0">
                                <tr>
                                    <td style="color: #666;">Your Target:</td>
                                    <td style="text-align: right; font-weight: 600;">₹{target_price:,.0f}</td>
                                </tr>
                                <tr>
                                    <td style="color: #666;">Current Price:</td>
                                    <td style="text-align: right; font-weight: 700; color: #4caf50; font-size: 20px;">
                                        ₹{current_price:,.0f}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="color: #666;">Best Platform:</td>
                                    <td style="text-align: right; font-weight: 600; color: #ff9800;">
                                        {platform.upper()}
                                    </td>
                                </tr>
                                {'<tr><td style="color: #666;">You Save:</td><td style="text-align: right; font-weight: 600; color: #4caf50;">₹' + f"{savings:,.0f}" + '</td></tr>' if savings > 0 else ''}
                            </table>
                        </div>
                        
                        <!-- CTA Button -->
                        <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                                <td style="text-align: center; padding: 10px 0 30px 0;">
                                    <a href="{product_link}" 
                                       style="display: inline-block; background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); 
                                              color: #ffffff; text-decoration: none; padding: 16px 40px; 
                                              border-radius: 8px; font-size: 16px; font-weight: 600;
                                              box-shadow: 0 4px 15px rgba(255, 152, 0, 0.4);">
                                        🛒 Buy Now on {platform.upper()}
                                    </a>
                                </td>
                            </tr>
                        </table>
                        
                        <p style="color: #888; font-size: 13px; text-align: center; margin: 0;">
                            ⚡ Prices can change quickly. Don't miss out!
                        </p>
                    </td>
                </tr>
                
                <!-- Footer -->
                <tr>
                    <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #eeeeee;">
                        <p style="color: #999999; font-size: 13px; margin: 0 0 10px 0;">
                            <a href="{unsubscribe_link}" style="color: #ff9800; text-decoration: none;">
                                Manage your alerts
                            </a>
                            &nbsp;|&nbsp;
                            <a href="{EmailConfig.FRONTEND_URL}" style="color: #ff9800; text-decoration: none;">
                                Visit OfferZone
                            </a>
                        </p>
                        <p style="color: #bbbbbb; font-size: 12px; margin: 0;">
                            © {datetime.now().year} OfferZone. All rights reserved.
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        text_content = f"""
        Hi {user_name}! Great news!
        
        Price Drop Alert for: {product_name}
        
        Your Target: ₹{target_price:,.0f}
        Current Price: ₹{current_price:,.0f}
        Best Platform: {platform.upper()}
        {f"You Save: ₹{savings:,.0f}" if savings > 0 else ""}
        
        Buy now: {product_link}
        
        Manage alerts: {unsubscribe_link}
        
        - The OfferZone Team
        """
        
        return cls._send_email(to_email, subject, html_content, text_content)