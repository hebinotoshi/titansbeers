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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

# Command triggers
BEER_TRIGGERS = ["beer", "ビール", "びーる", "🍺", "🍻"]
SIZE_TRIGGERS = ["size", "サイズ"]
STAFF_TRIGGERS = ["staff"]
HAGEHIGE_TRIGGERS = ["hagehige"]
YURIE_TRIGGERS = ["yurie", "ゆりえ", "ユリエ"]
ADAM_TRIGGERS = ["adam", "アダム"]
MY_BEERS_TRIGGERS = ["my beers", "mybeers", "my list", "saved", "マイビール"]
