import requests

HEADERS = {"User-Agent": "TravelPlanningAgent/1.0 (educational project)"}

CATEGORY_TAGS = {
    "ร้านอาหาร": "restaurant",
    "อาหาร": "restaurant",
    "สถานที่ท่องเที่ยว": "tourism",
    "แหล่งท่องเที่ยว": "attraction",
    "วัด": "place_of_worship",
    "โรงแรม": "hotel",
    "ห้างสรรพสินค้า": "mall",
    "สนามบิน": "aeroway",
    "hospital": "hospital",
    "โรงพยาบาล": "hospital",
}


def search_places(location: str, category: str = None) -> str:
    """ค้นหาสถานที่โดยใช้ OpenStreetMap Nominatim (ฟรี ไม่ต้อง API key)."""
    try:
        tag = CATEGORY_TAGS.get(category, category) if category else None
        query = f"{tag} {location}" if tag else location

        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 6, "addressdetails": 1},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()

        if not results:
            return f"ไม่พบสถานที่: '{query}'"

        lines = [f"ผลการค้นหา '{query}' ({len(results)} แห่ง):\n"]
        for i, r in enumerate(results, 1):
            name = r.get("display_name", "N/A")
            place_type = r.get("type", r.get("class", ""))
            short = name.split(",")[0].strip()
            lat, lon = r.get("lat", ""), r.get("lon", "")
            maps_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=16"
            lines.append(f"{i}. {short} [{place_type}]")
            lines.append(f"   MAP_URL={maps_link}")
            lines.append(f"   ที่อยู่: {name}")

        return "\n".join(lines)

    except Exception as e:
        return f"Map search error: {e}"
