import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import os

# Venue URL for Titans Craft Beer Bar
VENUE_URL = "https://untappd.com/v/titans-craft-beer-bar-and-bottle-shop/5286704"

# Free proxy services to try
PROXY_SERVICES = [
    # WebScrapingAPI free tier
    "https://api.webscrapingapi.com/v1?api_key=free&url=",
    # AllOrigins (CORS proxy that also works for scraping)
    "https://api.allorigins.win/raw?url=",
    # corsproxy.io
    "https://corsproxy.io/?",
]


def scrape_beers() -> List[Dict[str, str]]:
    """
    Scrape beer information from Untappd venue page.
    Returns a list of beer dictionaries.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
    }

    # Try direct request first
    html_content = None

    # Try each proxy service
    for proxy_base in PROXY_SERVICES:
        try:
            proxy_url = f"{proxy_base}{VENUE_URL}"
            print(f"Trying proxy: {proxy_base[:40]}...")
            response = requests.get(proxy_url, headers=headers, timeout=20)
            if response.status_code == 200 and "menu-item" in response.text:
                html_content = response.text
                print(f"Success with proxy!")
                break
        except Exception as e:
            print(f"Proxy failed: {e}")
            continue

    # If all proxies fail, try direct (might work in some cases)
    if not html_content:
        try:
            print("Trying direct request...")
            response = requests.get(VENUE_URL, headers=headers, timeout=20)
            if response.status_code == 200:
                html_content = response.text
        except Exception as e:
            print(f"Direct request failed: {e}")

    if not html_content:
        print("All methods failed to fetch Untappd page")
        return []

    # Parse the HTML
    soup = BeautifulSoup(html_content, "html.parser")
    beer_items = soup.select("li.menu-item")

    beers = []
    for item in beer_items:
        beer_info = _parse_html_beer(item)
        if beer_info:
            beers.append(beer_info)

    return beers


def _parse_html_beer(item) -> Optional[Dict[str, str]]:
    """Parse beer from HTML li element."""
    try:
        # Beer name and link
        name_link = item.select_one("h5 a.track-click")
        if not name_link:
            return None

        name = name_link.text.strip()
        # Remove leading number (e.g., "1. Observable World" -> "Observable World")
        name = re.sub(r'^\d+\.\s*', '', name)

        href = name_link.get("href", "")
        check_in = f"https://untappd.com{href}" if href else "https://untappd.com"

        # Style
        style_em = item.select_one("h5 em")
        style = style_em.text.strip() if style_em else ""

        # Brewery
        brewery_link = item.select_one("h6 a.track-click")
        brewery = brewery_link.text.strip() if brewery_link else ""

        # ABV - extract from h6 span text
        h6 = item.select_one("h6")
        abv = ""
        if h6:
            h6_text = h6.get_text()
            abv_match = re.search(r'([\d.]+)%\s*ABV', h6_text)
            if abv_match:
                abv = f"{abv_match.group(1)}%"

        # Rating
        rating = ""
        rating_span = item.select_one("span.num")
        if rating_span:
            rating_text = rating_span.text.strip()
            rating = rating_text.strip("()")

        # Label image
        label = ""
        img = item.select_one(".beer-label img")
        if img:
            label = img.get("src", "")

        return {
            "name": name,
            "brewery": brewery,
            "style": style,
            "abv": abv,
            "label": label,
            "rating": rating,
            "check_in": check_in,
        }
    except Exception as e:
        print(f"Error parsing beer: {e}")
        return None


def trim_string(s: str, max_length: int = 40) -> str:
    """Trim string and add ellipsis if too long."""
    s = s.replace("\r", " ").replace("\n", " ")
    if len(s) > max_length:
        return s[: max_length - 3] + "..."
    return s
