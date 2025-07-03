#!/usr/bin/env python3

from cosmos_handler import delete_all_data

def main():
    print("⚠️  WARNING: This will delete ALL data in your CosmosDB collection!")
    confirm = input("Type 'YES' to confirm deletion: ").strip()
    if confirm == 'YES':
        delete_all_data()
        print("✅ All data has been deleted.")
    else:
        print("❌ Deletion aborted.")

if __name__ == "__main__":
    main()
