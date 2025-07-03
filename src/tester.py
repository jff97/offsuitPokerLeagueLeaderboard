from keep_the_score_api_service import get_simplified_month_json
from cosmos_handler import store_month_document, get_month_document, delete_all_data
from poker_analyzer2 import flatten_all_months_to_tuples, build_percentile_leaderboard, build_top_3_finish_rate_leaderboard
from wipe import wipe_all
from script_to_migrate_legacy_csv import migrate_start
import pprint
import io

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
    json_month_1 = get_month_document("202506") #this one is legacy allways stays there
    json_month_2 = get_month_document("202507")

    all_flat_records = flatten_all_months_to_tuples([json_month_1, json_month_2])

    # Step 5: build and print percentile leaderboard (ranking inside)
    percentile_leaderboard = build_percentile_leaderboard(all_flat_records)
    return percentile_leaderboard.to_string(index=False)

def placement_leaderboard():
    json_month_1 = get_month_document("202506") #this one is legacy allways stays there
    json_month_2 = get_month_document("202507")

    all_flat_records = flatten_all_months_to_tuples([json_month_1, json_month_2]) 

    top3_leaderboard = build_top_3_finish_rate_leaderboard(all_flat_records)
    return top3_leaderboard.to_string(index=False)


def test2():
    # Step 1: wipe all data to start fresh
    wipe_all() 
    
    # Step 2: get legacy month document
    migrate_start() # this will create month 202506
    json_month_1 = get_month_document("202506") #this one is legacy allways stays there

    # Step 3: Get current month document
    month_doc = get_simplified_month_json(tokens_and_names)
    store_month_document(month_doc)
    json_month_2 = get_month_document("202507")

    # Step 4: flatten json data into single tuple list of show ups
    all_flat_records = flatten_all_months_to_tuples([json_month_1, json_month_2])

    # Step 5: build and print percentile leaderboard (ranking inside)
    percentile_leaderboard = build_percentile_leaderboard(all_flat_records)
    print("\n🏆 Cumulative Leaderboard (sorted by average percentile rank):\n")
    print(percentile_leaderboard.to_string(index=False))

    # Step 6: build and print top 3 finish rate leaderboard (ranking inside)
    top3_leaderboard = build_top_3_finish_rate_leaderboard(all_flat_records)
    print("\n🥇 Leaderboard by Top 3 Finish Percentage:\n")
    print(top3_leaderboard.to_string(index=False))


if __name__ == "__main__":
    test2()
