from poker_data_transformer import get_list_of_rounds_from_api

from cosmos_handler import store_rounds, delete_all_round_data, save_log, get_all_logs, delete_all_logs, get_all_rounds

from poker_analyzer import build_percentile_leaderboard, build_top_3_finish_rate_leaderboard
from script_to_migrate_legacy_csv import get_june_data_as_rounds
from round import Round

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
    new_api_rounds = get_list_of_rounds_from_api(tokens_and_names)
    store_rounds(new_api_rounds)
    refresh_june_legacy_csv_rounds()

def get_percentile_leaderboard_from_rounds():
    stored_rounds = get_all_rounds()
    percentile_leaderboard = build_percentile_leaderboard(stored_rounds)
    return percentile_leaderboard.to_string(index=False)

def get_percentile_leaderboard_from_rounds_no_round_limit():
    stored_rounds = get_all_rounds()
    percentile_leaderboard = build_percentile_leaderboard(stored_rounds, 1)
    return percentile_leaderboard.to_string(index=False)

def get_placement_leaderboard_from_rounds():
    stored_rounds = get_all_rounds()
    top3_leaderboard = build_top_3_finish_rate_leaderboard(stored_rounds)
    return top3_leaderboard.to_string(index=False)

def _compare_rounds(new_rounds: List[Round], old_rounds: List[Round]):
    set_new = set(new_rounds)
    set_old = set(old_rounds)
    print(f"New rounds count: {len(set(new_rounds))}, Old rounds count: {len(set(old_rounds))}")

    only_in_new = set_new - set_old
    only_in_old = set_old - set_new

    if not only_in_new and not only_in_old:
        print("✅ SUCCESS: Both round lists match exactly!")
    else:
        print("❌ MISMATCH FOUND:")
        if only_in_new:
            print(f"\nRounds only in NEW method ({len(only_in_new)}):")
            for round_obj in sorted(only_in_new):
                print(f"  {round_obj}")
        if only_in_old:
            print(f"\nRounds only in OLD method ({len(only_in_old)}):")
            for round_obj in sorted(only_in_old):
                print(f"  {round_obj}")


def refresh_june_legacy_csv_rounds():
    legacy_rounds = get_june_data_as_rounds()
    store_rounds(legacy_rounds)
