import csv
import io
from datetime import datetime
from cosmos_handler import store_month_document
import json


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


def build_and_store_full_month(month_id: str, bars: list):
    """
    bars: list of tuples (bar_token, bar_name, csv_data_str)
    Build one month doc containing all bars and store it.
    """
    month_doc = {
        "_id": month_id,
        "month": f"{month_id[:4]}-{month_id[4:]}",
        "bars": {}
    }

    for bar_token, bar_name, csv_data in bars:
        entry = parse_csv_to_bar_entry(csv_data, month_id, bar_token, bar_name)
        month_doc["bars"].update(entry)

    store_month_document(month_doc)
    #printthingy(month_doc)

    
    print(f"✅ Stored month document for {month_id} with {len(bars)} bars.")

def printthingy(month_doc): 
    output_path = "month_doc.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
           month_doc,
           f,
           indent=2,
           ensure_ascii=False
        )
    print(f"Month document written to {output_path}")
# -----------------------------
# CSV literal functions below
# -----------------------------

def get_csv_literal_bar_alibi() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Nico A,101,15,32,41,13
2,Joe G,100,0,44,47,9
3,Cindy R,97,14,16,35,32
4,Lori H.,85,9,17,21,38
5,Devon T,83,41,10,20,12
6,Colton,79,29,38,7,5
7,Pyerre L,77,18,20,24,15
8,Miguel Q,61,12,19,23,7
9,Greg H.,49,11,18,9,11
10,Steel Neil,42,35,0,6,1
11,Greg S,40,4,5,5,26
12,Rob H.,39,10,9,12,8
13,Johnathan H.,38,17,8,13,0
14,Tracy S,37,7,12,18,0
15,Jack,31,13,0,4,14
16,Bob R,30,6,6,8,10
17,L,30,0,11,19,0
18,John S.,29,16,0,11,2
19,Tony Sr.,29,8,4,17,0
20,Caleb G,27,0,7,14,6
21,Mellisa H,27,5,0,22,0
22,Domanic A,23,2,21,0,0
23,Ben D,20,0,15,2,3
24,Carter,16,0,1,15,0
25,John F.,16,0,0,16,0
26,Jeremiah,15,1,14,0,0
27,Jordan H.,13,0,13,0,0
28,Joaquin,10,0,0,10,0
29,Darnell,6,3,3,0,0
30,Alex W,5,0,2,3,0
31,Angelica G,4,0,0,0,4
32,Joey,1,0,0,1,0
"""

def get_csv_literal_bar_anticipationsun() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Mike L,87 points,33 points,4 points,21 points,29 points
2,Adam U,63 points,27 points,30 points,5 points,1 points
3,Jarrett Fre,41 points,8 points,2 points,27 points,4 points
4,Roger W,40 points,0 points,1 points,33 points,6 points
5,Paul U,33 points,5 points,18 points,7 points,3 points
6,Tim C,32 points,0 points,0 points,9 points,23 points
7,Damian Atc,30 points,21 points,5 points,4 points,0 points
8,Dawson,27 points,10 points,6 points,6 points,5 points
9,Zach F,21 points,6 points,3 points,10 points,2 points
10,Charlie Tho,19 points,9 points,7 points,3 points,0 points
11,Kevin M,17 points,0 points,0 points,0 points,17 points
12,Orlando,8 points,0 points,0 points,8 points,0 points
13,Josh,4 points,4 points,0 points,0 points,0 points
14,Amar N,3 points,3 points,0 points,0 points,0 points
15,John S,2 points,0 points,0 points,2 points,0 points
16,A.J,1 points,1 points,0 points,0 points,0 points
"""

