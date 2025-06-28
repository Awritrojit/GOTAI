#!/usr/bin/env python3
"""
Test to reproduce the exact archiving/clearing scenario that causes readonly database.
"""
import os
import sys
import shutil

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.vector_store import VectorStore
from app.db.data_models import Node
from app import config

def test_archive_clear_scenario():
    print("=== Test Archive/Clear Scenario ===")
    
    # Clean start
    if os.path.exists(config.VECTOR_DB_PATH):
        shutil.rmtree(config.VECTOR_DB_PATH)
    
    try:
        print("\n--- Simulate initial run ---")
        # This simulates the global vector_store_client
        vs = VectorStore()
        
        # Add some data
        test_node = Node(
            id="test_node_1",
            text="This is a test node",
            parent_id=None,
            trajectory_id="trajectory_1",
            depth=0,
            score=0.8
        )
        vs.add_node(test_node)
        print("✓ Added initial node")
        
        print("\n--- Simulate archive and clear (original method) ---")
        # This simulates the problematic clear_current_run method
        vs.clear_collection()  # Step 1
        print("✓ Called clear_collection()")
        
        if os.path.exists(config.VECTOR_DB_PATH):  # Step 2
            shutil.rmtree(config.VECTOR_DB_PATH)
            print("✓ Removed database directory")
        
        vs.__init__()  # Step 3 - This is problematic!
        print("✓ Called __init__() on existing instance")
        
        print("\n--- Try to add new data after problematic clear ---")
        test_node2 = Node(
            id="test_node_2",
            text="This is another test node",
            parent_id=None,
            trajectory_id="trajectory_2",
            depth=0,
            score=0.9
        )
        vs.add_node(test_node2)
        print("✓ Successfully added node after problematic clear")
        
    except Exception as e:
        print(f"✗ Error with original method: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50)
    print("Now testing the CORRECT approach...")
    
    try:
        print("\n--- Clean start for correct method ---")
        if os.path.exists(config.VECTOR_DB_PATH):
            shutil.rmtree(config.VECTOR_DB_PATH)
        
        # Create NEW VectorStore instance
        vs_correct = VectorStore()
        
        # Add some data
        test_node3 = Node(
            id="test_node_3",
            text="Test node for correct method",
            parent_id=None,
            trajectory_id="trajectory_3",
            depth=0,
            score=0.7
        )
        vs_correct.add_node(test_node3)
        print("✓ Added initial node with correct method")
        
        print("\n--- Simulate clear with correct method ---")
        # Don't reuse the same instance, create a new one
        if os.path.exists(config.VECTOR_DB_PATH):
            shutil.rmtree(config.VECTOR_DB_PATH)
            print("✓ Removed database directory")
        
        # Create completely new VectorStore instance
        vs_new = VectorStore()
        print("✓ Created new VectorStore instance")
        
        test_node4 = Node(
            id="test_node_4",
            text="Test node after correct clear",
            parent_id=None,
            trajectory_id="trajectory_4",
            depth=0,
            score=0.85
        )
        vs_new.add_node(test_node4)
        print("✓ Successfully added node after correct clear")
        
        print("\n=== Correct method works! ===")
        
    except Exception as e:
        print(f"✗ Error with correct method: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_archive_clear_scenario()
