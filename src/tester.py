from keep_the_score_api_service import fetch_board_json
from mapping_service import build_month_doc
from cosmos_handler import store_month_document, get_month_document, delete_all_data

import pprint
import io

def fetch_and_build_month(api_tokens_and_bar_names):
    bar_data_list = []

    for token, bar_name in api_tokens_and_bar_names:
        bar_json = fetch_board_json(token)
        if "error" in bar_json:
            print(f"Error fetching {bar_name}: {bar_json['error']}")
            continue
        bar_data_list.append((token, bar_name, bar_json))

    return build_month_doc(bar_data_list)

def test1():
    tokens_and_names = [
        ("pcynjwvnvgqme", "Hosed on Brady"),
        ("qdtgqhtjkrtpe", "Alibi"),
    ]

    output = io.StringIO()

    print("\n=== Deleting all data ===", file=output)
    delete_all_data()
    print("All data deleted.", file=output)

    print("=== Fetching and building month document ===", file=output)
    month_doc = fetch_and_build_month(tokens_and_names)

    month_id = month_doc.get("_id")

    print(f"\n=== Storing month document with _id: {month_id} ===", file=output)
    store_month_document(month_doc)

    print(f"\n=== Reading back stored month document with _id: {month_id} ===", file=output)
    retrieved = get_month_document(month_id)
    pprint.pprint(retrieved, stream=output, depth=8, compact=True)

    return output.getvalue()

if __name__ == "__main__":
    test1()
