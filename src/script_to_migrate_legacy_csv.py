import csv
import io
import os
from datetime import datetime
from poker_data_transformer import _map_month_to_list_of_rounds, _convert_json_rounds_to_round_objects


def parse_csv_to_bar_entry(csv_data: str, month_id: str, bar_token: str, bar_name: str) -> dict:
    """
    Parse a single bar's CSV into { bar_token: {bar_name, rounds} },
    excluding player_id entirely.
    """
    f = io.StringIO(csv_data.strip())
    reader = csv.DictReader(f)

    # Determine which columns are rounds (skip empty, 'Totals', 'Player')
    round_cols = [
        col for col in reader.fieldnames
        if col and col.lower() not in ('totals', 'total', 'player')
    ]

    rounds_list = []
    for idx, rnd in enumerate(round_cols, start=1):
        rounds_list.append({
            "round_id": f"{month_id}_{bar_token}_{idx}",
            "date": datetime(datetime.utcnow().year, 6, 15 + idx, 12, 0, 0).strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "scores": []
        })

    for row in reader:
        # Read player name (handle blank header)
        player_name = (
            row.get('Player')
            or row.get('player')
            or row.get('')
            or list(row.values())[1]
        ).strip()

        for i, rnd in enumerate(round_cols):
            pts_text = row.get(rnd, '').strip()
            try:
                points = int(pts_text.split()[0])
            except Exception:
                points = 0

            if points > 0:
                rounds_list[i]["scores"].append({
                    "name": player_name,
                    "points": points
                })

    return {
        bar_token: {
            "bar_name": bar_name,
            "rounds": rounds_list
        }
    }

def _get_legacy_month_as_round_objects(month_id: str, bars: list):
    month_doc = {
        "_id": month_id,
        "month": f"{month_id[:4]}-{month_id[4:]}",
        "bars": {}
    }

    for bar_token, bar_name, csv_data in bars:
        entry = parse_csv_to_bar_entry(csv_data, month_id, bar_token, bar_name)
        month_doc["bars"].update(entry)

    list_of_rounds_from_new_method = _map_month_to_list_of_rounds(month_doc)
    round_objects = _convert_json_rounds_to_round_objects(list_of_rounds_from_new_method)

    return round_objects

def _get_csv_file_path(filename: str) -> str:
    """Get the absolute path to a CSV file in the output directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_dir = os.path.join(script_dir, "..", "oldStuffRename", "june2025", "output")
    return os.path.join(csv_dir, filename)

def _read_csv_file(filename: str) -> str:
    """Read the contents of a CSV file and return as string."""
    csv_path = _get_csv_file_path(filename)
    with open(csv_path, 'r') as f:
        return f.read().strip()

def get_csv_literal_bar_alibi() -> str:
    return _read_csv_file("alibi.csv")

def get_csv_literal_bar_anticipationsun() -> str:
    return _read_csv_file("anticipationSun.csv")

def get_csv_literal_bar_anticipationtues() -> str:
    return _read_csv_file("anticipationTues.csv")

def get_csv_literal_bar_brickyard() -> str:
    return _read_csv_file("brickyard.csv")

def get_csv_literal_bar_chatters() -> str:
    return _read_csv_file("chatters.csv")

def get_csv_literal_bar_corknbarrel() -> str:
    return _read_csv_file("corkNBarrel.csv")

def get_csv_literal_bar_hosed() -> str:
    return _read_csv_file("hosed.csv")

def get_csv_literal_bar_lakeside() -> str:
    return _read_csv_file("lakeside.csv")

def get_csv_literal_bar_layton() -> str:
    return _read_csv_file("laytonHeights.csv")

def get_csv_literal_bar_mavricks() -> str:
    return _read_csv_file("mavricks.csv")

def get_csv_literal_bar_southbound() -> str:
    return _read_csv_file("southBound.csv")

def get_csv_literal_bar_tinys() -> str:
    return _read_csv_file("tinys.csv")

def get_csv_literal_bar_witts() -> str:
    return _read_csv_file("wittsEnd.csv")


def get_june_data_as_rounds():
    month_id = "202506"

    bars = [
        ("qdtgqhtjkrtpe", "legacyThe Alibi",            get_csv_literal_bar_alibi()),
        ("pwtmrylcjnjye", "legacyAnticipation", get_csv_literal_bar_anticipationsun()),
        ("fakeanticipationtuesdayapitoken","legacyAnticipation Tues", get_csv_literal_bar_anticipationtues()),
        ("zyqphgqxppcde",    "legacyBrickyard Pub",        get_csv_literal_bar_brickyard()),
        ("xpwtrdfsvdtce",     "legacyChatter's",         get_csv_literal_bar_chatters()),
        ("jykjlbzxzkqye",  "legacyCork N Barrel",    get_csv_literal_bar_corknbarrel()),
        ("pcynjwvnvgqme",        "legacyHOSED ON BRADY",   get_csv_literal_bar_hosed()),
        ("khptcxdgnpnbe",     "legacyLakeside Pub & Grill",         get_csv_literal_bar_lakeside()),
        ("vvkcftdnvdvge",       "legacyLAYTON HEIGHTS",           get_csv_literal_bar_layton()),
        ("czyvrxfdrjbye",     "legacyMavericks ",         get_csv_literal_bar_mavricks()),
        ("ybmwcqckckdhe",   "legacySouth Bound Again",       get_csv_literal_bar_southbound()),
        ("tbyyvqmpjsvke",        "legacyTiny's A Neighborhood Sports Tavern",            get_csv_literal_bar_tinys()),
        ("jkhwxjkpxycle",        "legacyWITTS END",            get_csv_literal_bar_witts()),
    ]

    return _get_legacy_month_as_round_objects(month_id, bars)

if __name__ == "__main__":
    get_june_data_as_rounds()
