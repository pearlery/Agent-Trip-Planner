from datetime import datetime, timedelta
from tools._amadeus import get, resolve_city, AIRPORT_CODES


def search_flights(origin: str, destination: str, departure_date: str = None, adults: int = 1) -> str:
    """Search real flights via Amadeus API (free tier). departure_date format: YYYY-MM-DD
    ต้องตั้ง AMADEUS_API_KEY และ AMADEUS_API_SECRET ใน .env"""
    try:
        if departure_date is None:
            departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        origin_code = resolve_city(origin, AIRPORT_CODES)
        dest_code = resolve_city(destination, AIRPORT_CODES)

        data = get(
            "/v2/shopping/flight-offers",
            originLocationCode=origin_code,
            destinationLocationCode=dest_code,
            departureDate=departure_date,
            adults=adults,
            max=5,
            currencyCode="THB",
        )
        offers = data.get("data", [])

        if not offers:
            return (
                f"ไม่พบเที่ยวบิน {origin.title()} ({origin_code}) → {destination.title()} ({dest_code})\n"
                f"วันที่: {departure_date}"
            )

        lines = [
            f"เที่ยวบิน {origin.title()} ({origin_code}) → {destination.title()} ({dest_code})",
            f"วันที่: {departure_date}  |  ผู้โดยสาร: {adults} คน\n",
        ]

        for i, offer in enumerate(offers, 1):
            price = float(offer["price"]["total"])
            currency = offer["price"]["currency"]
            itin = offer["itineraries"][0]
            segs = itin["segments"]

            duration = itin["duration"].replace("PT", "").replace("H", "ชม.").replace("M", "น.")
            airline = segs[0]["carrierCode"]
            dep = segs[0]["departure"]["at"][:16].replace("T", " ")
            arr = segs[-1]["arrival"]["at"][:16].replace("T", " ")
            stops = len(segs) - 1
            stop_str = "เที่ยวบินตรง" if stops == 0 else f"แวะ {stops} จุด"

            lines.append(
                f"  [{i}] {airline}  {dep} → {arr}  ({duration})  {stop_str}\n"
                f"       ราคา: {price:,.0f} {currency}"
            )

        return "\n".join(lines)

    except RuntimeError as e:
        return str(e)
    except Exception as e:
        return f"Flight search error: {e}"