def get_csv_literal_bar_anticipationtues() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Brandon C,87 points,29 points,7 points,23 points,28 points
2,Tim C,62 points,11 points,19 points,29 points,3 points
3,Jarrett F,51 points,23 points,25 points,3 points,0 points
4,Paul U,51 points,35 points,6 points,5 points,5 points
5,Troy R,48 points,10 points,5 points,17 points,16 points
6,Chris G,40 points,9 points,31 points,0 points,0 points
7,Zach F,33 points,5 points,2 points,4 points,22 points
8,Adam M,14 points,6 points,8 points,0 points,0 points
9,Bonnie,13 points,12 points,1 points,0 points,0 points
10,Damian A,13 points,8 points,4 points,1 points,0 points
11,Roger W,13 points,0 points,3 points,6 points,4 points
12,Dawson,11 points,7 points,0 points,2 points,2 points
13,Mike L,4 points,4 points,0 points,0 points,0 points
14,Lisa,3 points,3 points,0 points,0 points,0 points
15,Tom Z,2 points,2 points,0 points,0 points,0 points
16,Aaron,1 points,1 points,0 points,0 points,0 points
"""

def get_csv_literal_bar_brickyard() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Dave B,99 points,9 points,39 points,36 points,15 points
2,Lori H,80 points,5 points,32 points,8 points,35 points
3,Anthony Sr,66 points,31 points,3 points,30 points,2 points
4,Bartman,65 points,14 points,13 points,9 points,29 points
5,Rob H,58 points,12 points,5 points,24 points,17 points
6,Greg H,54 points,37 points,0 points,7 points,10 points
7,Wyatt,53 points,10 points,26 points,4 points,13 points
8,Pyerre,43 points,8 points,7 points,12 points,16 points
9,Bob R,41 points,0 points,0 points,0 points,41 points
10,Jason H,35 points,0 points,12 points,5 points,18 points
11,Paul C-B,35 points,11 points,15 points,6 points,3 points
12,Rieley,35 points,6 points,2 points,13 points,14 points
13,Evan D,33 points,25 points,0 points,3 points,5 points
14,Bonnie,27 points,13 points,14 points,0 points,0 points
15,Tony S,25 points,7 points,9 points,0 points,9 points
16,Carlee,19 points,2 points,11 points,0 points,6 points
17,Evan J,17 points,0 points,6 points,10 points,1 points
18,Eric S,14 points,4 points,4 points,2 points,4 points
19,Ben,13 points,3 points,1 points,1 points,8 points
20,Jalani,12 points,0 points,0 points,0 points,12 points
21,Richard,11 points,0 points,0 points,11 points,0 points
22,Troy,11 points,0 points,0 points,0 points,11 points
23,Bryan O,10 points,0 points,10 points,0 points,0 points
24,Hunter,8 points,0 points,8 points,0 points,0 points
25,Jawad,7 points,0 points,0 points,0 points,7 points
26,Adrian,1 points,1 points,0 points,0 points,0 points
"""


def get_csv_literal_bar_chatters() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Lori H,79,26,21,13,19
2,Cindy R,67,20,3,19,25
3,Carol,41,14,0,25,2
4,John E,28,0,15,0,13
5,Steel Neil,28,0,27,1,0
6,David,7,3,4,0,0
7,Rob H,5,1,1,2,1
8,Hilda,4,2,2,0,0
"""


def get_csv_literal_bar_corknbarrel() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Troy R,74,31,5,35,3
2,Greg H,70,8,27,5,30
3,Geralyn,69,25,21,23,0
4,Milan,52,1,33,11,7
5,Dmitry,49,4,2,7,36
6,Ben L,40,5,8,3,24
7,Carol,37,7,7,10,13
8,Arsen,33,0,0,29,4
9,Lori H,31,6,9,4,12
10,Pyerre,29,3,3,12,11
11,Jason H,28,19,0,0,9
12,Rob H,25,2,4,9,10
13,Alex,14,0,10,2,2
14,Dr. Z,12,0,1,6,5
15,John E,8,0,0,0,8
16,Tony Sr,8,0,0,8,0
17,Gene D,7,0,0,1,6
18,Gene G,7,0,6,0,1
"""


