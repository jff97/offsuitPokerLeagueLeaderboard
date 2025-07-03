from cosmos_handler import delete_all_documents

if __name__ == "__main__":
    deleted_count = delete_all_documents()
    print(f"Deleted {deleted_count} documents from the collection.")
