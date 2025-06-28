#!/usr/bin/env python3
"""
Test to understand the difference between add() and upsert() after database recreation.
"""
import chromadb
import os
import shutil
from sentence_transformers import SentenceTransformer

def test_add_vs_upsert():
    print("=== Add vs Upsert Test ===")
    
    db_path = "/Users/awritrojitbanerjee/Projects/GOTAI/test_add_vs_upsert"
    
    try:
        print("\n--- Test 1: Use add() after database recreation ---")
        
        # Clean start
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        
        os.makedirs(db_path, exist_ok=True)
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection("test_collection")
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode("test text").tolist()
        
        # Use add() instead of upsert()
        collection.add(
            ids=["test_add"],
            embeddings=[embedding],
            documents=["test with add"]
        )
        print("✓ add() works after database recreation")
        
        print("\n--- Test 2: Use upsert() on existing database ---")
        
        # Try upsert on the same collection without recreation
        embedding2 = model.encode("test text 2").tolist()
        collection.upsert(
            ids=["test_upsert"],
            embeddings=[embedding2],
            documents=["test with upsert"]
        )
        print("✓ upsert() works on existing database")
        
        print("\n--- Test 3: Use upsert() after recreation ---")
        
        # Remove and recreate
        del collection
        del client
        shutil.rmtree(db_path)
        
        os.makedirs(db_path, exist_ok=True)
        client2 = chromadb.PersistentClient(path=db_path)
        collection2 = client2.get_or_create_collection("test_collection")
        
        # Try upsert on fresh database
        try:
            collection2.upsert(
                ids=["test_upsert_fresh"],
                embeddings=[embedding],
                documents=["test upsert on fresh db"]
            )
            print("✓ upsert() works on fresh database")
        except Exception as e:
            print(f"✗ upsert() fails on fresh database: {e}")
            
            # Try add() first, then upsert()
            print("\n--- Test 4: Try add() first, then upsert() ---")
            collection2.add(
                ids=["test_add_first"],
                embeddings=[embedding],
                documents=["add first"]
            )
            print("✓ add() works")
            
            collection2.upsert(
                ids=["test_upsert_after_add"],
                embeddings=[embedding2],
                documents=["upsert after add"]
            )
            print("✓ upsert() works after add()")
        
        print("\n=== Test completed ===")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(db_path):
            shutil.rmtree(db_path)

if __name__ == "__main__":
    test_add_vs_upsert()