def get_csv_literal_bar_hosed() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Sean G,50 points,2 points,35 points,6 points,7 points
2,Troy R,49 points,23 points,10 points,10 points,6 points
3,Geralyn,46 points,29 points,1 points,7 points,9 points
4,Mason,45 points,6 points,8 points,4 points,27 points
5,Tekoya,44 points,0 points,23 points,0 points,21 points
6,Greg S,43 points,8 points,5 points,22 points,8 points
7,AJ,40 points,35 points,0 points,0 points,5 points
8,Mike M,34 points,11 points,12 points,11 points,0 points
9,Rob H.,33 points,0 points,0 points,0 points,33 points
10,Ahmad B,29 points,7 points,3 points,9 points,10 points
"""


def get_csv_literal_bar_lakeside() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Kevin,107 points,13 points,17 points,45 points,32 points
2,John B,89 points,39 points,37 points,13 points,0 points
3,Dave B,69 points,6 points,43 points,12 points,8 points
4,Bartman,67 points,12 points,20 points,22 points,13 points
5,Bobby,66 points,14 points,31 points,9 points,12 points
6,Jaye S,64 points,33 points,3 points,19 points,9 points
7,Tony Spenser,63 points,7 points,13 points,17 points,26 points
8,Charlie T,58 points,4 points,0 points,39 points,15 points
9,John H,53 points,10 points,15 points,14 points,14 points
10,Evan J,49 points,16 points,14 points,18 points,1 points
11,Dave J,42 points,5 points,4 points,33 points,0 points
12,Bonnie L,41 points,27 points,8 points,6 points,0 points
13,Aaron C,38 points,0 points,0 points,0 points,38 points
14,Paul C.B,35 points,8 points,11 points,11 points,5 points
15,Lyle,34 points,15 points,10 points,2 points,7 points
16,Carlee,31 points,1 points,0 points,20 points,10 points
17,Caleb G,28 points,0 points,19 points,3 points,6 points
18,Rieley Pet,26 points,3 points,16 points,5 points,2 points
19,Gavin,24 points,0 points,6 points,15 points,3 points
20,Mike L,23 points,11 points,12 points,0 points,0 points
21,Dino,18 points,0 points,18 points,0 points,0 points
22,Wayne,10 points,0 points,0 points,10 points,0 points
23, Enea,9 points,0 points,9 points,0 points,0 points
24,Carl,8 points,0 points,0 points,8 points,0 points
25,Bill,7 points,0 points,0 points,7 points,0 points
26,Katie,4 points,0 points,0 points,4 points,0 points
27,Jeremy,2 points,0 points,2 points,0 points,0 points
28,Emily,1 points,0 points,0 points,1 points,0 points
29,Jared,1 points,0 points,1 points,0 points,0 points
"""


def get_csv_literal_bar_layton() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,John F,73 points,9 points,31 points,10 points,23 points
2,Roger W,56 points,6 points,0 points,21 points,29 points
3,Clayton A,55 points,21 points,0 points,27 points,7 points
4,Donovan B,48 points,27 points,8 points,7 points,6 points
5,Adam M,43 points,3 points,0 points,5 points,35 points
6,Matt P,43 points,33 points,1 points,0 points,9 points
7,Mason,41 points,0 points,25 points,6 points,10 points
8,Cindy R,35 points,5 points,19 points,9 points,2 points
9,Bill E,34 points,0 points,0 points,33 points,1 points
10,Bob R,30 points,8 points,3 points,8 points,11 points
11,John H,27 points,7 points,5 points,3 points,12 points
12, Cristiana,25 points,10 points,6 points,4 points,5 points
13,Jordan H,9 points,1 points,0 points,0 points,8 points
14,Ben D,8 points,2 points,2 points,1 points,3 points
15,Dino,7 points,0 points,7 points,0 points,0 points
16,Caleb G,6 points,0 points,0 points,2 points,4 points
17,Josh J,4 points,4 points,0 points,0 points,0 points
"""


def get_csv_literal_bar_mavricks() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Greg S,69 points,5 points,27 points,4 points,33 points
2,Brian P,66 points,11 points,33 points,12 points,10 points
3,Jeremy k,61 points,22 points,5 points,25 points,9 points
4,John S,56 points,34 points,8 points,9 points,5 points
5,Troy R,53 points,1 points,0 points,31 points,21 points
6,Joe G,48 points,9 points,2 points,37 points,0 points
7,John F,46 points,28 points,10 points,8 points,0 points
8,Mike L,42 points,4 points,4 points,7 points,27 points
9,John H,25 points,2 points,9 points,6 points,8 points
10,Amar N,23 points,0 points,21 points,1 points,1 points
11,Ben D,22 points,3 points,0 points,13 points,6 points
12,Caleb G,19 points,0 points,1 points,11 points,7 points
13,Bob R,16 points,7 points,7 points,0 points,2 points
14,Bill E,15 points,10 points,0 points,5 points,0 points
15,Chris M,14 points,0 points,0 points,14 points,0 points
16,Quinn,10 points,0 points,0 points,10 points,0 points
17,Sandy V,8 points,8 points,0 points,0 points,0 points
18,Roger W,6 points,6 points,0 points,0 points,0 points
19,William G,6 points,0 points,6 points,0 points,0 points
20,Pyerre L,5 points,0 points,3 points,2 points,0 points
21,Matt P,4 points,0 points,0 points,0 points,4 points
22,Bonnie,3 points,0 points,0 points,3 points,0 points
23,Veronica,3 points,0 points,0 points,0 points,3 points
"""


