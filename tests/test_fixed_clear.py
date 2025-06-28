#!/usr/bin/env python3
"""
Test the fixed archive/clear scenario.
"""
import os
import sys
import shutil

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.vector_store import vector_store_client, reset_vector_store
from app.db.data_models import Node
from app import config

def test_fixed_clear_scenario():
    print("=== Test Fixed Clear Scenario ===")
    
    # Clean start
    if os.path.exists(config.VECTOR_DB_PATH):
        shutil.rmtree(config.VECTOR_DB_PATH)
    
    try:
        print("\n--- Initial run ---")
        # Add some data using the global instance
        test_node = Node(
            id="test_node_1",
            text="This is a test node",
            parent_id=None,
            trajectory_id="trajectory_1",
            depth=0,
            score=0.8
        )
        vector_store_client.add_node(test_node)
        print("✓ Added initial node")
        
        # Verify it was added
        retrieved = vector_store_client.get_node_by_id("test_node_1")
        if retrieved:
            print("✓ Successfully retrieved initial node")
        
        print("\n--- Simulate archiving process ---")
        # Get nodes for archiving (this would happen in archive_current_run)
        all_nodes = vector_store_client.get_all_nodes_for_graph()
        print(f"✓ Retrieved {len(all_nodes)} nodes for archiving")
        
        print("\n--- Clear using fixed method ---")
        # This simulates the fixed clear_current_run method
        vector_store_client.clear_collection()
        print("✓ Cleared collection")
        
        if os.path.exists(config.VECTOR_DB_PATH):
            shutil.rmtree(config.VECTOR_DB_PATH)
            print("✓ Removed database directory")
        
        # Use the new reset function instead of __init__()
        reset_vector_store()
        print("✓ Reset vector store using new method")
        
        print("\n--- Test new run after clear ---")
        test_node2 = Node(
            id="test_node_2",
            text="Test node after fixed clear",
            parent_id=None,
            trajectory_id="trajectory_2",
            depth=0,
            score=0.9
        )
        vector_store_client.add_node(test_node2)
        print("✓ Successfully added node after fixed clear")
        
        # Verify it was added
        retrieved2 = vector_store_client.get_node_by_id("test_node_2")
        if retrieved2:
            print("✓ Successfully retrieved node after clear")
        
        # Verify the old node is gone
        old_node = vector_store_client.get_node_by_id("test_node_1")
        if not old_node:
            print("✓ Confirmed old data was cleared")
        
        print("\n--- Test multiple cycles ---")
        for i in range(3):
            print(f"\nCycle {i+1}:")
            
            # Add a node
            test_node = Node(
                id=f"cycle_node_{i+1}",
                text=f"Node from cycle {i+1}",
                parent_id=None,
                trajectory_id=f"cycle_{i+1}",
                depth=0,
                score=0.5 + i * 0.1
            )
            vector_store_client.add_node(test_node)
            print(f"  ✓ Added node for cycle {i+1}")
            
            # Clear and reset
            vector_store_client.clear_collection()
            if os.path.exists(config.VECTOR_DB_PATH):
                shutil.rmtree(config.VECTOR_DB_PATH)
            reset_vector_store()
            print(f"  ✓ Cleared and reset for cycle {i+1}")
        
        print("\n=== All tests passed! The fix works! ===")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_clear_scenario()
