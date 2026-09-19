import logging
from decimal import Decimal

from app.models.user import User
from app.services.email_service import send_email

logger = logging.getLogger("securebank.security")


def notify_login(
    user: User,
    device_fingerprint: str | None,
    trusted: bool,
    new_device: bool,
) -> None:
    """
    Sends a real email when a login comes from an untrusted/new device.
    Email failures are caught inside send_email and never raised here —
    a broken SMTP config must never block someone from logging in.
    """
    if trusted:
        return

    logger.warning(
        "Untrusted login | user_id=%s device_fingerprint=%s new_device=%s",
        user.id,
        device_fingerprint,
        new_device,
    )

    subject = "New sign-in to your SecureBank account"
    body = (
        f"Hi {user.full_name},\n\n"
        f"We noticed a sign-in to your SecureBank account from a device we "
        f"don't recognize as trusted.\n\n"
        f"Device fingerprint: {device_fingerprint or 'unknown'}\n"
        f"New device: {'yes' if new_device else 'no'}\n\n"
        f"If this was you, no action is needed — you can trust this device "
        f"from your account settings. If this wasn't you, please secure "
        f"your account immediately.\n\n"
        f"— SecureBank"
    )
    send_email(to_email=user.email, subject=subject, body=body)


def notify_transaction_approval_request(
    user_id: int,
    transaction_id: int,
    amount: Decimal,
    currency: str,
) -> None:
    """
    Placeholder for a real push notification (FCM/APNs) to the user's
    trusted device(s), asking them to approve/reject. No mobile app exists
    yet to receive it, so this just logs — swap for real push once Phase 5
    (Flutter app) exists and can register a device token to push to.
    """
    logger.info(
        "Push approval requested | user_id=%s transaction_id=%s amount=%s %s",
        user_id,
        transaction_id,
        amount,
        currency,
    )


def notify_transaction_decision(user_id: int, transaction_id: int, status: str) -> None:
    logger.info(
        "Transaction decided | user_id=%s transaction_id=%s status=%s",
        user_id,
        transaction_id,
        status,
    )