import json

def flatten_rounds(monthly_data):
    flattened_rounds = []

    general_month_info = {}
    for key, value in monthly_data.items():
        if key != 'bars' and key != '_id':
            general_month_info[key] = value

    bars = monthly_data.get('bars', {})

    for bar_id in bars:
        bar_info = bars[bar_id]

        bar_name = bar_info.get('bar_name')

        rounds = bar_info.get('rounds', [])

        for round_info in rounds:
            round_document = {}

            for key in general_month_info:
                round_document[key] = general_month_info[key]

            round_document['bar_id'] = bar_id
            round_document['bar_name'] = bar_name

            for key, value in round_info.items():
                round_document[key] = value

            flattened_rounds.append(round_document)

    return flattened_rounds

def main():
    input_filename = input("Please enter the path to the JSON input file: ").strip()

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            monthly_data = json.load(f)
    except Exception as e:
        print(f"Error reading or parsing JSON file: {e}")
        return

    flattened = flatten_rounds(monthly_data)

    for round_doc in flattened:
        print(json.dumps(round_doc, indent=2))

if __name__ == "__main__":
    main()
