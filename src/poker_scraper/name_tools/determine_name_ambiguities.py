from .. import persistence
import re
from collections import defaultdict

# my steps i think are 
# 1. do all non legacy add last names manually in website for current month
# 2. re run list make sure we got them all and do 1 again if needed
# 3. for legacy do the add last names that are obvious and leave ones that arent obvious
# 4. run the script and make look at repeating 3 if any were missed
# 5. apply safe merge_into steps for legacy
# 6. check manually the script for complex ambiguities like anthony sr and tony sr and tony s
# 7. should not need to do database script merge into operations for current month because it can be taken care of in the website

def normalize(name: str) -> str:
    """Normalize player names to lowercase and single-space separated."""
    return re.sub(r"\s+", " ", name.strip().lower())

def split_name(name: str):
    """
    Split normalized name into first and last parts.
    Returns (first_name, last_name) where last_name can be empty.
    """
    parts = normalize(name).split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]

def determine_name_actions(entries):
    """
    Determine action for each unique normalized player name based on ambiguity.
    
    Returns a dict:
        normalized_name -> (action, related_names, list_of_original_(player, bar))
    """
    norm_to_orig_bar = defaultdict(set)
    for player, bar in entries:
        norm = normalize(player)
        norm_to_orig_bar[norm].add((player, bar))

    # Group names by first name for similarity checks
    first_to_names = defaultdict(set)
    for norm_name in norm_to_orig_bar:
        first, _ = split_name(norm_name)
        first_to_names[first].add(norm_name)

    name_actions = {}
    for norm_name in norm_to_orig_bar:
        first, last = split_name(norm_name)
        variants = first_to_names[first] - {norm_name}

        if last == "" and variants:
            action = "MERGE_INTO"
            related = sorted(variants)
        elif last == "" and not variants:
            action = "ADD_LAST_NAME"
            related = []
        elif last != "" and variants:
            if all(split_name(v)[1] != "" for v in variants):
                action = "KEEP"
                related = []
            else:
                action = "REVIEW"
                related = sorted(variants)
        else:
            action = "KEEP"
            related = []

        name_actions[norm_name] = (action, related, sorted(norm_to_orig_bar[norm_name]))

    return name_actions


def get_sorted_line_items(name_actions, show_keeps):
    items = []

    # Separate entries by action for nicer output order
    for norm_name, (action, related, player_bar_list) in sorted(name_actions.items()):
        if action == "KEEP" and show_keeps:
            items.append((norm_name, action, related, player_bar_list))
    
    for norm_name, (action, related, player_bar_list) in sorted(name_actions.items()):
        if action == "ADD_LAST_NAME":
            items.append((norm_name, action, related, player_bar_list))
        
    for norm_name, (action, related, player_bar_list) in sorted(name_actions.items()):
        if action != "KEEP" and action != "ADD_LAST_NAME":
            items.append((norm_name, action, related, player_bar_list))
    return items

def get_output_file_path():
    import os
    # Determine folder path relative to this file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "temp")
    os.makedirs(output_dir, exist_ok=True)

    # Full file path
    return os.path.join(output_dir, "ambiguous_names_analysis.txt")

def write_results_to_txt(entries, show_keeps = True):
    """
    Write the analysis results to a text file with columns:
    Name | Bars it appears at | Action | Related info (if any)
    """
    
    # Adjustable column widths
    name_col_width = 15
    bars_col_width = 125
    action_col_width = 12

    name_actions = determine_name_actions(entries)

    # For quick lookup of bars per normalized name
    norm_to_orig_bar = defaultdict(set)
    for player, bar in entries:
        norm = normalize(player)
        norm_to_orig_bar[norm].add((player, bar))

    items = get_sorted_line_items(name_actions, show_keeps)

    output_file_path = get_output_file_path()

    with open(output_file_path, "w") as f:
        # Write entries with related info
        for norm_name, action, related, player_bar_list in items:
            bars = sorted({bar for _, bar in player_bar_list})
            bars_str = "; ".join(bars)

            if action == "ADD_LAST_NAME":
                line = (f"{norm_name:{name_col_width}} | from {bars_str:{bars_col_width}} | "
                        f"{action:{action_col_width}} | Needs full name")
            else:
                related_descriptions = []
                for r in related:
                    related_entries = norm_to_orig_bar.get(r, [])
                    related_bars = sorted({bar for _, bar in related_entries})
                    related_descriptions.append(f"{r} (Bars: {', '.join(related_bars)})")

                if action == "MERGE_INTO":
                    related_str = f"Possible Matches: {', '.join(related_descriptions)}"
                elif action == "REVIEW":
                    related_str = f"Related: {', '.join(related_descriptions)}"
                else:
                    related_str = ""

                line = f"{norm_name:{name_col_width}} | from {bars_str:{bars_col_width}} | {action:{action_col_width}}"
                if related_str:
                    line += f" | {related_str}"

            f.write(line + "\n")

    print(f"Analysis written to {output_file_path}")
    
if __name__ == "__main__":
    rounds = persistence.get_all_rounds() 
    # Flatten rounds to get player-bar pairs
    entries = []
    for round_obj in rounds:
        for player in round_obj.players:
            entries.append((player.player_name, round_obj.bar_name))

    write_results_to_txt(entries, True)
    print("Analysis written to ambiguous_names_analysis.txt")
