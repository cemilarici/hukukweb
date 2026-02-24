from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger(__name__)


def smtp_configured() -> bool:
    return all([settings.smtp_host, settings.smtp_user, settings.smtp_pass, settings.smtp_from, settings.smtp_to])


def send_contact_notification(subject: str, body: str) -> None:
    if not smtp_configured():
        logger.info("SMTP not configured. Email payload: %s | %s", subject, body)
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = settings.smtp_to
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(msg)
