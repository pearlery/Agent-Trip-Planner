import requests

HEADERS = {"User-Agent": "TravelPlanningAgent/1.0 (educational)"}

WMO = {
    0: "แดดจัด", 1: "แดดเป็นส่วนใหญ่", 2: "มีเมฆบางส่วน", 3: "ครึ้มฟ้า",
    45: "หมอก", 48: "หมอกเกาะ",
    51: "ฝนปรอยเบา", 53: "ฝนปรอย", 55: "ฝนปรอยหนัก",
    61: "ฝนเบา", 63: "ฝนปานกลาง", 65: "ฝนหนัก",
    71: "หิมะเบา", 73: "หิมะปานกลาง", 75: "หิมะหนัก",
    80: "ฝนสั้นๆ", 81: "ฝนสั้นปานกลาง", 82: "ฝนสั้นหนัก",
    95: "พายุฝนฟ้าคะนอง", 96: "พายุลูกเห็บ", 99: "พายุลูกเห็บหนัก",
}


def _geocode(city: str):
    resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": city, "format": "json", "limit": 1},
        headers=HEADERS,
        timeout=10,
    )
    results = resp.json()
    if not results:
        return None, None, city
    r = results[0]
    return float(r["lat"]), float(r["lon"]), r.get("display_name", city).split(",")[0]


def get_weather(city: str, days: int = 5) -> str:
    """Get weather forecast for a city (1-7 days). ใช้ Open-Meteo API (ฟรี ไม่ต้อง key)."""
    try:
        lat, lon, display_name = _geocode(city)
        if lat is None:
            return f"ไม่พบตำแหน่ง: {city}"

        days = max(1, min(days, 7))
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weathercode,windspeed_10m,apparent_temperature",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
                "timezone": "auto",
                "forecast_days": days,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        cur = data["current"]
        cur_desc = WMO.get(cur.get("weathercode", 0), "ไม่ทราบ")

        lines = [
            f"สภาพอากาศ: {display_name}",
            f"\nสภาพปัจจุบัน:",
            f"  อุณหภูมิ  : {cur['temperature_2m']}°C (รู้สึกเหมือน {cur['apparent_temperature']}°C)",
            f"  ความชื้น  : {cur['relative_humidity_2m']}%",
            f"  ลม        : {cur['windspeed_10m']} km/h",
            f"  สภาพ      : {cur_desc}",
            f"\nพยากรณ์ {days} วัน:",
        ]

        daily = data["daily"]
        for i, date in enumerate(daily["time"]):
            desc = WMO.get(daily["weathercode"][i], "?")
            rain = daily["precipitation_probability_max"][i]
            hi = daily["temperature_2m_max"][i]
            lo = daily["temperature_2m_min"][i]
            lines.append(f"  {date}  สูง {hi}°C / ต่ำ {lo}°C  ฝน {rain}%  {desc}")

        return "\n".join(lines)

    except Exception as e:
        return f"Weather error: {e}"
