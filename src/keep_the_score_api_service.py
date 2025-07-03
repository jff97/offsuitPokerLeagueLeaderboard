import requests

def fetch_board_json(token: str) -> dict:
    url = f"https://keepthescore.com/api/{token}/board/"
    headers = {
        "accept": "*/*"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # raises exception for 4xx/5xx
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


if __name__ == "__main__":
    tokens = [
        "jyklbzxzkqye", #cork and barrel
        "xpwtrdfsvdtce", # chatters
        "czyvrxfdrjbye", #mavricks
        "qdtgqhtjkrtpe", #alibi
        "pcynjwvnvgqme", #Hosed on brady
    ]

    for token in tokens:
        print(f"Fetching board for token: {token}")
        result = fetch_board_json(token)
        print(result)
        print("-" * 40)