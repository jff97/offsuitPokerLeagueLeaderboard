"""Tool for exporting bar list with titles from Keep The Score."""
import json
from io import StringIO
from datetime import datetime
from offsuit_analyzer.config import config
from offsuit_analyzer import email_smtp_service
from offsuit_analyzer.data_service import keep_the_score_api_client as api

DAY_MAP = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def _weekday_sort_key(bar_config):
    """Custom sort order: Saturday (5) first, Sunday (6) second, then Monday-Friday (0-4)."""
    poker_night = bar_config.poker_night
    if poker_night == 5:  # Saturday
        return 0
    elif poker_night == 6:  # Sunday
        return 1
    else:  # Monday-Friday
        return poker_night + 2


def _generate_bar_list_report() -> str:
    """Generate a formatted report of all bars with their details.
    
    Returns:
        str: Formatted JSON report of bars
    """
    sorted_bar_configs = sorted(config.BAR_CONFIGS, key=_weekday_sort_key)
    
    bar_data = []
    for bar_config in sorted_bar_configs:
        day_name = DAY_MAP.get(bar_config.poker_night, "Unknown")
        title = api.get_board_title(bar_config.token)
        
        bar_data.append({
            "token": bar_config.token,
            "poker_night": bar_config.poker_night,
            "day": day_name,
            "bar_title": title
        })
    
    return json.dumps(bar_data, indent=2)


def email_bar_list_report() -> None:
    """Email a report of all bars to configured recipients."""
    report_text = _generate_bar_list_report()
    
    subject = "Bar List Export - AUTOMATED"
    body = "Attached is the latest export of poker bar information from Keep The Score."
    
    text_file = StringIO(report_text)
    filename = datetime.now().strftime("%Y%m%d") + "_bar_list_export.json"
    
    for recipient_email_address in config.LIST_OF_EMAIL_RECIPIENTS_NAME_CLASH:
        text_file.seek(0)
        email_smtp_service.send_email(
            recipient_email_address, 
            subject, 
            body, 
            text_file_attachment=text_file, 
            text_file_name=filename
        )


def get_bar_list_with_private_tokens() -> list:
    """Get list of all bars with their private tokens (before encryption).
    
    Returns:
        list: List of bar dictionaries with tokens and bar details
    """
    sorted_bar_configs = sorted(config.BAR_CONFIGS, key=_weekday_sort_key)
    
    bar_data = []
    for bar_config in sorted_bar_configs:
        day_name = DAY_MAP.get(bar_config.poker_night, "Unknown")
        title = api.get_board_title(bar_config.token)
        
        bar_data.append({
            "token": bar_config.token,
            "poker_night": bar_config.poker_night,
            "day": day_name,
            "bar_title": title
        })
    
    return bar_data
