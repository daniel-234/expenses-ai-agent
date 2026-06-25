from openai.types.chat import ChatCompletionToolParam

CURRENCY_CONVERSION_TOOL: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "convert_currency",
        "description": "Convert the given amount from a currency and return it in another currency",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "An amount of money like 42.50 or 10.00 or 25.00",
                },
                "from_currency": {
                    "type": "string",
                    "description": "The source currency code like EUR or USD",
                },
                "to_currency": {
                    "type": "string",
                    "description": "The target currency code like USD or EUR",
                },
            },
            "required": ["amount", "from_currency", "to_currency"],
        },
    },
}


DATETIME_FORMATTER_TOOL: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "format_datetime",
        "description": "Format the date and time an expense has been made",
        "parameters": {
            "type": "object",
            "properties": {
                "datetime_str": {
                    "type": "string",
                    "description": "The date and time of an expense",
                },
                "timezone_str": {
                    "type": "string",
                    "description": "The timezone of the country where the expense has been made (e.g. Europe/Madrid)",
                },
            },
            "required": [
                "datetime_str",
            ],
        },
    },
}
