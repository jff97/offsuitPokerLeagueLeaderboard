from poker_data_transformer import get_flat_list_of_rounds_from_api, legacy_month_list_of_rounds_getter

from cosmos_handler import store_flattened_rounds, get_all_rounds, delete_all_round_data

from poker_analyzer2 import build_percentile_leaderboard, build_top_3_finish_rate_leaderboard

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
def placement_leaderboard_by_month_method():
    all_flat_records = legacy_month_list_of_rounds_getter(tokens_and_names)
    top3_leaderboard = build_top_3_finish_rate_leaderboard(all_flat_records)
    return top3_leaderboard.to_string(index=False)

def percentile_leaderboard_by_month_method():
    all_flat_records = legacy_month_list_of_rounds_getter(tokens_and_names)
    percentile_leaderboard = build_percentile_leaderboard(all_flat_records)
    return percentile_leaderboard.to_string(index=False)

def refresh_rounds_database():
    delete_all_round_data()
    flattened_records_from_round_format = get_flat_list_of_rounds_from_api(tokens_and_names)
    store_flattened_rounds(flattened_records_from_round_format)

def get_percentile_leaderboard_from_rounds():
    database_fetched_rounds = get_all_rounds()
    percentile_leaderboard = build_percentile_leaderboard(database_fetched_rounds)
    return percentile_leaderboard.to_string(index=False)

def get_placement_leaderboard_from_rounds():
    database_fetched_rounds = get_all_rounds()
    top3_leaderboard = build_top_3_finish_rate_leaderboard(database_fetched_rounds)
    return top3_leaderboard.to_string(index=False)

def _compare_flat_rounds_from_months_and_rounds_based():
    flattened_records_from_round_format = get_flat_list_of_rounds_from_api(tokens_and_names)
    flattened_records_from_month_data_format = legacy_month_list_of_rounds_getter(tokens_and_names)
    _compare_flattened_records(flattened_records_from_round_format, flattened_records_from_month_data_format)

def _compare_flattened_records(
    new_records: List[Tuple[str, str, str, int]],
    old_records: List[Tuple[str, str, str, int]]
) -> None:
    

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

def _test_round_method_with_database():
    refresh_rounds_database()
    database_fetched_rounds = get_all_rounds()

    percentile_leaderboard = build_percentile_leaderboard(database_fetched_rounds)
    print("Percentile Leaderboard from rounds database")
    print(percentile_leaderboard.to_string(index=False))

    top3_leaderboard = build_top_3_finish_rate_leaderboard(database_fetched_rounds)
    print("Placement Leaderboard from rounds database")
    print(top3_leaderboard.to_string(index=False))

def _test_month_method_no_db():
    print("Percentile Leaderboard from months method")
    print(percentile_leaderboard_by_month_method())

if __name__ == "__main__":
    _test_month_method_no_db
    _test_round_method_with_database()

