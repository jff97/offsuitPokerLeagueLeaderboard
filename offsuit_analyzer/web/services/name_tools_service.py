from offsuit_analyzer import persistence
from offsuit_analyzer import name_tools

def get_all_warnings_for_display() -> str:
    """Retrieve all warnings formatted for HTML display."""
    list_of_all_warning_strings = persistence.get_all_warnings()
    combined_warnings = "\n".join(list_of_all_warning_strings)
    html_ready = combined_warnings.replace("\n", "<br>")
    return html_ready

def get_ambiguous_names():
    rounds = persistence.get_all_rounds()
    return name_tools.get_ambiguous_names_with_actions(rounds)

def get_all_name_clashes():
    return name_tools.get_all_name_problems_as_string()

def delete_all_name_clashes():
    return name_tools.delete_all_name_clashes()

def check_and_log_clashing_player_names():
    """Check for name clashes and save warnings to database."""
    name_tools.adaptive_name_problem_finder_process()
    
    rounds = persistence.get_all_rounds()
    name_clashes = name_tools.detect_name_clashes(rounds)
    persistence.delete_all_warnings()
    if name_clashes:
        persistence.save_warnings(name_clashes)

def delete_warnings():
    """Delete all warning entries from the database."""
    persistence.delete_all_warnings()
