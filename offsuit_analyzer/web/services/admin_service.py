import requests
from offsuit_analyzer import data_service
from offsuit_analyzer import persistence
from offsuit_analyzer.config import config
from .name_tools_service import check_and_log_clashing_player_names

def refresh_rounds_database():
    """Refresh the rounds database with latest data from this months Keep the score API"""
    all_rounds = data_service.get_this_months_rounds_for_bars()  
    persistence.store_rounds(all_rounds)

def email_json_rounds_to_admin():
    persistence.email_json_rounds_backup()

def email_bar_list_to_admin():
    """Email bar list report to admin."""
    data_service.email_bar_list_report()

def run_name_clash_detection():
    """Manually run name clash detection."""
    check_and_log_clashing_player_names()


def trigger_frontend_update():
    """
    Trigger the frontend leaderboards refresh workflow on GitHub via the repository dispatch event.
    
    Dispatches a GitHub workflow that updates the frontend leaderboard caches.
    Uses the GitHub PAT token stored in environment variables (FRONTEND_PAT).
    
    Returns:
        tuple: (success: bool, message: str, status_code: int)
    """
    github_token = config.FRONTEND_PAT
    if not github_token:
        return False, 'GitHub token not configured', 500
    
    # GitHub API endpoint for repository dispatch
    github_url = 'https://api.github.com/repos/jff97/PokerAnalyzerDisplayWebsite/dispatches'
    
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {github_token}',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    payload = {
        'event_type': 'refresh_leaderboards'
    }
    
    try:
        response = requests.post(github_url, json=payload, headers=headers)
        
        if response.status_code == 204:
            # 204 No Content is the success response from GitHub
            return True, 'Frontend workflow dispatched', 200
        else:
            error_msg = f'GitHub API returned {response.status_code}'
            print(f'GitHub API error: {response.status_code} - {response.text}')
            return False, error_msg, 500
            
    except Exception as e:
        error_msg = f'Failed to dispatch workflow: {str(e)}'
        print(f'Error triggering frontend update: {str(e)}')
        return False, error_msg, 500