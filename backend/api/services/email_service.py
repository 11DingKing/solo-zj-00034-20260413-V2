import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from loguru import logger


class EmailService:
    @staticmethod
    def _get_smtp_config() -> dict:
        return {
            "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "from_email": os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USERNAME", "")),
            "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        }

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        config = EmailService._get_smtp_config()
        
        if not config["username"] or not config["password"]:
            logger.warning("SMTP credentials not configured. Email not sent.")
            logger.info(f"Would send email to {to_email}: {subject}")
            logger.info(f"HTML content: {html_content[:200]}...")
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = config["from_email"]
            msg["To"] = to_email
            msg["Subject"] = subject

            if text_content:
                part1 = MIMEText(text_content, "plain")
                msg.attach(part1)

            part2 = MIMEText(html_content, "html")
            msg.attach(part2)

            with smtplib.SMTP(config["host"], config["port"]) as server:
                if config["use_tls"]:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                
                server.login(config["username"], config["password"])
                server.sendmail(config["from_email"], to_email, msg.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def send_password_reset_email(
        to_email: str,
        reset_token: str,
        frontend_url: str = "http://localhost:5173",
    ) -> bool:
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        subject = "Password Reset Request"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4caf50;">Password Reset Request</h2>
                <p>Hello,</p>
                <p>You have requested to reset your password. Click the link below to set a new password:</p>
                <p style="margin: 20px 0;">
                    <a href="{reset_link}" 
                       style="display: inline-block; padding: 12px 24px; background-color: #4caf50; 
                              color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Reset Password
                    </a>
                </p>
                <p style="font-size: 14px; color: #666;">
                    If the button doesn't work, copy and paste this link into your browser:
                </p>
                <p style="font-size: 12px; word-break: break-all; color: #666; background: #f5f5f5; padding: 10px; border-radius: 5px;">
                    {reset_link}
                </p>
                <p style="margin-top: 20px; font-size: 14px; color: #666;">
                    <strong>Important:</strong> This link will expire in 15 minutes and can only be used once.
                </p>
                <p style="font-size: 14px; color: #666;">
                    If you didn't request this password reset, please ignore this email.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #999;">
                    This is an automated email, please do not reply.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        Hello,
        
        You have requested to reset your password. Use the link below to set a new password:
        
        {reset_link}
        
        Important: This link will expire in 15 minutes and can only be used once.
        
        If you didn't request this password reset, please ignore this email.
        
        This is an automated email, please do not reply.
        """
        
        return EmailService.send_email(to_email, subject, html_content, text_content)
