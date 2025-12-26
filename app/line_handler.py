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
    MY_BEERS_TRIGGERS,
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
SCRAPER_API_URL = "http://159.13.59.218:5000"


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

    # My beers command
    if text in MY_BEERS_TRIGGERS:
        user_id = event.get("source", {}).get("userId", "")
        return get_saved_beers(user_id)

    return None


def get_saved_beers(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user's saved beers from Oracle API."""
    try:
        response = requests.get(f"{SCRAPER_API_URL}/mybeers/{user_id}", timeout=10)
        response.raise_for_status()
        beers = response.json()

        if not beers:
            return {
                "type": "text",
                "text": "You haven't saved any beers yet!\n\nType 'beer' to see the menu and save your favorites."
            }

        # Build carousel of saved beers
        bubbles = []
        for beer in beers[:10]:  # Limit to 10
            bubble = {
                "type": "bubble",
                "size": "kilo",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": beer.get("beer_name", "Unknown"),
                            "weight": "bold",
                            "size": "lg",
                            "wrap": True,
                        },
                        {
                            "type": "text",
                            "text": beer.get("brewery", ""),
                            "color": "#8c8c8c",
                            "size": "md",
                            "wrap": True,
                        },
                        {
                            "type": "text",
                            "text": beer.get("style", ""),
                            "size": "sm",
                            "wrap": True,
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"ABV: {beer.get('abv', '')}",
                                    "size": "xs",
                                },
                                {
                                    "type": "text",
                                    "text": f"Rating: {beer.get('rating', '')}",
                                    "size": "xs",
                                    "align": "end",
                                },
                            ],
                            "margin": "md",
                        },
                        {
                            "type": "text",
                            "text": f"Saved: {beer.get('saved_at', '')[:10]}",
                            "size": "xs",
                            "color": "#aaaaaa",
                            "margin": "md",
                        },
                    ],
                    "spacing": "sm",
                    "paddingAll": "13px",
                },
            }
            bubbles.append(bubble)

        return {
            "type": "flex",
            "altText": "⭐ Your Saved Beers",
            "contents": {"type": "carousel", "contents": bubbles},
        }

    except Exception as e:
        print(f"Error getting saved beers: {e}")
        return {
            "type": "text",
            "text": "Sorry, couldn't load your saved beers. Try again later."
        }


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


def handle_postback(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle postback events (button clicks)."""
    import json

    postback = event.get("postback", {})
    data_str = postback.get("data", "")

    try:
        data = json.loads(data_str)
    except json.JSONDecodeError:
        return None

    action = data.get("action")
    user_id = event.get("source", {}).get("userId", "")

    if action == "save_beer":
        beer_name = data.get("name", "Unknown")
        brewery = data.get("brewery", "")
        style = data.get("style", "")
        abv = data.get("abv", "")
        rating = data.get("rating", "")

        # Save to database via Oracle API
        try:
            save_response = requests.post(
                f"{SCRAPER_API_URL}/save",
                json={
                    "user_id": user_id,
                    "beer_name": beer_name,
                    "brewery": brewery,
                    "style": style,
                    "abv": abv,
                    "rating": rating,
                },
                timeout=10
            )
            save_response.raise_for_status()
            print(f"Saved beer '{beer_name}' for user {user_id}")
        except Exception as e:
            print(f"Error saving beer: {e}")
            return {
                "type": "text",
                "text": f"Sorry, couldn't save the beer. Try again later."
            }

        return {
            "type": "text",
            "text": f"⭐ Saved '{beer_name}' to your list!\n\nType 'my beers' to see your saved beers."
        }

    return None


def process_webhook(body: Dict[str, Any]) -> None:
    """Process the webhook body and handle all events."""
    import json
    print(f"=== WEBHOOK RECEIVED ===")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    print(f"========================")

    events = body.get("events", [])

    for event in events:
        event_type = event.get("type")
        reply_token = event.get("replyToken")

        if not reply_token:
            continue

        response_message = None

        if event_type == "message":
            response_message = handle_message(event)
        elif event_type == "postback":
            response_message = handle_postback(event)

        if response_message:
            reply_message(reply_token, response_message)
