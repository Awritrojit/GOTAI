#!/usr/bin/env python3
"""
Test to understand ChromaDB clear_collection behavior and readonly issue.
"""
import chromadb
import os
import shutil

def test_chromadb_clear_behavior():
    print("=== ChromaDB Clear Behavior Test ===")
    
    actual_path = "/Users/awritrojitbanerjee/Projects/GOTAI/db_data"
    
    # Clean start
    if os.path.exists(actual_path):
        shutil.rmtree(actual_path)
    os.makedirs(actual_path, exist_ok=True)
    
    try:
        print("\n--- Step 1: Create client and collection ---")
        client = chromadb.PersistentClient(path=actual_path)
        collection = client.get_or_create_collection("test_collection")
        
        print("--- Step 2: Add initial data ---")
        collection.add(
            documents=["Hello world 1"],
            ids=["test_id_1"]
        )
        print("✓ Added initial data")
        
        # Check database file permissions
        db_file = os.path.join(actual_path, "chroma.sqlite3")
        if os.path.exists(db_file):
            stat = os.stat(db_file)
            print(f"Database file permissions: {oct(stat.st_mode)}")
            print(f"Database file writable: {os.access(db_file, os.W_OK)}")
        
        print("--- Step 3: Delete collection (like clear_collection) ---")
        client.delete_collection("test_collection")
        print("✓ Deleted collection")
        
        # Check database file permissions after delete
        if os.path.exists(db_file):
            stat = os.stat(db_file)
            print(f"Database file permissions after delete: {oct(stat.st_mode)}")
            print(f"Database file writable after delete: {os.access(db_file, os.W_OK)}")
        
        print("--- Step 4: Recreate collection ---")
        collection = client.get_or_create_collection("test_collection")
        print("✓ Recreated collection")
        
        print("--- Step 5: Try to add data after recreation ---")
        collection.add(
            documents=["Hello world 2"],
            ids=["test_id_2"]
        )
        print("✓ Added data after recreation")
        
        print("--- Step 6: Create new client instance ---")
        client2 = chromadb.PersistentClient(path=actual_path)
        collection2 = client2.get_or_create_collection("test_collection")
        
        print("--- Step 7: Try to add data with new client ---")
        collection2.add(
            documents=["Hello world 3"],
            ids=["test_id_3"]
        )
        print("✓ Added data with new client")
        
        print("\n=== All steps completed successfully! ===")
        
    except Exception as e:
        print(f"\n✗ Error at step: {e}")
        import traceback
        traceback.print_exc()
        
        # Check database file permissions after error
        db_file = os.path.join(actual_path, "chroma.sqlite3")
        if os.path.exists(db_file):
            stat = os.stat(db_file)
            print(f"\nDatabase file permissions after error: {oct(stat.st_mode)}")
            print(f"Database file writable after error: {os.access(db_file, os.W_OK)}")

if __name__ == "__main__":
    test_chromadb_clear_behavior()
