from poker_data_transformer import get_flat_list_of_rounds_from_api, legacy_month_list_of_rounds_getter

from cosmos_handler import store_flattened_rounds, get_all_rounds, delete_all_round_data, save_log, get_all_logs, delete_all_logs

from poker_analyzer2 import build_percentile_leaderboard, build_top_3_finish_rate_leaderboard
from script_to_migrate_legacy_csv import migrate_start

from typing import List, Tuple
from datetime import datetime

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

def log_time():
    string_to_log = f"[Daily Task] Ran at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    save_log(string_to_log)

def delete_logs():
    delete_all_logs()

def get_all_logs_to_display_for_api() -> str:
    list_of_all_log_strings = get_all_logs()
    combined_logs = "\n".join(list_of_all_log_strings)
    html_ready = combined_logs.replace("\n", "<br>")
    return html_ready

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
    refresh_june_legacy_csv_rounds()

def get_percentile_leaderboard_from_rounds():
    database_fetched_rounds = get_all_rounds()
    percentile_leaderboard = build_percentile_leaderboard(database_fetched_rounds)
    return percentile_leaderboard.to_string(index=False)

def get_percentile_leaderboard_from_rounds_no_round_limit():
    database_fetched_rounds = get_all_rounds()
    percentile_leaderboard = build_percentile_leaderboard(database_fetched_rounds, 1)
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

def legacy_test():
    (flat_records_new_method, flat_records_old_method) = migrate_start()
    _compare_flattened_records(flat_records_new_method, flat_records_old_method)

def refresh_june_legacy_csv_rounds():
    (flat_records_new_method, _) = migrate_start()
    store_flattened_rounds(flat_records_new_method)
    

if __name__ == "__main__":
    #1
    # _test_month_method_no_db
    # _test_round_method_with_database()
    legacy_test()

