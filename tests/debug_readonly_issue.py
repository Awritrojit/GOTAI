#!/usr/bin/env python3
"""
Debug script to reproduce and understand the readonly database issue.
"""
import os
import sys
import shutil
import time

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.vector_store import VectorStore
from app.db.data_models import Node
from app import config

def test_database_operations():
    print("=== Debug: ChromaDB Readonly Issue ===")
    
    # Clean up any existing database
    if os.path.exists(config.VECTOR_DB_PATH):
        print(f"Removing existing database at: {config.VECTOR_DB_PATH}")
        shutil.rmtree(config.VECTOR_DB_PATH)
    
    print(f"Database path: {config.VECTOR_DB_PATH}")
    print(f"Collection name: {config.COLLECTION_NAME}")
    
    try:
        # Test 1: Initial creation
        print("\n--- Test 1: Initial VectorStore creation ---")
        vs1 = VectorStore()
        
        # Add a test node
        test_node = Node(
            id="test_node_1",
            text="This is a test node",
            parent_id=None,
            trajectory_id="trajectory_1",
            depth=0,
            score=0.8
        )
        
        vs1.add_node(test_node)
        print("✓ Successfully added test node")
        
        # Verify node exists
        retrieved_node = vs1.get_node_by_id("test_node_1")
        if retrieved_node:
            print("✓ Successfully retrieved test node")
        else:
            print("✗ Failed to retrieve test node")
        
        # Check database files
        print("\n--- Database files after creation ---")
        for root, dirs, files in os.walk(config.VECTOR_DB_PATH):
            for file in files:
                file_path = os.path.join(root, file)
                stat = os.stat(file_path)
                print(f"File: {file_path}")
                print(f"  Permissions: {oct(stat.st_mode)}")
                print(f"  Writable: {os.access(file_path, os.W_OK)}")
        
        print("\n--- Test 2: Clear collection ---")
        vs1.clear_collection()
        print("✓ Successfully cleared collection")
        
        print("\n--- Test 3: Create new VectorStore instance ---")
        vs2 = VectorStore()
        
        # Try to add another node
        test_node2 = Node(
            id="test_node_2",
            text="This is another test node",
            parent_id=None,
            trajectory_id="trajectory_2",
            depth=0,
            score=0.9
        )
        
        vs2.add_node(test_node2)
        print("✓ Successfully added second test node")
        
        print("\n--- Test 4: Another clear operation ---")
        vs2.clear_collection()
        print("✓ Successfully cleared collection again")
        
        print("\n--- Test 5: Third VectorStore instance ---")
        vs3 = VectorStore()
        
        test_node3 = Node(
            id="test_node_3",
            text="This is a third test node",
            parent_id=None,
            trajectory_id="trajectory_3",
            depth=0,
            score=0.85
        )
        
        vs3.add_node(test_node3)
        print("✓ Successfully added third test node")
        
        print("\n=== All tests passed! ===")
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        
        # Check database files and permissions after error
        print("\n--- Database files after error ---")
        if os.path.exists(config.VECTOR_DB_PATH):
            for root, dirs, files in os.walk(config.VECTOR_DB_PATH):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        stat = os.stat(file_path)
                        print(f"File: {file_path}")
                        print(f"  Permissions: {oct(stat.st_mode)}")
                        print(f"  Writable: {os.access(file_path, os.W_OK)}")

if __name__ == "__main__":
    test_database_operations()
