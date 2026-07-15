"""Weekly digest email — build the message + send via SMTP.

Sender is injected so tests use `RecordingSender` and never hit real SMTP.
"""

from __future__ import annotations

import logging
import smtplib
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from typing import Protocol

from sqlmodel import Session, select

from app.core.config import get_settings
from app.models.preference import MediaType
from app.models.recommendation import Recommendation
from app.models.user import User

log = logging.getLogger("luminary.digest")
settings = get_settings()

DIGEST_WINDOW_DAYS = 7


class Sender(Protocol):
    def send(self, *, to: str, subject: str, html: str, text: str) -> None: ...


class SMTPSender:
    """Real SMTP sender — used in production."""

    def send(self, *, to: str, subject: str, html: str, text: str) -> None:
        if not settings.SMTP_HOST:
            log.warning("SMTP_HOST not configured; skipping email to %s", to)
            return
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.DIGEST_FROM_EMAIL
        msg["To"] = to
        msg.set_content(text)
        msg.add_alternative(html, subtype="html")

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
            s.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                s.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            s.send_message(msg)


class RecordingSender:
    """Test helper — collects sent messages instead of transmitting them."""

    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send(self, *, to: str, subject: str, html: str, text: str) -> None:
        self.sent.append({"to": to, "subject": subject, "html": html, "text": text})


# ---------- content ----------

def _picks_since_last_digest(session: Session, user: User) -> list[Recommendation]:
    cutoff = user.last_digest_sent_at or (datetime.now(UTC) - timedelta(days=DIGEST_WINDOW_DAYS))
    return list(session.exec(
        select(Recommendation)
        .where(Recommendation.user_id == user.id)
        .where(Recommendation.created_at >= cutoff)
        .order_by(Recommendation.created_at.desc())  # type: ignore[attr-defined]
        .limit(6)
    ))


def _render(user: User, picks: list[Recommendation]) -> tuple[str, str, str]:
    """Return (subject, html_body, text_body)."""
    subject = f"Your Luminary picks this week, {user.display_name.split()[0]}"

    if not picks:
        text = (
            f"Hi {user.display_name},\n\n"
            "No new picks this week — pop back in and try a section when you have a moment.\n\n"
            "— Luminary"
        )
        html = f"<p>Hi {user.display_name},</p><p>No new picks this week.</p>"
        return subject, html, text

    lines_text = [f"Hi {user.display_name},\n"]
    lines_html = [f"<p>Hi {user.display_name},</p>"]
    for p in picks:
        media_label = {MediaType.BOOK: "Book", MediaType.MOVIE: "Movie",
                       MediaType.ARTICLE: "Article"}[p.media_type]
        lines_text.append(f"[{media_label}] {p.title}\n{p.description[:200]}\n")
        lines_html.append(
            f"<p><strong>[{media_label}]</strong> {p.title}<br>"
            f"<span style='color:#6b6b6b'>{p.description[:200]}</span></p>"
        )
    lines_text.append("— Luminary")
    lines_html.append("<p>— Luminary</p>")
    return subject, "\n".join(lines_html), "\n".join(lines_text)


# ---------- job ----------

def send_weekly_digest(session: Session, *, sender: Sender | None = None) -> int:
    """Send one digest per opted-in user. Returns the number of emails sent."""
    if not settings.DIGEST_ENABLED:
        log.info("DIGEST_ENABLED is false; skipping digest run")
        return 0

    sender = sender or SMTPSender()

    users = list(session.exec(select(User).where(User.digest_opt_in == True)))  # noqa: E712
    sent_count = 0
    for user in users:
        picks = _picks_since_last_digest(session, user)
        subject, html, text = _render(user, picks)
        try:
            sender.send(to=user.email, subject=subject, html=html, text=text)
        except Exception as exc:  # noqa: BLE001
            log.warning("digest send to %s failed: %s", user.email, exc)
            continue
        user.last_digest_sent_at = datetime.now(UTC)
        session.add(user)
        sent_count += 1
    session.commit()
    return sent_count
