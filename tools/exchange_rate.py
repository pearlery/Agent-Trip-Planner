import requests


def get_exchange_rate(from_currency: str, to_currency: str, amount: float = 1.0) -> str:
    """Get live currency exchange rate. รองรับ THB โดยตรง (open.er-api.com, ไม่ต้อง API key)."""
    try:
        resp = requests.get(
            f"https://open.er-api.com/v6/latest/{from_currency.upper()}",
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("result") != "success":
            return f"ไม่สามารถดึงอัตราแลกเปลี่ยน {from_currency} ได้"

        rate = data.get("rates", {}).get(to_currency.upper())
        if rate is None:
            return f"ไม่พบสกุลเงิน '{to_currency}'"

        converted = amount * rate
        updated = data.get("time_last_update_utc", "")[:16]
        return (
            f"อัตราแลกเปลี่ยน (อัปเดต: {updated}):\n"
            f"  1 {from_currency.upper()} = {rate:,.4f} {to_currency.upper()}\n"
            f"  {amount:,.2f} {from_currency.upper()} = {converted:,.2f} {to_currency.upper()}"
        )
    except requests.RequestException as e:
        return f"Network error: {e}"
    except Exception as e:
        return f"Error: {e}"
