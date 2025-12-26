import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re

# Venue URL for Titans Craft Beer Bar
VENUE_URL = "https://untappd.com/v/titans-craft-beer-bar-and-bottle-shop/5286704"


def scrape_beers() -> List[Dict[str, str]]:
    """
    Scrape beer information from Untappd venue page.
    Returns a list of beer dictionaries.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        session = requests.Session()
        response = session.get(VENUE_URL, headers=headers, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        beer_items = soup.select("li.menu-item")

        beers = []
        for item in beer_items:
            beer_info = _parse_html_beer(item)
            if beer_info:
                beers.append(beer_info)

        return beers

    except Exception as e:
        print(f"Error fetching Untappd page: {e}")
        return []


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
