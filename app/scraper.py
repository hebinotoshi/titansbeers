import cloudscraper
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .config import UNTAPPD_VENUE_URL


def scrape_beers() -> List[Dict[str, str]]:
    """
    Scrape beer information from Untappd venue page.
    Returns a list of beer dictionaries.
    """
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'firefox',
                'platform': 'windows',
                'mobile': False
            }
        )
        response = scraper.get(UNTAPPD_VENUE_URL, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching Untappd page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    beer_elements = soup.select(".menu-section-list li")

    beers = []
    for beer in beer_elements:
        try:
            beer_info = _parse_beer_element(beer)
            if beer_info:
                beers.append(beer_info)
        except Exception as e:
            print(f"Error parsing beer element: {e}")
            continue

    return beers


def _parse_beer_element(beer) -> Optional[Dict[str, str]]:
    """Parse a single beer element and return beer info dict."""
    # Name and check-in link
    name_element = beer.select_one(".track-click")
    if not name_element:
        return None

    name = name_element.text.strip()
    href = name_element.get("href", "")
    check_in = f"https://untappd.com{href}" if href else ""

    # Strip leading number from name (e.g., "1. IPA Name" -> "IPA Name")
    if "." in name:
        name = name.split(".", 1)[1].strip()

    # Brewery
    brewery = ""
    h6_element = beer.find("h6")
    if h6_element:
        brewery_link = h6_element.find("a")
        if brewery_link:
            brewery = brewery_link.text.strip()

    # Style
    style = ""
    h5_element = beer.find("h5")
    if h5_element:
        style_em = h5_element.find("em")
        if style_em:
            style = style_em.text.strip()

    # ABV
    abv = ""
    if h6_element:
        abv_span = h6_element.find("span")
        if abv_span:
            abv_text = abv_span.text.strip()
            abv = abv_text.split("\n")[0].strip()

    # Label image
    label = ""
    label_div = beer.find("div", class_="beer-label")
    if label_div:
        img = label_div.find("img")
        if img:
            label = img.get("src", "")

    # Rating
    rating = ""
    rating_div = beer.find("div", class_="caps small")
    if rating_div:
        data_rating = rating_div.get("data-rating", "")
        if data_rating:
            try:
                rating = str(round(float(data_rating), 2))
            except ValueError:
                rating = data_rating

    return {
        "name": name,
        "brewery": brewery,
        "style": style,
        "abv": abv,
        "label": label,
        "rating": rating,
        "check_in": check_in,
    }


def trim_string(s: str, max_length: int = 40) -> str:
    """Trim string and add ellipsis if too long."""
    s = s.replace("\r", " ").replace("\n", " ")
    if len(s) > max_length:
        return s[: max_length - 3] + "..."
    return s
