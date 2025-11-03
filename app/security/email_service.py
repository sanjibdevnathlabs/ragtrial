"""
Email service for sending verification and password reset emails.

Uses SMTP configuration from config.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import constants
from config import Config
from logger import get_logger

logger = get_logger(__name__)


class EmailService:
    """
    Service for sending emails.

    Handles:
    - Email verification emails
    - Password reset emails
    - SMTP connection management
    """

    def __init__(self):
        """Initialize email service with config."""
        self.config = Config()
        self.smtp_host = self.config.auth.email.smtp_host
        self.smtp_port = self.config.auth.email.smtp_port
        self.smtp_username = self.config.auth.email.smtp_username
        self.smtp_password = self.config.auth.email.smtp_password
        self.from_email = self.config.auth.email.from_email
        self.from_name = self.config.auth.email.from_name
        self.enabled = self.config.auth.email.enabled

    def send_email(
        self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None
    ) -> bool:
        """
        Send email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info("email_disabled", to=to_email, subject=subject)
            return True  # Return True in dev/test environments

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Attach text and HTML parts
            if text_body:
                msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info("email_sent", to=to_email, subject=subject)
            return True

        except Exception as e:
            logger.error(
                "email_send_failed",
                to=to_email,
                subject=subject,
                error=str(e),
                exc_info=True,
            )
            return False

    def send_verification_email(self, to_email: str, verification_token: str) -> bool:
        """
        Send email verification email.

        Args:
            to_email: User's email address
            verification_token: Verification token

        Returns:
            True if sent successfully, False otherwise
        """
        # TODO: Create proper email template
        verification_url = f"http://localhost:8000/api/v1/auth/verify-email?token={verification_token}"

        subject = "Verify your email address"
        
        html_body = f"""
        <html>
            <body>
                <h2>Welcome to RAG Trial!</h2>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_url}">Verify Email</a></p>
                <p>Or copy and paste this URL into your browser:</p>
                <p>{verification_url}</p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account, please ignore this email.</p>
            </body>
        </html>
        """

        text_body = f"""
        Welcome to RAG Trial!

        Please verify your email address by visiting:
        {verification_url}

        This link will expire in 24 hours.

        If you didn't create an account, please ignore this email.
        """

        return self.send_email(to_email, subject, html_body, text_body)

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """
        Send password reset email.

        Args:
            to_email: User's email address
            reset_token: Password reset token

        Returns:
            True if sent successfully, False otherwise
        """
        # TODO: Create proper email template
        reset_url = f"http://localhost:8000/api/v1/auth/reset-password?token={reset_token}"

        subject = "Reset your password"
        
        html_body = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You requested to reset your password. Click the link below to reset it:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>Or copy and paste this URL into your browser:</p>
                <p>{reset_url}</p>
                <p>This link will expire in 30 minutes.</p>
                <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
            </body>
        </html>
        """

        text_body = f"""
        Password Reset Request

        You requested to reset your password. Visit this URL to reset it:
        {reset_url}

        This link will expire in 30 minutes.

        If you didn't request this, please ignore this email and your password will remain unchanged.
        """

        return self.send_email(to_email, subject, html_body, text_body)

    def send_password_changed_notification(self, to_email: str) -> bool:
        """
        Send notification that password was changed.

        Args:
            to_email: User's email address

        Returns:
            True if sent successfully, False otherwise
        """
        subject = "Your password was changed"
        
        html_body = """
        <html>
            <body>
                <h2>Password Changed</h2>
                <p>Your password was successfully changed.</p>
                <p>If you didn't make this change, please contact support immediately.</p>
            </body>
        </html>
        """

        text_body = """
        Password Changed

        Your password was successfully changed.

        If you didn't make this change, please contact support immediately.
        """

        return self.send_email(to_email, subject, html_body, text_body)

