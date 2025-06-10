import httpx

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

API_ADDRESS = 'https://api.frankfurter.app/'

@tool
def get_exchange_rate(
    currency_from: str = 'USD',
    currency_to: str = 'EUR',
    currency_date: str = 'latest'
):
    """This tool helps to get current currency exchange rate

    Args:
        currency_from: The currency to convert from (e.g., USD)
        currency_to: The currency to convert to (e.g., EUR)
        currency_date: The date on which this exchange is sought. 
                       Default is "latest"

    Returns:
        A dictionary containing the exchange rate. However, it will contain
        error message in case of an error.
    """
    try:
        address = API_ADDRESS + f"{currency_date}"
        params = {
            "from": currency_from,
            "to": currency_to
        }

        response = httpx.get(address, params=params)
        response.raise_for_status()

        data = response.json()

        if 'rates' not in data:
            return {'error': 'Invalid API response format'}
        return data

    except httpx.HTTPError as e:
        return {'error': f'API request failed: {e}'}
    except ValueError:
        return {'error': 'Invalid JSON response from API'}



if __name__ == "__main__":
    pass
