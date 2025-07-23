import os
import socket
from dataclasses import dataclass
import json

@dataclass
class BarConfig:
    """Configuration for a bar's poker night."""
    token: str
    poker_night: int  # Weekday number: 0=Monday, 1=Tuesday, ..., 6=Sunday


class Config:
    def __init__(self):
        self.IS_DEVELOPMENT_ENV = self._get_is_development_environment()
        self.BAR_CONFIGS = self._get_bar_configs_from_json()
        self.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER = 16
        self.LIST_OF_EMAIL_RECIPIENTS_NAME_CLASH = ["jicfox7@gmail.com", "ospl2025@gmail.com"]
        self.POKER_APP_BASE_URL = os.getenv("POKER_APP_BASE_URL")
        self.NAME_TOOL_1_LINK = self.POKER_APP_BASE_URL + "api/nametools/getwarnings"
        self.NAME_TOOL_2_LINK = self.POKER_APP_BASE_URL + "api/nametools/ambiguousnamestool"
        self.NAME_SIMILARITY_THRESHOLD = 79.9
        self.MAX_SIGMA_DISPLAYED_TRUESKILL = 7
        self._set_cosmos_config_items()
        self._set_email_stuff()

    def _set_email_stuff(self):
        self.FROM_EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS_FOR_SMTP_CLIENT")
        self.EMAIL_APP_PASSWORD = os.getenv("SMTP_APP_KEY_FOR_EMAIL_CLIENT")
        self.SMTP_SERVER = "smtp.gmail.com"
        self.SMTP_PORT = 587
    
    def _set_cosmos_config_items(self):
        self.MONGO_DB_NAME = "offsuitPokerAnalyzerDB"
        self.DATABASE_CONNECTION_STRING = os.getenv("OFFSUIT_ANALYZER_COSMOS_DB_CONNECTION_STRING")

        collection_env_suffix = "Dev" if self.IS_DEVELOPMENT_ENV else "Prod"
        self.ROUNDS_COLLECTION_NAME = "pokerRoundsCollection" + collection_env_suffix
        self.LOGS_COLLECTION_NAME = "logsCollection" + collection_env_suffix
        self.WARNINGS_COLLECTION_NAME = "warningsCollection" + collection_env_suffix
        self.NAME_INFOS_COLLECTION_NAME = "nameClashesCollection" + collection_env_suffix

    

    @staticmethod
    def _get_is_development_environment() -> bool:
        try:
            return socket.gethostname() == "JohnsPC"
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
