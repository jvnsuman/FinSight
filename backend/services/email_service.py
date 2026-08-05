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


def send_login_alert_email(
    to_email: str,
    user_name: str,
    device_info: str | None,
    ip_address: str | None,
    reset_link: str | None = None,
) -> None:
    """
    Sends a login-alert email whenever a new session is created (Milestone 3 -
    session management / login alerts). If `reset_link` is provided, includes
    a direct "reset your password" link so the recipient can act immediately
    if this login wasn't them - resetting the password also logs out every
    other device (see reset_password in auth_service).
    Raises smtplib exception on failure - the caller (session_service) treats
    this as non-fatal and swallows it, since the in-app notification is the
    reliable channel and login shouldn't fail because SMTP hiccuped.
    """
    device_text = device_info or "an unknown device"
    location_text = f" (IP: {ip_address})" if ip_address else ""

    subject = "New login to your FinSight account"
    body_text = (
        f"Hi {user_name},\n\n"
        f"We noticed a new login to your FinSight account on {device_text}{location_text}.\n\n"
        f"If this was you, no action is needed.\n\n"
        f"If it wasn't you, please reset your password right away:\n"
        f"{reset_link or ''}\n\n"
        f"Resetting your password will also log you out of every other device, "
        f"and you can review or log out individual sessions any time from your "
        f"Profile page on FinSight.\n\n"
    )
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1E293B;">
        <h2 style="color: #028090;">New login to your FinSight account</h2>
        <p>Hi {user_name},</p>
        <p>We noticed a new login to your account:</p>
        <p style="background-color:#F7F9F8; border-radius:8px; padding:12px 16px; color:#1E293B;">
          <strong>Device:</strong> {device_text}<br/>
          {"<strong>IP address:</strong> " + ip_address + "<br/>" if ip_address else ""}
        </p>
        <p>If this was you, no action is needed.</p>
        <p style="color:#E0574B;">If it's not you, then please reset the password.</p>
        {f'''
        <p style="margin: 24px 0;">
          <a href="{reset_link}"
             style="background-color:#E0574B; color:#ffffff; padding:12px 24px;
                    text-decoration:none; border-radius:6px; display:inline-block;">
            Click here to reset the password
          </a>
        </p>
        <p>Or copy and paste this link into your browser:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        ''' if reset_link else ''}
        <p style="color:#64748B; font-size:13px;">
          Resetting your password will also log you out of every other device.
          You can also log out this specific device any time from your Profile
          page on the FinSight app - just open Profile → Active sessions.
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


def send_password_changed_email(to_email: str, user_name: str) -> None:
    """
    Sends a confirmation email whenever the account's password is changed -
    covers both the logged-in "change password" flow (auth_service.
    change_password) and the "forgot password" reset flow (auth_service.
    reset_password), since either one leaves the account with a new password
    and the owner should know either way.

    Deliberately doesn't include a reset link here (unlike the login alert):
    if this WASN'T the account owner, the safest next step is contacting
    support, since a same-flow reset link would just let whoever changed it
    lock the real owner out again. Raises smtplib exception on failure - both
    callers treat this as non-fatal and swallow it, same as the other
    account emails in this module.
    """
    subject = "Your FinSight password was changed"
    body_text = (
        f"Hi {user_name},\n\n"
        f"This is a confirmation that the password for your FinSight account was just changed.\n\n"
        f"If you made this change, no action is needed.\n\n"
        f"If you didn't change your password, your account may be compromised - "
        f"please contact support right away.\n\n"
    )
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1E293B;">
        <h2 style="color: #028090;">Your FinSight password was changed</h2>
        <p>Hi {user_name},</p>
        <p>This is a confirmation that the password for your FinSight account was just changed.</p>
        <p>If you made this change, no action is needed.</p>
        <p style="color:#E0574B;">If you didn't change your password, your account may be compromised - please contact support right away.</p>
        <p style="color:#64748B; font-size:13px;">
          You can review your account's active sessions any time from your
          Profile page on the FinSight app - just open Profile → Active sessions.
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


def send_account_deactivated_email(to_email: str, user_name: str, reason: str | None, purge_date) -> None:
    """
    Sends a detailed confirmation email when a user deactivates their own
    FinSight account (auth_service.deactivate_account). Unlike the shorter
    security emails in this module, this one is deliberately thorough since
    it's explaining a multi-step, delayed-deletion process the user needs to
    actually understand: what just happened, what's reversible and until
    when, what happens automatically after that, and how to get help if this
    wasn't intentional.

    purge_date is a datetime - the point after which the account and all its
    data (accounts, transactions, budgets, investments, goals, trades,
    sessions) are permanently and irreversibly deleted by
    account_cleanup_service.purge_expired_deleted_accounts.
    """
    purge_date_str = purge_date.strftime("%d %B %Y")
    reason_line_text = f"Reason given: {reason}\n\n" if reason else ""
    reason_line_html = f'<p style="color:#64748B;"><em>Reason given: {reason}</em></p>' if reason else ""

    subject = "Your FinSight account has been deactivated"
    body_text = (
        f"Hi {user_name},\n\n"
        f"We're confirming that your FinSight account was deactivated just now.\n\n"
        f"{reason_line_text}"
        f"What this means right now:\n"
        f"  - You've been logged out of every device, and your account can no longer be used to log in.\n"
        f"  - Nothing has been deleted yet. All of your data - accounts, transactions, budgets, "
        f"investments, goals, and trade history - is untouched and kept exactly as it was.\n\n"
        f"What happens next:\n"
        f"  - Your account will be permanently deleted on {purge_date_str} (30 days from today), "
        f"along with all the data listed above. This cannot be undone once it happens.\n"
        f"  - Until then, this is a grace period. If you'd like to keep your account, "
        f"contact support before {purge_date_str} and we can help you get back in.\n\n"
        f"If you didn't request this and believe your account was deactivated without your "
        f"permission, please contact support immediately so we can look into it before "
        f"the permanent deletion date.\n\n"
        f"We're sorry to see you go.\n"
    )
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #1E293B;">
        <h2 style="color: #028090;">Your FinSight account has been deactivated</h2>
        <p>Hi {user_name},</p>
        <p>We're confirming that your FinSight account was deactivated just now.</p>
        {reason_line_html}
        <h3 style="color:#0B2E33; font-size:15px;">What this means right now</h3>
        <ul>
          <li>You've been logged out of every device, and your account can no longer be used to log in.</li>
          <li>Nothing has been deleted yet. All of your data - accounts, transactions, budgets, investments, goals, and trade history - is untouched and kept exactly as it was.</li>
        </ul>
        <h3 style="color:#0B2E33; font-size:15px;">What happens next</h3>
        <ul>
          <li>Your account will be <strong>permanently deleted on {purge_date_str}</strong> (30 days from today), along with all the data listed above. This cannot be undone once it happens.</li>
          <li>Until then, this is a grace period. If you'd like to keep your account, contact support before {purge_date_str} and we can help you get back in.</li>
        </ul>
        <p style="color:#E0574B;">
          If you didn't request this and believe your account was deactivated without your permission,
          please contact support immediately so we can look into it before the permanent deletion date.
        </p>
        <p style="color:#64748B; font-size:13px;">We're sorry to see you go.</p>
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
