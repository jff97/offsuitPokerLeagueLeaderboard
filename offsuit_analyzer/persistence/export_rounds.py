import json
import zipfile
from io import BytesIO
from datetime import datetime
from offsuit_analyzer import email_smtp_service
from offsuit_analyzer.config import config


from offsuit_analyzer.persistence.cosmos_client import get_all_rounds

def _create_zipped_json_rounds_data(rounds) -> BytesIO:
    """Convert rounds data to a ZIP file containing formatted JSON.
    
    Args:
        rounds: List of Round objects to be converted to JSON and zipped
    
    Returns:
        BytesIO: A memory buffer containing the ZIP file with JSON data
    """
    rounds_data = [round_obj.to_dict() for round_obj in rounds]
    json_string = json.dumps(rounds_data, separators=(',', ':'), ensure_ascii=False)
    
    # Create a BytesIO object to hold the zipped data
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the JSON string to the ZIP
        json_file_name = datetime.now().strftime("%Y%m%d") + 'rounds_export.json'
        zip_file.writestr(json_file_name, json_string)
    
    zip_buffer.seek(0)
    return zip_buffer

def email_json_rounds_backup() -> None:
    """Email a ZIP file containing rounds data to configured recipients."""
    rounds = get_all_rounds()
    zip_file = _create_zipped_json_rounds_data(rounds)
    
    list_of_recipient_email_addresses = [config.ADMIN_EMAIL]
    subject = "Poker Rounds Export - AUTOMATED"
    body = "Attached is the latest export of poker rounds from the production database."
    
    filename = datetime.now().strftime("%Y%m%d") + "_rounds_export.zip"
    
    for recipient_email_address in list_of_recipient_email_addresses:
        zip_file.seek(0)
        email_smtp_service.send_email(recipient_email_address, subject, body, binary_file_attachment = zip_file, binary_file_name = filename)
