from poker_data_transformer import get_simplified_month_json, flatten_months_to_tuples, _normalize_player_name, get_flat_list_of_rounds

from cosmos_handler import store_month_document, get_month_document, delete_all_month_data, store_flattened_rounds, get_all_rounds, delete_all_round_data

from poker_analyzer2 import  build_percentile_leaderboard, build_top_3_finish_rate_leaderboard

import json

from typing import List, Tuple

tokens_and_names = [
        ("jykjlbzxzkqye", "Cork N Barrel"),
        ("xpwtrdfsvdtce", "Chatters"),
        ("czyvrxfdrjbye", "Mavricks"),
        ("qdtgqhtjkrtpe", "Alibi"),
        ("vvkcftdnvdvge", "Layton Heights"),
        ("tbyyvqmpjsvke", "Tinys"),
        ("pcynjwvnvgqme", "Hosed on Brady"),
        ("jkhwxjkpxycle", "Witts End"),
        ("khptcxdgnpnbe", "Lakeside"),
        ("zyqphgqxppcde", "Brickyard Pub"),
        ("ybmwcqckckdhe", "South Bound Again"),
        ("pwtmrylcjnjye", "Anticipation Sunday"),
    ]

def percentile_leaderboard():
    json_month_2 = get_month_document("202507")
    all_flat_records = flatten_months_to_tuples([ json_month_2])

    # Step 5: build and print percentile leaderboard (ranking inside)
    percentile_leaderboard = build_percentile_leaderboard(all_flat_records)
    print("Percentile Leaderboard from month database")
    return percentile_leaderboard.to_string(index=False)

def placement_leaderboard():
    json_month_2 = get_month_document("202507")

    all_flat_records = flatten_months_to_tuples([json_month_2]) 

    top3_leaderboard = build_top_3_finish_rate_leaderboard(all_flat_records)
    return top3_leaderboard.to_string(index=False)

def test2():
    # Step 1: wipe all data to start fresh
    delete_all_month_data

    # Step 3: Get current month document
    month_doc = get_simplified_month_json(tokens_and_names)
    store_month_document(month_doc)
    
    with open("output.json", "w") as f: f.write(json.dumps(month_doc, indent=2))

def test3():
    flattened_records_from_round_format = get_flat_list_of_rounds(tokens_and_names)

    flattened_records_from_month_data_format = flatten_months_to_tuples([get_simplified_month_json(tokens_and_names)])
    compare_flattened_records(flattened_records_from_round_format, flattened_records_from_month_data_format)

def test4():
    flattened_records_from_round_format = get_flat_list_of_rounds(tokens_and_names)
    percentile_leaderboard = build_percentile_leaderboard(flattened_records_from_round_format)
    print()
    print(percentile_leaderboard.to_string(index=False))

    # top3_leaderboard = build_top_3_finish_rate_leaderboard(flattened_records_from_round_format)
    # print(top3_leaderboard.to_string(index=False))

def test5():
    flattened_records_from_round_format = get_flat_list_of_rounds(tokens_and_names)

    store_flattened_rounds(flattened_records_from_round_format)

    database_fetched_rounds = get_all_rounds()

    percentile_leaderboard = build_percentile_leaderboard(database_fetched_rounds)
    print("Percentile Leaderboard from rounds database")
    print(percentile_leaderboard.to_string(index=False))

    # top3_leaderboard = build_top_3_finish_rate_leaderboard(database_fetched_rounds)
    # print(top3_leaderboard.to_string(index=False))

def compare_flattened_records(
    new_records: List[Tuple[str, str, str, int]],
    old_records: List[Tuple[str, str, str, int]]
) -> None:
    """
    Compare two lists of flattened records and print differences.

    Args:
        new_records: List of tuples from new method.
        old_records: List of tuples from old method.

    Returns:
        None. Prints detailed comparison result.
    """

    # Convert lists to sets for unordered comparison
    set_new = set(new_records)
    set_old = set(old_records)
    print(f"New records count: {len(set(new_records))}, Old records count: {len(set(old_records))}")


    only_in_new = set_new - set_old
    only_in_old = set_old - set_new

    if not only_in_new and not only_in_old:
        print("✅ SUCCESS: Both record lists match exactly!")
    else:
        print("❌ MISMATCH FOUND:")
        if only_in_new:
            print(f"\nRecords only in NEW method ({len(only_in_new)}):")
            for rec in sorted(only_in_new):
                print(f"  {rec}")
        if only_in_old:
            print(f"\nRecords only in OLD method ({len(only_in_old)}):")
            for rec in sorted(only_in_old):
                print(f"  {rec}")

def verify_flattened_rounds(simplified_rounds, flattened_records):
    """
    Check that every (normalized_name, round_id, bar_name, points) in simplified_rounds
    exists in flattened_records. Prints mismatches if found.
    """
    # Convert flattened list to a set for fast lookup
    flattened_set = set(flattened_records)
    mismatches_found = False

    for round_doc in simplified_rounds:
        round_id = round_doc["round_id"]
        bar_name = round_doc["bar_name"]
        scores = round_doc.get("scores", [])

        for score in scores:
            normalized_name = _normalize_player_name(score["name"])
            points = score["points"]
            if points == 0:
                continue  # Skip players with 0 points
            expected_tuple = (normalized_name, round_id, bar_name, points)

            if expected_tuple not in flattened_set:
                print(f"❌ Missing: {expected_tuple}")
                mismatches_found = True

    if not mismatches_found:
        print("✅ All round scores correctly represented in flattened data.")

if __name__ == "__main__":
    delete_all_month_data()
    delete_all_round_data()
    test2()
    print(percentile_leaderboard())
    test5()

