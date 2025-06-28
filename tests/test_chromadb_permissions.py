#!/usr/bin/env python3
"""
Simple test to isolate ChromaDB permissions issue.
"""
import chromadb
import os
import tempfile
import shutil

def test_chromadb_permissions():
    print("=== ChromaDB Permissions Test ===")
    
    # Test 1: Use a temporary directory to see if ChromaDB works at all
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\nTest 1: Using temporary directory: {temp_dir}")
        try:
            client = chromadb.PersistentClient(path=temp_dir)
            collection = client.get_or_create_collection("test_collection")
            collection.add(
                documents=["Hello world"],
                ids=["test_id_1"]
            )
            print("✓ ChromaDB works with temporary directory")
        except Exception as e:
            print(f"✗ ChromaDB failed with temporary directory: {e}")
    
    # Test 2: Try with the actual path from config
    actual_path = "/Users/awritrojitbanerjee/Projects/GOTAI/db_data"
    print(f"\nTest 2: Using actual path: {actual_path}")
    
    # Clean up any existing data
    if os.path.exists(actual_path):
        shutil.rmtree(actual_path)
    
    # Create directory and set permissions explicitly
    os.makedirs(actual_path, exist_ok=True)
    os.chmod(actual_path, 0o755)
    
    try:
        client = chromadb.PersistentClient(path=actual_path)
        collection = client.get_or_create_collection("test_collection")
        collection.add(
            documents=["Hello world"],
            ids=["test_id_1"]
        )
        print("✓ ChromaDB works with actual path")
        
        # Check what files were created
        print("\nFiles created:")
        for root, dirs, files in os.walk(actual_path):
            for file in files:
                file_path = os.path.join(root, file)
                stat = os.stat(file_path)
                print(f"  {file_path}: {oct(stat.st_mode)}")
        
    except Exception as e:
        print(f"✗ ChromaDB failed with actual path: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Try with different permissions
    print(f"\nTest 3: Setting directory to 777 permissions")
    if os.path.exists(actual_path):
        shutil.rmtree(actual_path)
    
    os.makedirs(actual_path, exist_ok=True)
    os.chmod(actual_path, 0o777)
    
    try:
        client = chromadb.PersistentClient(path=actual_path)
        collection = client.get_or_create_collection("test_collection")
        collection.add(
            documents=["Hello world"],
            ids=["test_id_1"]
        )
        print("✓ ChromaDB works with 777 permissions")
    except Exception as e:
        print(f"✗ ChromaDB failed with 777 permissions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chromadb_permissions()
