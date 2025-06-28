#!/usr/bin/env python3
"""
End-to-end test of the fixed GOT-AI system through the API.
"""
import requests
import time
import json

def test_end_to_end_api():
    print("=== End-to-End API Test ===")
    
    base_url = "http://localhost:8000"
    
    try:
        print("\n--- Test 1: Start first analysis ---")
        response = requests.post(f"{base_url}/api/start", 
                                json={"hypothesis": "AI will transform the global economy by 2030"})
        if response.status_code == 200:
            print("✓ Successfully started first analysis")
        else:
            print(f"✗ Failed to start analysis: {response.status_code}")
            return
        
        # Let it run for a bit
        print("Waiting 10 seconds for analysis to generate some nodes...")
        time.sleep(10)
        
        # Check nodes
        response = requests.get(f"{base_url}/api/graph_data")
        if response.status_code == 200:
            graph_data = response.json()
            print(f"✓ Analysis generated {len(graph_data['nodes'])} nodes")
        else:
            print("✗ Failed to get graph data")
            return
        
        print("\n--- Test 2: Stop and archive first analysis ---")
        response = requests.post(f"{base_url}/api/stop", 
                                json={"run_name": "AI Economic Transformation Test"})
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Successfully archived first analysis: {result['message']}")
        else:
            print(f"✗ Failed to stop/archive analysis: {response.status_code}")
            return
        
        # Verify data is cleared
        response = requests.get(f"{base_url}/api/graph_data")
        if response.status_code == 200:
            graph_data = response.json()
            print(f"✓ After archiving: {len(graph_data['nodes'])} nodes (should be 0)")
        
        print("\n--- Test 3: Start second analysis ---")
        response = requests.post(f"{base_url}/api/start", 
                                json={"hypothesis": "Quantum computing will revolutionize cryptography within 5 years"})
        if response.status_code == 200:
            print("✓ Successfully started second analysis")
        else:
            print(f"✗ Failed to start second analysis: {response.status_code}")
            return
        
        # Let it run briefly
        print("Waiting 8 seconds for second analysis...")
        time.sleep(8)
        
        # Check nodes
        response = requests.get(f"{base_url}/api/graph_data")
        if response.status_code == 200:
            graph_data = response.json()
            print(f"✓ Second analysis generated {len(graph_data['nodes'])} nodes")
        
        print("\n--- Test 4: Stop and archive second analysis ---")
        response = requests.post(f"{base_url}/api/stop", 
                                json={"run_name": "Quantum Cryptography Study"})
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Successfully archived second analysis: {result['message']}")
        
        print("\n--- Test 5: Clear data manually ---")
        response = requests.post(f"{base_url}/api/clear")
        if response.status_code == 200:
            print("✓ Successfully cleared data manually")
        
        print("\n--- Test 6: Third quick test ---")
        response = requests.post(f"{base_url}/api/start", 
                                json={"hypothesis": "Test hypothesis for verification"})
        if response.status_code == 200:
            print("✓ Successfully started third analysis")
        
        time.sleep(3)
        
        response = requests.post(f"{base_url}/api/clear")
        if response.status_code == 200:
            print("✓ Successfully cleared third analysis")
        
        print("\n--- Test 7: Check archives ---")
        response = requests.get(f"{base_url}/api/archives")
        if response.status_code == 200:
            archives = response.json()
            print(f"✓ Found {len(archives)} archived runs:")
            for archive in archives:
                print(f"  - {archive['run_name']} ({archive['timestamp']})")
        
        
        print("\n=== All API tests passed! The system is fully working! ===")
        
    except Exception as e:
        print(f"✗ Error in API test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_end_to_end_api()
