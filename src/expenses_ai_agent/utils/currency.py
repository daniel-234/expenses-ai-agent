from decimal import Decimal

import requests
from decouple import config

EXCHANGE_RATE_API_KEY = config("EXCHANGE_RATE_API_KEY", default="")
API_PAIR_URL = (
    "https://v6.exchangerate-api.com/v6/{api}/pair/{from_currency}/{to_currency}"
)


def convert_currency(
    amount: Decimal | float, from_currency: str, to_currency: str
) -> Decimal:
    """Return the amount 'from_currency' converted to 'to_currency' as Decimal value"""
    decimal_amount = Decimal(str(amount))
    if from_currency == to_currency:
        return decimal_amount
    if not EXCHANGE_RATE_API_KEY:
        raise ValueError("EXCHANGE_RATE_API_KEY is not set")
    response = requests.get(
        API_PAIR_URL.format(
            api=EXCHANGE_RATE_API_KEY,
            from_currency=from_currency,
            to_currency=to_currency,
        ),
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return Decimal(str(data["conversion_rate"])) * decimal_amount