def get_csv_literal_bar_southbound() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Mike L,64 points,5 points,11 points,19 points,29 points
2,Paul P,61 points,7 points,6 points,25 points,23 points
3,Bobby C,55 points,21 points,22 points,6 points,6 points
4,Mike T,49 points,10 points,34 points,5 points,0 points
5,Patty T,49 points,33 points,9 points,7 points,0 points
6,Paul S,46 points,8 points,3 points,31 points,4 points
7,Brian P,41 points,9 points,28 points,3 points,1 points
8,Steph E,32 points,27 points,2 points,0 points,3 points
9,Evan J,27 points,4 points,10 points,8 points,5 points
10,Jeremy K,17 points,0 points,0 points,0 points,17 points
11,Bonnie L,12 points,6 points,4 points,2 points,0 points
12,Sandy V,11 points,3 points,8 points,0 points,0 points
13,Katy V,8 points,0 points,5 points,1 points,2 points
14,Joe,7 points,0 points,7 points,0 points,0 points
15,Charlie T,6 points,1 points,0 points,5 points,0 points
16,Brandon I,2 points,2 points,0 points,0 points,0 points
17,Dale,1 points,0 points,1 points,0 points,0 points
"""




def get_csv_literal_bar_tinys() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Cindy R,100 points,26 points,8 points,35 points,31 points
2,Ben D,91 points,32 points,5 points,29 points,25 points
3,Rob H,48 points,0 points,25 points,23 points,0 points
4,Wyatt S,42 points,20 points,6 points,11 points,5 points
5,Paul CB,34 points,5 points,1 points,9 points,19 points
6,Jarrett F,31 points,0 points,31 points,0 points,0 points
6,Troy R,31 points,9 points,4 points,10 points,8 points
7,Joe Graham,19 points,0 points,19 points,0 points,0 points
8,Caleb G,16 points,8 points,0 points,6 points,2 points
9,Aaron C,12 points,0 points,0 points,12 points,0 points
9,Bonnie,12 points,1 points,0 points,7 points,4 points
10,Brian P,10 points,7 points,0 points,0 points,3 points
11,Eric H,9 points,6 points,0 points,2 points,1 points
12,Damian A,7 points,0 points,7 points,0 points,0 points
12,Jason H,7 points,0 points,2 points,5 points,0 points
12,Rickey J,7 points,0 points,0 points,0 points,7 points
13,Carlee J,6 points,0 points,0 points,6 points,0 points
13,JD,6 points,0 points,0 points,0 points,6 points
14,Greg S,5 points,2 points,3 points,0 points,0 points
15,Mike L,4 points,0 points,0 points,4 points,0 points
15,Wendell,4 points,4 points,0 points,0 points,0 points
16,Bob G,3 points,0 points,0 points,3 points,0 points
16,Charlie T,3 points,3 points,0 points,0 points,0 points
17,Robert B,1 points,0 points,0 points,1 points,0 points
"""

def get_csv_literal_bar_witts() -> str:
    return """
,,TOTALS,Round 1,Round 2,Round 3,Round 4
1,Charlie T,55 points,18 points,0 points,12 points,25 points
2,Rieley P,51 points,0 points,20 points,18 points,13 points
3,Gus,40 points,1 points,14 points,24 points,1 points
4,Zach F,33 points,12 points,1 points,1 points,19 points
5,Jarrett F,29 points,24 points,3 points,0 points,2 points
6,Mike T,26 points,0 points,26 points,0 points,0 points
7,Patti T,2 points,0 points,2 points,0 points,0 points
"""


def migrate_start():
    month_id = "202506"  # YYYYMM

    bars = [
        ("alibi_token",        "Alibi",            get_csv_literal_bar_alibi()),
        ("anticipationsun_token", "Anticipation Sun", get_csv_literal_bar_anticipationsun()),
        ("anticipationtues_token","Anticipation Tues", get_csv_literal_bar_anticipationtues()),
        ("brickyard_token",    "Brickyard",        get_csv_literal_bar_brickyard()),
        ("chatters_token",     "Chatters",         get_csv_literal_bar_chatters()),
        ("corknbarrel_token",  "Cork n Barrel",    get_csv_literal_bar_corknbarrel()),
        ("hosed_token",        "Hosed on Brady",   get_csv_literal_bar_hosed()),
        ("lakeside_token",     "Lakeside",         get_csv_literal_bar_lakeside()),
        ("layton_token",       "Layton",           get_csv_literal_bar_layton()),
        ("mavricks_token",     "Mavricks",         get_csv_literal_bar_mavricks()),
        ("southbound_token",   "Southbound",       get_csv_literal_bar_southbound()),
        ("tinys_token",        "Tinys",            get_csv_literal_bar_tinys()),
        ("witts_token",        "Witts",            get_csv_literal_bar_witts()),
    ]

    build_and_store_full_month(month_id, bars)

if __name__ == "__main__":
    migrate_start()
