"""Shared Amadeus OAuth2 token helper."""
import os
import time
import requests

_cache = {"token": None, "expires": 0}

BASE_URL = "https://test.api.amadeus.com"


def get_token() -> str:
    if _cache["token"] and time.time() < _cache["expires"]:
        return _cache["token"]

    api_key = os.environ.get("AMADEUS_API_KEY", "")
    api_secret = os.environ.get("AMADEUS_API_SECRET", "")
    if not api_key or not api_secret:
        raise RuntimeError(
            "AMADEUS_API_KEY และ AMADEUS_API_SECRET ยังไม่ได้ตั้งค่า\n"
            "สมัครฟรีได้ที่ https://developers.amadeus.com แล้วใส่ใน .env"
        )

    resp = requests.post(
        f"{BASE_URL}/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": api_secret,
        },
        timeout=15,
    )
    if not resp.ok:
        raise RuntimeError(f"Amadeus auth failed: {resp.text}")

    data = resp.json()
    _cache["token"] = data["access_token"]
    _cache["expires"] = time.time() + data["expires_in"] - 60
    return _cache["token"]


def get(path: str, **params) -> dict:
    token = get_token()
    resp = requests.get(
        f"{BASE_URL}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=20,
    )
    if not resp.ok:
        raise RuntimeError(f"Amadeus API error {resp.status_code}: {resp.text[:300]}")
    return resp.json()


# IATA city/airport code lookup
CITY_CODES = {
    "tokyo": "TYO",    "japan": "TYO",    "osaka": "OSA",   "kyoto": "UKY",
    "seoul": "SEL",    "korea": "SEL",    "busan": "PUS",
    "paris": "PAR",    "france": "PAR",
    "london": "LON",   "uk": "LON",
    "rome": "ROM",     "italy": "ROM",    "milan": "MIL",   "venice": "VCE",
    "singapore": "SIN",
    "dubai": "DXB",
    "new york": "NYC", "usa": "NYC",
    "bangkok": "BKK",  "thailand": "BKK",
    "amsterdam": "AMS","netherlands": "AMS",
    "barcelona": "BCN","spain": "MAD",
    "zurich": "ZRH",   "switzerland": "ZRH",
}

AIRPORT_CODES = {
    "bangkok": "BKK",  "thailand": "BKK",
    "tokyo": "NRT",    "japan": "NRT",    "osaka": "KIX",
    "seoul": "ICN",    "korea": "ICN",
    "paris": "CDG",    "france": "CDG",
    "london": "LHR",   "uk": "LHR",
    "singapore": "SIN",
    "rome": "FCO",     "italy": "FCO",
    "dubai": "DXB",
    "new york": "JFK", "usa": "JFK",
    "amsterdam": "AMS","barcelona": "BCN",
}


def resolve_city(name: str, lookup: dict = None) -> str:
    if lookup is None:
        lookup = CITY_CODES
    name_lower = name.lower().strip()
    for k, v in lookup.items():
        if k in name_lower or name_lower in k:
            return v
    return name.upper()[:3]
