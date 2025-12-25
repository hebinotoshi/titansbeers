import hashlib
import hmac
import base64
from typing import Optional, Dict, Any
import requests

from .config import (
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_CHANNEL_SECRET,
    BEER_TRIGGERS,
    SIZE_TRIGGERS,
    STAFF_TRIGGERS,
    HAGEHIGE_TRIGGERS,
    YURIE_TRIGGERS,
    ADAM_TRIGGERS,
)
from .scraper import scrape_beers
from .flex_messages import (
    build_beer_carousel,
    build_size_message,
    build_staff_carousel,
    build_hagehige_carousel,
    build_personal_message,
)


LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"


def verify_signature(body: bytes, signature: str) -> bool:
    """Verify the Line webhook signature."""
    if not LINE_CHANNEL_SECRET:
        return True  # Skip verification if secret not set (dev mode)

    hash_value = hmac.new(
        LINE_CHANNEL_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()

    expected_signature = base64.b64encode(hash_value).decode("utf-8")
    return hmac.compare_digest(signature, expected_signature)


def handle_message(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Handle an incoming Line message event.
    Returns the flex message to reply with, or None.
    """
    message = event.get("message", {})
    if message.get("type") != "text":
        return None

    text = message.get("text", "").strip().lower()

    # Beer command - scrape on demand
    if text in BEER_TRIGGERS:
        beers = scrape_beers()
        if beers:
            return build_beer_carousel(beers)
        return None

    # Size command
    if text in SIZE_TRIGGERS:
        return build_size_message()

    # Staff command
    if text in STAFF_TRIGGERS:
        return build_staff_carousel()

    # Hagehige command
    if text in HAGEHIGE_TRIGGERS:
        return build_hagehige_carousel()

    # Yurie command
    if text in YURIE_TRIGGERS:
        return build_personal_message("yurie")

    # Adam command
    if text in ADAM_TRIGGERS:
        return build_personal_message("adam")

    return None


def reply_message(reply_token: str, message: Dict[str, Any]) -> bool:
    """Send a reply message via Line Messaging API."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }

    payload = {
        "replyToken": reply_token,
        "messages": [message],
    }

    try:
        response = requests.post(LINE_REPLY_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Error sending reply: {e}")
        return False


def process_webhook(body: Dict[str, Any]) -> None:
    """Process the webhook body and handle all events."""
    events = body.get("events", [])

    for event in events:
        if event.get("type") != "message":
            continue

        reply_token = event.get("replyToken")
        if not reply_token:
            continue

        response_message = handle_message(event)
        if response_message:
            reply_message(reply_token, response_message)
