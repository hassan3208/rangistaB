# import os
# import smtplib
# from email.message import EmailMessage
# import pathlib
# import logging

# GMAIL_USER = os.getenv("GMAIL_USER")
# GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")

# # Set up logging
# logger = logging.getLogger(__name__)

# def send_welcome(to_email: str, to_name: str):
#     if not GMAIL_USER or not GMAIL_APP_PASS:
#         logger.error("GMAIL_USER or GMAIL_APP_PASS not set")
#         return  # Let signup proceed without failing

#     msg = EmailMessage()
#     msg["Subject"] = "Welcome to Rangista — Thanks for signing up!"
#     msg["From"] = f"Rangista <{GMAIL_USER}>"
#     msg["To"] = to_email

#     # Load HTML template, inject name, and set plain-text fallback
#     template_path = pathlib.Path(__file__).with_name("welcome.html")
#     try:
#         html_content = template_path.read_text(encoding="utf-8")
#         html_rendered = html_content.replace("{{user_name}}", to_name)
#     except Exception as e:
#         logger.warning(f"Failed to load welcome.html: {e}")
#         html_rendered = f"<p>Hi {to_name},</p><p>Welcome to Rangista! We're glad you joined.</p><p>— Team Rangista</p>"

#     # Plain text fallback
#     plain_text = f"Hi {to_name},\n\nWelcome to Rangista! We're glad you joined.\n\n— Team Rangista"
#     msg.set_content(plain_text)
#     msg.add_alternative(html_rendered, subtype="html")

#     # Connect to Gmail SMTP with STARTTLS
#     try:
#         with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
#             smtp.ehlo()
#             smtp.starttls()
#             smtp.ehlo()
#             smtp.login(GMAIL_USER, GMAIL_APP_PASS)
#             smtp.send_message(msg)
#         logger.info(f"Welcome email sent to {to_email}")
#     except (smtplib.SMTPException, ConnectionError, TimeoutError) as e:
#         logger.error(f"Failed to send welcome email to {to_email}: {e}")
#         # Don't raise, let signup succeed












import os
import smtplib
from email.message import EmailMessage
import logging

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")

# Set up logging
logger = logging.getLogger(__name__)

def send_welcome(to_email: str, to_name: str):
    if not GMAIL_USER or not GMAIL_APP_PASS:
        logger.error("GMAIL_USER or GMAIL_APP_PASS not set")
        return  # Let signup proceed without failing

    msg = EmailMessage()
    msg["Subject"] = f"Hey {to_name}, Welcome to Rangista!"
    msg["From"] = f"Rangista <{GMAIL_USER}>"
    msg["To"] = to_email

    # Plain text content with humanized tone and social media links
    plain_text = f"""Hi {to_name},

So happy you're here! Welcome to Rangista, where we pour love into creating handmade, hand-painted clothes just for you. Ready to dive in? You can check out our latest collections, pick your favorite pieces, and order with ease at https://rangistawebsite.vercel.app.

A few things to get you started:
- Browse our newest designs
- Save the pieces you love
- Shop worry-free with secure payment options

Got questions? Just email us at rangistaarttowear@gmail.com or ping us on WhatsApp at +92 324 0405762. We're here to help!

Stay connected with us:
WhatsApp: https://wa.me/923240405762
Instagram: https://www.instagram.com/_rangista/
Facebook: https://www.facebook.com/p/Rangista-100065230491278/

Thanks for joining our little community!
Team Rangista
© 2025 Rangista — Art to Wear. All rights reserved.
https://rangistawebsite.vercel.app"""

    msg.set_content(plain_text)

    # Connect to Gmail SMTP with STARTTLS
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(GMAIL_USER, GMAIL_APP_PASS)
            smtp.send_message(msg)
        logger.info(f"Welcome email sent to {to_email}")
    except (smtplib.SMTPException, ConnectionError, TimeoutError) as e:
        logger.error(f"Failed to send welcome email to {to_email}: {e}")
        # Don't raise, let signup succeed