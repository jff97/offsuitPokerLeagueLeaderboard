from poker_data_transformer import get_flat_list_of_rounds_from_api

from cosmos_handler import store_flattened_rounds, delete_all_round_data, save_log, get_all_logs, delete_all_logs, get_all_round_entries

from poker_analyzer2 import build_percentile_leaderboard, build_top_3_finish_rate_leaderboard
from script_to_migrate_legacy_csv import get_june_data_as_rounds
from round_data_object import RoundEntry

from typing import List
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
    string_to_log = f"[Daily Task] Ran at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC"
    save_log(string_to_log)

def delete_logs():
    delete_all_logs()

def get_all_logs_to_display_for_api() -> str:
    list_of_all_log_strings = get_all_logs()
    combined_logs = "\n".join(list_of_all_log_strings)
    html_ready = combined_logs.replace("\n", "<br>")
    return html_ready

def refresh_rounds_database():
    log_time()
    delete_all_round_data()
    flattened_records_from_round_format = get_flat_list_of_rounds_from_api(tokens_and_names)
    store_flattened_rounds(flattened_records_from_round_format)
    refresh_june_legacy_csv_rounds()

def get_percentile_leaderboard_from_rounds():
    database_fetched_round_entries = get_all_round_entries()
    percentile_leaderboard = build_percentile_leaderboard(database_fetched_round_entries)
    return percentile_leaderboard.to_string(index=False)

def get_percentile_leaderboard_from_rounds_no_round_limit():
    round_entries = get_all_round_entries()
    percentile_leaderboard = build_percentile_leaderboard(round_entries, 1)
    return percentile_leaderboard.to_string(index=False)

def get_placement_leaderboard_from_rounds():
    round_entries = get_all_round_entries()
    top3_leaderboard = build_top_3_finish_rate_leaderboard(round_entries)
    return top3_leaderboard.to_string(index=False)

def _compare_flattened_records(new_rounds: List[RoundEntry], old_rounds: List[RoundEntry]):
    set_new = set(new_rounds)
    set_old = set(old_rounds)
    print(f"New records count: {len(set(new_rounds))}, Old records count: {len(set(old_rounds))}")

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
    


def refresh_june_legacy_csv_rounds():
    flat_records_new_method = get_june_data_as_rounds()
    store_flattened_rounds(flat_records_new_method)
