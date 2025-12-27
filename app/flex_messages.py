import json
import os
from typing import List, Dict, Any
from .scraper import trim_string

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Titans logo URL
TITANS_LOGO = "https://obs.line-scdn.net/0hMJn8lgocEmVTQQaKOTRtMgMcGQdgIwxucXUGAnQ-KQg4IyxMJltfYDI9Ogw4CgpPZ3cCc3c6EzV2Ix1Yb0Y4d3U-NSohGlZYN3cWdDcqByUiITAzKA/f256x256"


def load_json_data(filename: str) -> Any:
    """Load JSON data from the data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        return None


def build_beer_carousel(beers: List[Dict[str, str]]) -> Dict[str, Any]:
    """Build a Flex Message carousel for beers."""
    bubbles = []

    for beer in beers:
        # Create postback data for saving beer
        save_data = json.dumps({
            "action": "save_beer",
            "name": beer.get("name", ""),
            "brewery": beer.get("brewery", ""),
            "style": beer.get("style", ""),
            "abv": beer.get("abv", ""),
            "rating": beer.get("rating", ""),
            "label": beer.get("label", ""),
        })

        bubble = {
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "image",
                "url": beer.get("label", ""),
                "size": "full",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": trim_string(beer.get("name", "Unknown")),
                        "weight": "bold",
                        "size": "lg",
                        "wrap": True,
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": beer.get("brewery", ""),
                                        "wrap": True,
                                        "color": "#8c8c8c",
                                        "size": "md",
                                        "flex": 5,
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "type": "text",
                        "text": beer.get("style", ""),
                        "size": "md",
                    },
                    {
                        "type": "text",
                        "text": f"ABV: {beer.get('abv', '')}",
                        "size": "xs",
                    },
                    {
                        "type": "text",
                        "text": f"Rating: {beer.get('rating', '')}",
                        "color": "#8c8c8c",
                        "size": "xs",
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "Check-in on Untappd",
                            "uri": beer.get("check_in", "https://untappd.com"),
                        },
                        "gravity": "bottom",
                        "height": "sm",
                    },
                ],
                "spacing": "sm",
                "paddingAll": "13px",
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "⭐ Save to My List",
                            "data": save_data,
                            "displayText": f"Saving {trim_string(beer.get('name', ''), 20)}...",
                        },
                        "style": "primary",
                        "color": "#FFC107",
                        "height": "sm",
                    }
                ],
            },
            "styles": {
                "header": {"separator": False},
                "footer": {"separator": True},
            },
        }
        bubbles.append(bubble)

    return {
        "type": "flex",
        "altText": "🍺 Drink like a Titan! Ciao",
        "contents": {"type": "carousel", "contents": bubbles},
    }


def build_size_message() -> Dict[str, Any]:
    """Build the drink size Flex Message."""
    size_data = load_json_data("size_images.json")
    if not size_data:
        size_data = {
            "small": "https://lh3.googleusercontent.com/7FddvFDORagopqYcXzDvBZgIGAEPfMTztMQyj6BlxNyw3G0XzJHUXI40R1bw4VjhTA_vpov8JnizxwnbnamwGqITJpGnVhPb4_ZCPZrst6gPEw5DNEw2USbus7nran2y0C969wWcqGFf7DJRrvfDXzu6iIFqr3EU6cGrUf8BLDK_BasIuSvhdTvy8mC62-M6chgVsmWe7jwv8cADQ1lm8wo8OZFrIb_iSn4TW2fshA5QuUSK0sYvKU_HJ0-qWVs4_J-Et5IPqdpLmZTZsrZx1K251ac8eT7_kxkuU5s6sNbdHHonMCZ0FbRBO2pM5Ip_W2spLp3fmZiJ0IqbJSoOi-RsBtlZrBnv4_MkMwuVlw_zICcBY6ARbX6gdYWXY1jFqm7xrBun0JkhVxbWiMuVQaIKBT6RqAqDNECuiEX_HqVHRQTPAU2vv1bNsxM-KKDNgwjp3CNB36tX7027eot2X9JtE8yRBpicmfNmKuiic_MDUdVCMyj3_PzWAnuJhjLWzsjqNUZ5bfjYI-P9WVIOKJb_trutnB7yvXEZmZx7FXCxoYFeArYE6__F8dhs1ROauAAtJ2MeooAYGeyHMyDhwpct71vbpi6BwHQpzRybrfIAVSHMAT3SjaROTgrATRR2D6yLgWcs4R1D0X5QVcaECgtrF9tLdRPBP98gOYMPetPVLxSSlCYnzonM8ig7OWfVtX0dY6DxhvGi3Pe5Kw5P71rpn6r8mfkgnOxnmnhCXBW16O0y564tOEglolJnRpigAvCZ6imtceL2Ae7P3PKn8ZEvjPHZvYp2sIcN_u73ZKCY8nyK_stFJ6v_dT-RGQj-5pD_KNZgmVkxZbUYwv875SNrsjTdxxyTWrd9qGjhzMo8qceg7XinZeoszcy2G4ZDf_2GD2n6zCZUCZWdcvsQqboKIMHoPJrXqbayHwVMZFg=w1006-h1424-s-no?authuser=0",
            "goblet": "https://lh3.googleusercontent.com/WVnbgPIcH2tZ1s7QHH5_I4uYyPGWTPy0YQ-O5ZEEuPIdCX6OtbkVjRP_OK9dnQTNDsYR_Pl5gyawqcZhhGwj7tIgpE5KN-_qeAoabB7B-Lz0GrWqQuDOnTBBOQyxMA5Nb-l4H8QfNYXIciCm2o2RFQNi_R52Xgki9QJFwNDKuhD9lSWrOQPLt2huHVUCUXU-A3gvNmvim94TMPukJ9Tr-97xz93rHUNMGsOsVuPJD2aHx7s6sxuujW_zQIVuCgpXtd5pBjjQvXrB4J-rxGJ8kD8HoGnB4s6_gn-T4iO4Vl6LBSB9DAxMzH_1pxNvoSMEt1PDUWJv7cn8xq_w-2QysmDgPc3C3godwN-iZbNePdUv3W2rnWt6B0l50epniVjS_0woFbnYTM_W1j7jgkNqqgsW6jJWAR9arFUuyd8A2kOcTY87pI4j_9hWFCRTPmk9WDPnZ0v8ezMGj6-Hi5GY4KxzPuMqX5GmGLWrRoiD-NUOLZ7IzEByYIic9EK5FchbWEd618z0mIoDBMq4TBPMSDEpttTSJ47_tm0_uao-rOHtoTFQedFG8V91JwAuxoqVvmOXOMjup4pF1UwIDuME4Cd3c64RvW8sAnD7cBh6NIzBfszmFb3oqto4Zg-TMWlqbUTK78_PGc9DH4TZeVTUY9tvV-g0BNKyj3TvK_Ezu3dU467VyQ14SbjkubhBwMvQeOT3H8wWX2rURfKj6YdAh6cEb_OpYL4ZgqZURx67Ap54H2sC-_Li3Z7bLshRZYma-YbnfzWcbz33iqfOczYxrLtkXmQQmxzOKmf-qj72UVWUYaeM0PIvccC-21rL34gaYi_qTfw5FUyhwsnjgr6fmrRuIDdnVz62gC9uiHXox2ceAErCXHOTpBnYYeeRU4I9jJkHr4KOSK5-_a_6_CiXzJ73TZ4wNkZMkiMCVlgPBec=w1006-h1424-s-no?authuser=0",
            "titan": "https://lh3.googleusercontent.com/7gOGGHrjJ8tGZpt49jAOfvDWS3TEXJmTryDRE2Init8JNf1Uh5br5rQxo4SM2-AppdU2REAJw_OJyiIiSSwLGUClFwqo9EPySrEO1c98K6KfBFyeMvigbAVYiSD1YEj1YdTd9pSnC_0Qz8mMT1TEegQmaDrjnnyZAnoGZr47oFCFJ4tLgsHuBkicr7PBHqb7M7bV9PgRgGXgQFdB4bCuU_NE53lYegaUuuFquoMruFmzYIG5Y71DQ-qVSi6Vd-Wl85K0XTaQHoIxJFHPCPR4sSB6uLoSJTfXrC08lD_hlprIRdC18C1m0cQvsMKOFeeevS9QjCK1QCi8sAWxrbCBCYZrnp0d39oRtsOOLhN0IUkQTK5wDJWedpnWX1Twl4f0xxBGy02Zoht-iV2UYvgPxZjZgDVN0wTswm9RVdPAkEQhepEiwYPY81Z3JKNeRqOdVYNy1UB5lHf18PhQ9HJJHUCgefsYUiBTDd6l2D5ZUh49ND5MM3qkKxRMQlFLVuBHwJniTZS6oGvooPWIm8QgKjEXG-xviWKq8doxsFiP7IBNz7RBWPbgoas_aNDplCVjT9pXdWm4PCO7SnlQEFehZpgF2HXz1XMfiXFQGeGFsJAMd9GBIQZXtjPTzoCuDN1mePxP27lcsWj6kYf85fu_2YkUvtTP5CrPPV4n13mTzjisyqdD2Ll-I5fEahDpMX80EZIo-5kuIp83wPEZpEGhV6lS7vFBIifx1hF_usKp7onLgsXAe60ug_wZH27D7TJ969zWrErQF3OWAsoCrRAmsovjkl1hphJRGXwB7eF56Ken8HUM8xEhepjUvinqoMXmIL4ON9l-7mE_Ur_ig-xYfEisOhTdRtd1H-U16cZZkV8osEIrvlhmjrHP4hVfPp5ojpW7ZhWUjU8bWpdJL74RPxWdt5dF1VffAYlNmmAi1bc=w1006-h1424-s-no?authuser=0",
        }

    return {
        "type": "flex",
        "altText": "How thirsty are you today?",
        "contents": {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "image", "url": TITANS_LOGO, "size": "xs"},
                    {
                        "type": "text",
                        "text": "How thirsty are you today?",
                        "weight": "bold",
                        "size": "md",
                        "margin": "md",
                        "align": "center",
                    },
                    {"type": "separator", "margin": "xxl"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xxl",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {"type": "text", "text": "Small", "size": "md", "color": "#555555", "align": "center"},
                                    {"type": "text", "text": "Goblet", "align": "center"},
                                    {"type": "text", "text": "Titan", "align": "center"},
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {"type": "image", "url": size_data["small"], "gravity": "center"},
                                    {"type": "separator", "margin": "sm"},
                                    {"type": "image", "url": size_data["goblet"], "gravity": "center"},
                                    {"type": "separator", "margin": "sm"},
                                    {"type": "image", "url": size_data["titan"], "gravity": "center"},
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {"type": "text", "text": "200ml", "align": "center"},
                                    {"type": "text", "text": "340ml", "align": "center"},
                                    {"type": "text", "text": "710ml", "align": "center"},
                                ],
                            },
                        ],
                    },
                    {"type": "separator", "margin": "xxl"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": "Thanks for using me! Happy Friday",
                                "size": "xs",
                                "color": "#aaaaaa",
                                "flex": 0,
                            }
                        ],
                    },
                ],
            },
            "styles": {"footer": {"separator": True}},
        },
    }


def build_staff_carousel() -> Dict[str, Any]:
    """Build the staff carousel Flex Message."""
    staff_data = load_json_data("staff.json")
    if not staff_data:
        staff_data = []

    bubbles = []
    for staff in staff_data:
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "image", "url": TITANS_LOGO, "size": "xs"},
                    {
                        "type": "text",
                        "text": staff.get("name", ""),
                        "weight": "bold",
                        "size": "md",
                        "margin": "md",
                        "align": "center",
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xxl",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "image",
                                "url": staff.get("image", ""),
                                "size": "xxl",
                                "animated": False,
                                "aspectMode": "cover",
                            }
                        ],
                        "cornerRadius": "20px",
                        "action": {"type": "postback", "label": "action", "data": "hello"},
                    },
                    {"type": "separator", "margin": "xxl"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": "Thanks for using me! Happy Friday",
                                "size": "xs",
                                "color": "#aaaaaa",
                                "flex": 0,
                            }
                        ],
                    },
                ],
            },
            "styles": {"footer": {"separator": True}},
        }
        bubbles.append(bubble)

    return {
        "type": "flex",
        "altText": "We are Titans!",
        "contents": {"type": "carousel", "contents": bubbles},
    }


def build_hagehige_carousel() -> Dict[str, Any]:
    """Build the hagehige beers carousel Flex Message."""
    hagehige_data = load_json_data("hagehige.json")
    if not hagehige_data:
        hagehige_data = []

    bubbles = []
    for beer in hagehige_data:
        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "image",
                        "url": "https://assets.untappd.com/site/brewery_logos_hd/brewery-520788_c80d1_hd.jpeg",
                        "backgroundColor": "#000000",
                        "size": "xs",
                    }
                ],
            },
            "hero": {
                "type": "image",
                "url": beer.get("image", ""),
                "size": "4xl",
                "aspectMode": "fit",
                "backgroundColor": "#000000",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": beer.get("name", ""),
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True,
                        "color": "#FFFFFF",
                        "align": "center",
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [],
                            }
                        ],
                    },
                ],
                "backgroundColor": "#000000",
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {"type": "box", "layout": "vertical", "contents": [], "margin": "sm"},
                    {
                        "type": "text",
                        "text": "Untappd",
                        "weight": "bold",
                        "color": "#FF0000",
                        "align": "center",
                        "style": "normal",
                        "gravity": "top",
                        "offsetBottom": "10px",
                        "action": {
                            "type": "uri",
                            "label": "action",
                            "uri": beer.get("untappd_url", "https://untappd.com"),
                        },
                    },
                ],
                "flex": 0,
                "backgroundColor": "#000000",
            },
            "styles": {
                "header": {"backgroundColor": "#000000"},
                "hero": {"backgroundColor": "#000000"},
            },
        }
        bubbles.append(bubble)

    return {
        "type": "flex",
        "altText": "Hage & Hige!",
        "contents": {"type": "carousel", "contents": bubbles},
    }


def build_personal_message(name: str) -> Dict[str, Any]:
    """Build personal message for Yurie or Adam."""
    personal_data = {
        "yurie": {
            "name": "Yurie",
            "emoji": "",
            "image": "https://static.wixstatic.com/media/fd66bc_276013ed91a240e0a91dce00006e5031~mv2.jpg/v1/crop/x_0,y_386,w_2250,h_1958/fill/w_1200,h_1044,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/IMG_0331_edited.jpg",
        },
        "adam": {
            "name": "Adam",
            "emoji": "",
            "image": "https://lh3.googleusercontent.com/pw/AMWts8DRT_2D3eyJkyUgAbrKiIQJNhMsxKoytXOwLBk7FsQOdD-O1k7tAyPt-6JViNOZr2iGVMmGM_DyiZ8qf0avwpzpJFKAMqBOeFv4H7h70klo7GgmzSe3TApP-epSDTH9Z3ZI4sELLGJ_hxDBOJoj1vs=s240-no?authuser=0",
        },
    }

    person = personal_data.get(name.lower(), personal_data["adam"])

    return {
        "type": "flex",
        "altText": f"{person['name']}!",
        "contents": {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "image", "url": TITANS_LOGO, "size": "xs"},
                    {
                        "type": "text",
                        "text": f"{person['name']}{person['emoji']}",
                        "weight": "bold",
                        "size": "md",
                        "margin": "md",
                        "align": "center",
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xxl",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "image",
                                "url": person["image"],
                                "size": "full",
                                "animated": False,
                                "aspectMode": "cover",
                            }
                        ],
                        "action": {"type": "postback", "label": "action", "data": "hello"},
                        "cornerRadius": "400px",
                    },
                    {"type": "separator", "margin": "xxl"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": "Happy Friday",
                                "size": "xs",
                                "color": "#aaaaaa",
                                "align": "center",
                            }
                        ],
                    },
                ],
            },
            "styles": {"footer": {"separator": True}},
        },
    }
