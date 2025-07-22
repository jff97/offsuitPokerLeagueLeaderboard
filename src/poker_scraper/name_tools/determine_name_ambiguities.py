import re

from collections import defaultdict

def _normalize(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())

def _split_name(name: str):
    """
    Split normalized name into first and last parts.
    Returns (first_name, last_name) where last_name can be empty.
    """
    parts = _normalize(name).split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]

def _determine_name_actions(entries):
    """
    Determine action for each unique normalized player name based on ambiguity.
    
    Returns a dict:
        normalized_name -> (action, related_names, list_of_original_(player, bar))
    """
    norm_to_orig_bar = defaultdict(set)
    for player, bar in entries:
        norm = _normalize(player)
        norm_to_orig_bar[norm].add((player, bar))

    # Group names by first name for similarity checks
    first_to_names = defaultdict(set)
    for norm_name in norm_to_orig_bar:
        first, _ = _split_name(norm_name)
        first_to_names[first].add(norm_name)

    name_actions = {}
    for norm_name in norm_to_orig_bar:
        first, last = _split_name(norm_name)
        variants = first_to_names[first] - {norm_name}

        if last == "" and variants:
            action = "MERGE_INTO"
            related = sorted(variants)
        elif last == "" and not variants:
            action = "ADD_LAST_NAME"
            related = []
        elif last != "" and variants:
            if all(_split_name(v)[1] != "" for v in variants):
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


def _get_sorted_line_items(name_actions, show_keeps):
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

def _get_action_results(entries, show_keeps = True):
    # Adjustable column widths
    name_col_width = 15
    bars_col_width = 125
    action_col_width = 12

    name_actions = _determine_name_actions(entries)

    # For quick lookup of bars per normalized name
    norm_to_orig_bar = defaultdict(set)
    for player, bar in entries:
        norm = _normalize(player)
        norm_to_orig_bar[norm].add((player, bar))

    items = _get_sorted_line_items(name_actions, show_keeps)

    file_string = ""
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

        file_string += line + "\n"

        
    return file_string
    
def get_ambiguous_names_with_actions(rounds):
    entries = []
    for round_obj in rounds:
        for player in round_obj.players:
            entries.append((player.player_name, round_obj.bar_name))

    return _get_action_results(entries, True)
