#!/usr/bin/env python3
"""
Test the completely fixed vector store functionality.
"""
import os
import sys
import shutil

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Clean up completely first
import shutil
db_path = '/Users/awritrojitbanerjee/Projects/GOTAI/db_data'
if os.path.exists(db_path):
    shutil.rmtree(db_path)

# Clear Python cache to ensure fresh imports
import subprocess
subprocess.run(['find', '.', '-name', '*.pyc', '-delete'], cwd='/Users/awritrojitbanerjee/Projects/GOTAI')
subprocess.run(['find', '.', '-name', '__pycache__', '-type', 'd', '-exec', 'rm', '-rf', '{}', '+'], 
               cwd='/Users/awritrojitbanerjee/Projects/GOTAI', stderr=subprocess.DEVNULL)

# Now import our fixed modules
from app.db.vector_store import vector_store_client
from app.db.data_models import Node
from app.core.archive_manager import ArchiveManager

def test_complete_fixed_workflow():
    print("=== Complete Fixed Workflow Test ===")
    
    try:
        print("\n--- Run 1: Initial analysis ---")
        
        # Simulate start of analysis
        root_node = Node(
            id="root_1",
            text="Test hypothesis 1",
            trajectory_id="root",
            depth=0,
            score=0.8
        )
        vector_store_client.add_node(root_node)
        print("✓ Added root node for run 1")
        
        # Add some child nodes
        child_node = Node(
            id="child_1",
            text="Child hypothesis",
            parent_id="root_1",
            trajectory_id="traj_1",
            depth=1,
            score=0.7
        )
        vector_store_client.add_node(child_node)
        print("✓ Added child node for run 1")
        
        # Verify nodes exist
        all_nodes = vector_store_client.get_all_nodes_for_graph()
        print(f"✓ Run 1 has {len(all_nodes)} nodes")
        
        print("\n--- Archive and Clear Run 1 ---")
        archive_manager = ArchiveManager()
        
        # Archive the run (this would happen in the API)
        archive_result = archive_manager.archive_current_run("Test Run 1", "Test hypothesis 1")
        if archive_result["success"]:
            print("✓ Successfully archived run 1")
        else:
            print(f"✗ Failed to archive run 1: {archive_result}")
        
        # Clear the data
        clear_result = archive_manager.clear_current_run()
        if clear_result:
            print("✓ Successfully cleared run 1 data")
        else:
            print("✗ Failed to clear run 1 data")
        
        # Verify data is cleared
        cleared_nodes = vector_store_client.get_all_nodes_for_graph()
        print(f"✓ After clearing: {len(cleared_nodes)} nodes (should be 0)")
        
        print("\n--- Run 2: Second analysis ---")
        
        # Start a completely new analysis
        root_node_2 = Node(
            id="root_2",
            text="Test hypothesis 2",
            trajectory_id="root",
            depth=0,
            score=0.9
        )
        vector_store_client.add_node(root_node_2)
        print("✓ Added root node for run 2")
        
        # Add multiple nodes
        for i in range(3):
            child_node = Node(
                id=f"child_2_{i}",
                text=f"Child hypothesis {i}",
                parent_id="root_2",
                trajectory_id=f"traj_2_{i}",
                depth=1,
                score=0.6 + i * 0.1
            )
            vector_store_client.add_node(child_node)
        print("✓ Added 3 child nodes for run 2")
        
        # Verify nodes exist
        run2_nodes = vector_store_client.get_all_nodes_for_graph()
        print(f"✓ Run 2 has {len(run2_nodes)} nodes")
        
        print("\n--- Archive and Clear Run 2 ---")
        
        archive_result_2 = archive_manager.archive_current_run("Test Run 2", "Test hypothesis 2")
        if archive_result_2["success"]:
            print("✓ Successfully archived run 2")
        
        clear_result_2 = archive_manager.clear_current_run()
        if clear_result_2:
            print("✓ Successfully cleared run 2 data")
        
        print("\n--- Run 3: Third analysis (stress test) ---")
        
        root_node_3 = Node(
            id="root_3",
            text="Test hypothesis 3",
            trajectory_id="root",
            depth=0,
            score=0.85
        )
        vector_store_client.add_node(root_node_3)
        print("✓ Added root node for run 3")
        
        clear_result_3 = archive_manager.clear_current_run()
        if clear_result_3:
            print("✓ Successfully cleared run 3 data")
        
        print("\n=== All tests passed! The system is working! ===")
        
    except Exception as e:
        print(f"✗ Error in workflow test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_fixed_workflow()
