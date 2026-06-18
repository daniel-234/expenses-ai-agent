from decimal import Decimal

import requests
from decouple import config

EXCHANGE_RATE_API_KEY = config("EXCHANGE_RATE_API_KEY")
API_PAIR_URL = (
    "https://v6.exchangerate-api.com/v6/{api}/pair/{from_currency}/{to_currency}"
)


def convert_currency(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    """Return the amount 'from_currency' converted to 'to_currency' as Decimal value"""
    if from_currency == to_currency:
        return amount
    response = requests.get(
        API_PAIR_URL.format(
            api=EXCHANGE_RATE_API_KEY,
            from_currency=from_currency,
            to_currency=to_currency,
        )
    )
    response.raise_for_status()
    data = response.json()
    return Decimal(str(data["conversion_rate"])) * amount
