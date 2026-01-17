
from decouple import config
from datetime import datetime, timedelta, timezone
from jose import jwt
from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")


class Settings:
    JWT_SECRET: str = SECRET_KEY
    JWT_ALGORITHM: str = ALGORITHM
    EMAIL_VERIFY_EXPIRE_MINUTES: int = 30

    SMTP_EMAIL: str = "parashuramkalakutagi9@gmail.com"
    SMTP_PASSWORD: str = "rlcpskvqrkhuawap"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

settings = Settings()


def create_email_token(email: str):
    expire = datetime.now(timezone.utc) + ( timedelta(minutes=settings.EMAIL_VERIFY_EXPIRE_MINUTES))
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_email_token(token: str):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])



# async def send_verification_email(email: str, token: str):
#     verify_link = f"http://localhost:8000/verify-email?token={token}"
#
#     msg = MIMEText(f"Click the link to verify your email:\n{verify_link}")
#     msg["Subject"] = "Verify your Email"
#     msg["From"] = settings.SMTP_EMAIL
#     msg["To"] = email
#
#     with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
#         server.starttls()
#         server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
#         server.sendmail(settings.SMTP_EMAIL, email, msg.as_string())





async def send_verification_email(email: str, token: str):
    verify_link = f"http://localhost:8000/verify-email?token={token}"
    print(verify_link)

    # Beautiful HTML Email Template
    html_template = f"""
    <!DOCTYPE html>
    <html>
      <body style="margin:0; padding:0; background:#f4f6f9; font-family:'Segoe UI',Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
          <tr>
            <td align="center">

              <table width="600" cellpadding="0" cellspacing="0" 
                style="background:white; border-radius:16px; overflow:hidden;
                box-shadow:0 6px 25px rgba(0,0,0,0.08);">

                <!-- Header -->
                <tr>
                  <td align="center" style="background:#4f46e5; padding:30px;">
                    <h1 style="color:white; margin:0; font-size:28px; font-weight:600;">Welcome!</h1>
                    <p style="color:#e0e7ff; margin:8px 0 0 0; font-size:15px;">
                      Please verify your email address
                    </p>
                  </td>
                </tr>

                <!-- Body -->
                <tr>
                  <td style="padding:35px 40px;">
                    <h2 style="color:#111827; margin-top:0; font-size:22px;">Verify Your Email</h2>

                    <p style="color:#374151; font-size:16px; line-height:26px; margin:20px 0;">
                      Thank you for signing up! Click the button below to confirm your email address and activate your account.
                    </p>

                    <div style="text-align:center; margin:35px 0;">
                      <a href="{verify_link}" 
                        style="background:#4f46e5; padding:14px 34px; border-radius:10px;
                        color:white; text-decoration:none; font-size:17px; font-weight:600;
                        display:inline-block; letter-spacing:0.3px;">
                        Verify Email
                      </a>
                    </div>

                    <p style="color:#6b7280; font-size:14px; line-height:22px;">
                      If the button doesn’t work, click or copy the link below:
                    </p>

                    <p style="color:#4f46e5; font-size:14px; line-height:20px; word-break:break-all;">
                      {verify_link}
                    </p>
                  </td>
                </tr>

                <!-- Footer -->
                <tr>
                  <td align="center" 
                      style="background:#f9fafb; padding:25px; border-top:1px solid #e5e7eb;">
                    <p style="color:#9ca3af; font-size:13px; margin:0;">
                      © 2024 Your Company — All rights reserved
                    </p>
                  </td>
                </tr>

              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    # Build email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify Your Email"
    msg["From"] = settings.SMTP_EMAIL
    msg["To"] = email

    # Attach HTML Template
    msg.attach(MIMEText(html_template, "html"))

    # Send Email
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_EMAIL, email, msg.as_string())