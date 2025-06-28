#!/usr/bin/env python3
"""
Completely isolated test to check ChromaDB behavior without our modules.
"""
import chromadb
import os
import shutil
from sentence_transformers import SentenceTransformer

def test_isolated_chromadb():
    print("=== Isolated ChromaDB Test ===")
    
    db_path = "/Users/awritrojitbanerjee/Projects/GOTAI/test_isolated_db"
    
    # Clean start
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    
    try:
        print("\n--- Test 1: Create fresh database ---")
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection("test_collection")
        
        # Add some data
        collection.add(
            documents=["Hello world"],
            ids=["test_1"]
        )
        print("✓ Created and added data to fresh database")
        
        print("\n--- Test 2: Close and reopen ---")
        # Simulate closing and reopening (like what happens in our app)
        del collection
        del client
        
        client2 = chromadb.PersistentClient(path=db_path)
        collection2 = client2.get_or_create_collection("test_collection")
        
        collection2.add(
            documents=["Hello world 2"],
            ids=["test_2"]
        )
        print("✓ Reopened database and added more data")
        
        print("\n--- Test 3: Clear collection and add data ---")
        # Clear collection and try to add data
        client2.delete_collection("test_collection")
        collection3 = client2.get_or_create_collection("test_collection")
        
        collection3.add(
            documents=["Hello world 3"],
            ids=["test_3"]
        )
        print("✓ Cleared collection and added new data")
        
        print("\n--- Test 4: Test with SentenceTransformer (like our app) ---")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode("test text").tolist()
        
        collection3.upsert(
            ids=["test_with_embedding"],
            embeddings=[embedding],
            documents=["test with embedding"]
        )
        print("✓ Added data with embeddings")
        
        print("\n--- Test 5: Simulate our exact scenario ---")
        # This simulates what our VectorStore does
        del collection3
        del client2
        
        # Remove database files (like clear_current_run does)
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
            print("✓ Removed database directory")
        
        # Create new client (like VectorStore.__init__ does)
        os.makedirs(db_path, exist_ok=True)
        client3 = chromadb.PersistentClient(path=db_path)
        collection4 = client3.get_or_create_collection("test_collection")
        
        # Try to add data with embeddings (like our app does)
        collection4.upsert(
            ids=["final_test"],
            embeddings=[embedding],
            documents=["final test"]
        )
        print("✓ Successfully recreated database and added data")
        
        print("\n=== All isolated tests passed! ===")
        
    except Exception as e:
        print(f"✗ Error in isolated test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(db_path):
            shutil.rmtree(db_path)

if __name__ == "__main__":
    test_isolated_chromadb()
