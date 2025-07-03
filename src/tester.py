from keep_the_score_api_service import get_simplified_month_json
from cosmos_handler import store_month_document, get_month_document, delete_all_data

import pprint
import io

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
    month_doc = get_simplified_month_json(tokens_and_names)

    month_id = month_doc.get("_id")

    print(f"\n=== Storing month document with _id: {month_id} ===", file=output)
    store_month_document(month_doc)

    print(f"\n=== Reading back stored month document with _id: {month_id} ===", file=output)
    retrieved = get_month_document(month_id)
    pprint.pprint(retrieved, stream=output, depth=8, compact=True)

    return output.getvalue()

if __name__ == "__main__":
    log = test1()
    print(log)
