import httpx
from test_data_parsing import parse_brave_response

API_KEY = ""

def api_test(keyword: str):

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": API_KEY,
        "cache_control": "no-cache",

    }

    params = {
        "q": f"{keyword}",
        "count": 1,
    }

    response = httpx.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers=headers,
        params=params,
    )
    data = response.json()
    print(data)
    return data




