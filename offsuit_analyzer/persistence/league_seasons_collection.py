"""League seasons collection operations."""
from offsuit_analyzer.datamodel.poker_season import LeagueSeasonCalendar
from offsuit_analyzer.config import config
from . import cosmos_client


def upsert_calendar(calendar: LeagueSeasonCalendar, year: int) -> None:
    """
    Upsert the league season calendar for a specific year.
    Only one calendar per year is allowed.
    """
    collection = cosmos_client.db[config.LEAGUE_SEASONS_COLLECTION_NAME]

    doc = calendar.to_dict()
    doc["_id"] = str(year)  # Use year as unique ID for the document

    collection.replace_one(
        filter={"_id": str(year)},
        replacement=doc,
        upsert=True
    )


def get_calendar(year: int) -> LeagueSeasonCalendar | None:
    """
    Retrieve the league season calendar for a specific year.
    Returns None if no calendar exists for that year.
    """
    collection = cosmos_client.db[config.LEAGUE_SEASONS_COLLECTION_NAME]
    doc = collection.find_one({"_id": str(year)})
    return LeagueSeasonCalendar.from_dict(doc) if doc else None

def delete_all_seasons():
    """Delete all documents in the league seasons collection. Use with caution!"""
    collection = cosmos_client.db[config.LEAGUE_SEASONS_COLLECTION_NAME]
    result = collection.delete_many({})  # deletes all documents
    print(f"Deleted {result.deleted_count} documents from the seasons collection.")


if __name__ == "__main__":
    confirm = input("Are you sure you want to delete ALL seasons? Type 'YES' to confirm: ")
    if confirm == "YES":
        delete_all_seasons()
    else:
        print("Aborted. No documents were deleted.")
