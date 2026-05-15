from typing import Optional
from tools._amadeus import get, resolve_city, CITY_CODES


def search_hotels(destination: str, max_price_per_night: Optional[float] = None, min_rating: Optional[int] = None) -> str:
    """Search real hotels via Amadeus API (free tier). ต้องตั้ง AMADEUS_API_KEY และ AMADEUS_API_SECRET ใน .env"""
    try:
        city_code = resolve_city(destination, CITY_CODES)

        params = {"cityCode": city_code, "radius": 10, "radiusUnit": "KM"}
        if min_rating:
            params["ratings"] = ",".join(str(r) for r in range(int(min_rating), 6))

        data = get("/v1/reference-data/locations/hotels/by-city", **params)
        hotels = data.get("data", [])

        if not hotels:
            return f"ไม่พบโรงแรมใน {destination} (city code: {city_code})"

        lines = [f"โรงแรมใน {destination.title()} ({min(len(hotels), 10)} แห่ง จาก Amadeus):\n"]
        for h in hotels[:10]:
            name = h.get("name", "N/A")
            address = h.get("address", {})
            city_name = address.get("cityName", "")
            country = address.get("countryCode", "")
            rating = h.get("rating", "-")
            lines.append(f"  - {name}  | {city_name}, {country}  | ระดับ {rating} ดาว")

        if max_price_per_night:
            lines.append("\n(หมายเหตุ: ตรวจสอบราคาจริงได้บน Booking.com หรือ Agoda)")

        return "\n".join(lines)

    except RuntimeError as e:
        return str(e)
    except Exception as e:
        return f"Hotel search error: {e}"
