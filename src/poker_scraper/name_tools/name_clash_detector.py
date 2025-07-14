"""
Service for detecting name clashes in poker tournament data.
"""

from typing import List
from collections import defaultdict
from ..datamodel import Round
from ..persistence import get_all_rounds

def _is_name_formatted_correct(name: str) -> bool:
    normalized = name.strip()
    
    # Skip empty names
    if not normalized:
        return False
    
    if len(normalized.split()) <= 1:
        return False
    
    return True


from rapidfuzz import fuzz

def _names_are_similar(name1: str, name2: str) -> bool:
    """
    Compare two names and return True if they likely refer to the same person.

    Uses fuzzy matching on the first name and requires matching last initials.

    Args:
        name1: str - Name in "First LastInitial" format
        name2: str - Name in "First LastInitial" format

    Returns:
        bool - True if likely the same person, else False
    """
    try:
        name1 = name1.strip().lower()
        name2 = name2.strip().lower()

        first1, last1 = name1.rsplit(" ", 1)
        first2, last2 = name2.rsplit(" ", 1)

        # Last initials must match
        if not last1 or not last2 or last1[0] != last2[0]:
            return False

        # Fuzzy match on first names
        similarity = fuzz.ratio(first1, first2)
        return similarity >= 78
    except ValueError:
        return False



def detect_name_clashes(rounds: List[Round]) -> List[str]:
    """
    Detect name format issues across all rounds.
    
    Args:
        rounds: List of Round objects to analyze
        
    Returns:
        List of strings describing each format issue for logging
    """
    # Build mapping of player names to the bar/date combinations they appear at
    name_to_bar_dates = defaultdict(set)
    
    for round_obj in rounds:
        for player in round_obj.players:
            bar_date = f"{round_obj.bar_name} ({round_obj.round_date})"
            name_to_bar_dates[player.player_name].add(bar_date)
    
    # Check each name for format issues
    clashes = []
    for name in sorted(name_to_bar_dates.keys()):
        if not _is_name_formatted_correct(name):
            bar_dates = name_to_bar_dates[name]
            bar_dates_string = ', '.join(sorted(bar_dates))
            clashes.append(f"Invalid name at {bar_dates_string} name = {name}")
    
    # Check for similar names that might be the same person
    names_list = sorted(name_to_bar_dates.keys())
    for i, name1 in enumerate(names_list):
        for name2 in names_list[i+1:]:
            if _names_are_similar(name1, name2):
                bar_dates1 = name_to_bar_dates[name1]
                bar_dates2 = name_to_bar_dates[name2]
                bar_dates1_string = ', '.join(sorted(bar_dates1))
                bar_dates2_string = ', '.join(sorted(bar_dates2))
                clashes.append(f"Similar names: '{name1}' at {bar_dates1_string} vs '{name2}' at {bar_dates2_string}")
    
    return clashes

# Example usage and testing
def _example_usage():
    print("=== Name Clash Detection Service ===\n")
    
    # Get data
    rounds = get_all_rounds()
    print(f"Analyzing {len(rounds)} rounds...")
    
    # Detect clashes
    clashes = detect_name_clashes(rounds)
    print(f"\nFound {len(clashes)} potential name clashes:")
    for clash_string in clashes:  # Show all clashes
        print(f"  {clash_string}")

if __name__ == "__main__":
    _example_usage()
