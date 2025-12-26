import requests
from typing import List, Dict

# Oracle Cloud scraper API
SCRAPER_API_URL = "http://159.13.59.218:5000"


def scrape_beers() -> List[Dict[str, str]]:
    """
    Fetch beer information from Oracle Cloud scraper API.
    Returns a list of beer dictionaries.
    """
    try:
        response = requests.get(SCRAPER_API_URL, timeout=30)
        response.raise_for_status()
        beers = response.json()
        print(f"Successfully fetched {len(beers)} beers from scraper API")
        return beers
    except Exception as e:
        print(f"Error fetching from scraper API: {e}")
        return []


def trim_string(s: str, max_length: int = 40) -> str:
    """Trim string and add ellipsis if too long."""
    s = s.replace("\r", " ").replace("\n", " ")
    if len(s) > max_length:
        return s[: max_length - 3] + "..."
    return s
