import requests

def fetch_board_json(token: str) -> dict:
    url = f"https://keepthescore.com/api/{token}/board/"
    headers = {"accept": "*/*"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
