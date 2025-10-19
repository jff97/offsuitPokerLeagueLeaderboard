import json
from io import StringIO
from datetime import datetime
from offsuit_analyzer import email_smtp_service
from offsuit_analyzer.config import config


from offsuit_analyzer.persistence.cosmos_client import get_all_rounds

def _get_rounds_file_object() -> StringIO:
    """Get all rounds as a StringIO file object containing JSON data."""
    rounds = get_all_rounds()
    rounds_data = [round_obj.to_dict() for round_obj in rounds]
    json_string = json.dumps(rounds_data, indent=2, ensure_ascii=False)
    return StringIO(json_string)

def email_json_backup() -> None:
    """Email the rounds data to configured recipients."""
    file_object = _get_rounds_file_object()
    
    list_of_recipient_email_addresses = [config.ADMIN_EMAIL]
    subject = "Poker Rounds Export - AUTOMATED"
    body = "Attached is the latest export of poker rounds from the  production database."
    
    filename = datetime.now().strftime("%Y%m%d") + "_rounds_export.json"
    
    for recipient_email_address in list_of_recipient_email_addresses:
        file_object.seek(0)
        email_smtp_service.send_email(recipient_email_address, subject, body, file_object, filename)

def main():
    email_json_backup()

if __name__ == "__main__":
    main()


