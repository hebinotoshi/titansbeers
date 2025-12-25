import os
from dotenv import load_dotenv

load_dotenv()

# Line Bot Configuration
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")

# Untappd Configuration
UNTAPPD_VENUE_URL = "https://untappd.com/v/titans-craft-beer-bar-and-bottle-shop/5286704"

# HTTP Headers for scraping
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Command triggers
BEER_TRIGGERS = ["beer", "ビール", "びーる", "🍺", "🍻"]
SIZE_TRIGGERS = ["size", "サイズ"]
STAFF_TRIGGERS = ["staff"]
HAGEHIGE_TRIGGERS = ["hagehige"]
YURIE_TRIGGERS = ["yurie", "ゆりえ", "ユリエ"]
ADAM_TRIGGERS = ["adam", "アダム"]
