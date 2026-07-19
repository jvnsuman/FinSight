"""
Email service - send real emails via SMTP (Gmail)
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.config import settings

def send_verification_email(to_email: str, user_name: str, token: str) -> None:
    """
    Sends an email containing a verification link.
    Raises smtplib exception on failure.
    """
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    subject = "Verify your FinSight account"
    body_text = (
        f"Hi {user_name},\n\n"
        f"Thanks for signing up for FinSight. Please verify your email by clicking the link below:\n\n"
        f"{verification_link}\n\n"
        f"This link expires in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES // 60} hours.\n\n"
        f"If you didn't create this account, you can safely ignore this email."
    )
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1E293B;">
        <h2 style="color: #028090;">Verify your FinSight account</h2>
        <p>Hi {user_name},</p>
        <p>Thanks for signing up for FinSight. Please verify your email address to activate your account:</p>
        <p style="margin: 24px 0;">
          <a href="{verification_link}"
             style="background-color:#02C39A; color:#ffffff; padding:12px 24px;
                    text-decoration:none; border-radius:6px; display:inline-block;">
            Verify Email
          </a>
        </p>
        <p>Or copy and paste this link into your browser:</p>
        <p><a href="{verification_link}">{verification_link}</a></p>
        <p style="color:#64748B; font-size:13px;">
          This link expires in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES // 60} hours.
          If you didn't create this account, you can safely ignore this email.
        </p>
      </body>
    </html>
    """
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message.attach(MIMEText(body_text, "plain"))
    message.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())

def send_password_reset_email(to_email: str, user_name: str, token: str) ->  None:
    """
    Sends an email containing a password reset link.
    Raised smtplib exception o failure.
    """
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    subject = "Reset your FinSight password"
    body_text = (
        f"Hi {user_name},\n\n"
        f"We received a request to reset your FinSight password. Click the link below to choose a new one:\n\n"
        f"{reset_link}\n\n"
        f"This link expires in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.\n\n"
        f"If you didn't request this, you can safely ignore this email - your password will not change."
    )
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1E293B;">
        <h2 style="color: #028090;">Reset your FinSight password</h2>
        <p>Hi {user_name},</p>
        <p>We received a request to reset your password. Click the button below to choose a new one:</p>
        <p style="margin: 24px 0;">
          <a href="{reset_link}"
             style="background-color:#02C39A; color:#ffffff; padding:12px 24px;
                    text-decoration:none; border-radius:6px; display:inline-block;">
            Reset Password
          </a>
        </p>
        <p>Or copy and paste this link into your browser:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p style="color:#64748B; font-size:13px;">
          This link expires in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.
          If you didn't request this, you can safely ignore this email - your password will not change.
        </p>
      </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message.attach(MIMEText(body_text, "plain"))
    message.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())
