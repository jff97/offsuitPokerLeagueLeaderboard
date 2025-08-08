import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from pymongo import MongoClient
from offsuit_analyzer.config import config  # absolute import

def find_rounds_by_player(player_name: str, env_suffix: str):
    client = MongoClient(config.DATABASE_CONNECTION_STRING)
    db = client[config.MONGO_DB_NAME]
    collection = db[f"pokerRoundsCollection{env_suffix}"]

    query = { "players.player_name": player_name }
    docs = list(collection.find(query).limit(3))
    total_count = collection.count_documents(query)
    print(f"Found {total_count} total rounds with player '{player_name}' (showing first 3):")
    for doc in docs:
        # Convert ObjectId to string for JSON serialization
        doc['_id'] = str(doc['_id'])
        print(json.dumps(doc, indent=2))
        print("-" * 50)

def update_player_name(old_name: str, new_name: str, env_suffix: str):
    client = MongoClient(config.DATABASE_CONNECTION_STRING)
    db = client[config.MONGO_DB_NAME]
    collection = db[f"pokerRoundsCollection{env_suffix}"]

    # Update only the first matching player element in each document
    filter_query = { "players.player_name": old_name }
    update_query = { "$set": { "players.$.player_name": new_name } }

    result = collection.update_many(filter_query, update_query)
    print(f"Modified {result.modified_count} documents updating '{old_name}' to '{new_name}'.")

def main():
    print("=== Player Name Management Tool ===")
    
    # Ask for environment
    print("Environment:")
    print("1. Development (Dev)")
    print("2. Production (Prod)")
    
    while True:
        env_choice = input("\nSelect environment (1 or 2): ").strip()
        if env_choice in ['1', '2']:
            break
        print("Please enter 1 or 2")
    
    env_suffix = "Dev" if env_choice == '1' else "Prod"
    print(f"Using {env_suffix} environment")
    
    print("\nAction:")
    print("1. Search for player")
    print("2. Update player name")
    
    while True:
        choice = input("\nSelect action (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Please enter 1 or 2")
    
    if choice == '1':
        player_name = input("Enter player name to search for: ").strip()
        if not player_name:
            print("Player name cannot be empty")
            return
        
        print(f"\nSearching for player '{player_name}' in {env_suffix}...")
        find_rounds_by_player(player_name, env_suffix)
        
    elif choice == '2':
        old_name = input("Enter current player name: ").strip()
        if not old_name:
            print("Player name cannot be empty")
            return
            
        new_name = input("Enter new player name: ").strip()
        if not new_name:
            print("New player name cannot be empty")
            return
        
        print(f"\n--- CONFIRMATION ---")
        print(f"Environment: {env_suffix}")
        print(f"This will update ALL occurrences of '{old_name}' to '{new_name}'")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            print(f"\nUpdating '{old_name}' to '{new_name}' in {env_suffix}...")
            update_player_name(old_name, new_name, env_suffix)
            print("Update completed!")
        else:
            print("Update cancelled.")

if __name__ == "__main__":
    main()
