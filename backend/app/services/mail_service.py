"""
Email service — sends password reset emails via Gmail SMTP.
"""
import os
import smtplib
import secrets
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# In-memory store: {token: (user_id, expires_at)}
_reset_tokens: dict = {}
TOKEN_TTL = 3600  # 1 hour


def generate_reset_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    _reset_tokens[token] = (user_id, time.time() + TOKEN_TTL)
    return token


def verify_reset_token(token: str):
    entry = _reset_tokens.get(token)
    if not entry:
        return None
    user_id, expires_at = entry
    if time.time() > expires_at:
        del _reset_tokens[token]
        return None
    return user_id


def consume_reset_token(token: str):
    user_id = verify_reset_token(token)
    if user_id:
        _reset_tokens.pop(token, None)
    return user_id


def send_reset_email(to_email: str, reset_token: str) -> bool:
    mail_email    = os.getenv("MAIL_EMAIL", "").strip()
    mail_password = os.getenv("MAIL_PASSWORD", "").strip()
    if not mail_email or not mail_password:
        print("[Mail] MAIL_EMAIL or MAIL_PASSWORD not set")
        return False

    reset_url = f"http://127.0.0.1:3000?reset_token={reset_token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "LazyApply — Reset your password"
    msg["From"]    = mail_email
    msg["To"]      = to_email

    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px;">
      <h2 style="color:#6366f1;">LazyApply</h2>
      <p>You requested a password reset. Click the button below to set a new password.</p>
      <a href="{reset_url}"
         style="display:inline-block;background:#6366f1;color:#fff;padding:12px 24px;
                border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">
        Reset Password
      </a>
      <p style="color:#888;font-size:13px;">This link expires in 1 hour. If you didn't request this, ignore this email.</p>
    </div>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(mail_email, mail_password)
            server.sendmail(mail_email, to_email, msg.as_string())
        print(f"[Mail] Reset email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[Mail] Send error: {e}")
        return False
