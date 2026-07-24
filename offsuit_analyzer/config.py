import os
import socket
from dataclasses import dataclass
import json
import hashlib
import base64

@dataclass
class BarConfig:
    """Configuration for a bar's poker night."""
    token: str
    poker_night: int  # Weekday number: 0=Monday, 1=Tuesday, ..., 6=Sunday


def _derive_fernet_key_from_string(input_string: str) -> str:
    """
    Derive a valid Fernet key from any input string.
    Uses SHA-256 to create 32 bytes, then base64-encodes it.
    Deterministic: same input always produces same key.
    
    Args:
        input_string: Any string (password, passphrase, etc.)
        
    Returns:
        str: A valid Fernet key (44 characters, url-safe base64)
    """
    hash_bytes = hashlib.sha256(input_string.encode()).digest()
    return base64.urlsafe_b64encode(hash_bytes).decode()


class Config:
    def __init__(self):
        self.IS_DEVELOPMENT_ENV = self._get_is_development_environment()
        self.ADMIN_AUTH_TOKEN = os.getenv("ADMIN_AUTH_TOKEN")
        self.OFFSUIT_ADMIN_PASSWORD = os.getenv("OFFSUIT_ADMIN_PASSWORD")
        self.FRONTEND_PAT = os.getenv("FRONTEND_PAT")
        # Derive encryption key from TOKEN_ENCRYPTION_KEY env var (can be any string)
        token_key_input = os.getenv("TOKEN_ENCRYPTION_KEY")
        self.TOKEN_ENCRYPTION_KEY = _derive_fernet_key_from_string(token_key_input) if token_key_input else None
        self.BAR_CONFIGS = self._get_bar_configs_from_json()
        self.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER = 60
        self.MINIMUM_ROUNDS_FOR_BAR_ANALYSIS = 14

        self.POKER_APP_BASE_URL = os.getenv("POKER_APP_BASE_URL")
        self.NAME_TOOL_1_LINK = self.POKER_APP_BASE_URL + "api/nametools/getwarnings"
        self.NAME_TOOL_2_LINK = self.POKER_APP_BASE_URL + "api/nametools/ambiguousnamestool"
        self.NAME_SIMILARITY_THRESHOLD = 79.9
        self.BETA_TRUESKILL = 21
        self.TAU_TRUESKILL = .4
        self.PERCENT_FOR_ITM = 24
        self.PERCENT_FOR_ROI = .24
        self.STEEPNESS_FOR_ROI = 1.06
        self.POKER_TIMEZONE = "America/Chicago"  # Central Time for poker night calculations
        self._set_cosmos_config_items()
        self._set_email_stuff()

    def _get_email_list(self):
        list_of_emails = [self.ADMIN_EMAIL]
        if not self.IS_DEVELOPMENT_ENV:
            list_of_emails.append("ospl2025@gmail.com")
        return list_of_emails

    def _set_email_stuff(self):
        self.FROM_EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS_FOR_SMTP_CLIENT")
        self.EMAIL_APP_PASSWORD = os.getenv("SMTP_APP_KEY_FOR_EMAIL_CLIENT")
        self.SMTP_SERVER = "smtp.gmail.com"
        self.SMTP_PORT = 587
        self.ADMIN_EMAIL = "jicfox7@gmail.com"
        self.LIST_OF_EMAIL_RECIPIENTS_NAME_CLASH = self._get_email_list()
    
    def _set_cosmos_config_items(self):
        self.MONGO_DB_NAME = "offsuitPokerAnalyzerDB"
        self.DATABASE_CONNECTION_STRING = os.getenv("OFFSUIT_ANALYZER_COSMOS_DB_CONNECTION_STRING")

        collection_env_suffix = "Dev" if self.IS_DEVELOPMENT_ENV else "Prod"
        self.ROUNDS_COLLECTION_NAME = "pokerRoundsCollection" + collection_env_suffix
        self.WARNINGS_COLLECTION_NAME = "warningsCollection" + collection_env_suffix
        self.NAME_INFOS_COLLECTION_NAME = "nameClashesCollection" + collection_env_suffix
        self.EXCLUDED_QUALIFIERS_COLLECTION_NAME = "excludedQualifiers" + collection_env_suffix
        self.LOGS_COLLECTION_NAME = "logsCollection" + collection_env_suffix

    

    @staticmethod
    def _get_is_development_environment() -> bool:
        return False
        try:
            return socket.gethostname() == "JohnsPCWin11"
        except Exception:
            return False

    @staticmethod
    def _get_bar_configs_from_json() -> list[BarConfig]:
        try:
            tokens_json_str = os.getenv("KEEP_THE_SCORE_BAR_TOKEN_WEEKNIGHT_PAIRS_JSON")
            bar_config_entries_json = json.loads(tokens_json_str)
            return [BarConfig(**entry) for entry in bar_config_entries_json]
        except Exception as e:
            raise ValueError("Failed to load BAR_CONFIGS from JSON") from e
    


config = Config()  # This is what you import
