#!/usr/bin/env python3

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_archiving_functionality():
    """Test the complete archiving workflow"""
    
    print("🧪 Testing GOT-AI Archiving Functionality")
    print("=" * 50)
    
    # Test 1: Start analysis
    print("\n1. Starting analysis...")
    start_data = {
        "hypothesis": "Testing the archiving functionality of GOT-AI framework"
    }
    
    response = requests.post(f"{BASE_URL}/api/start", json=start_data)
    if response.status_code == 200:
        print("✅ Analysis started successfully")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Failed to start analysis: {response.status_code}")
        return
    
    # Wait for some processing
    print("\n2. Waiting for analysis to generate nodes...")
    time.sleep(10)  # Give it time to generate some nodes
    
    # Check status
    print("\n3. Checking status...")
    response = requests.get(f"{BASE_URL}/api/status")
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Status: {status}")
    else:
        print(f"❌ Failed to get status: {response.status_code}")
    
    # Get graph data
    print("\n4. Getting graph data...")
    response = requests.get(f"{BASE_URL}/api/graph_data")
    if response.status_code == 200:
        graph_data = response.json()
        nodes_count = len(graph_data.get('nodes', []))
        print(f"✅ Retrieved graph data with {nodes_count} nodes")
    else:
        print(f"❌ Failed to get graph data: {response.status_code}")
    
    # Test 2: Stop and archive with run name
    print("\n5. Stopping analysis and archiving...")
    stop_data = {
        "run_name": "Test Archive Run"
    }
    
    response = requests.post(f"{BASE_URL}/api/stop", json=stop_data)
    if response.status_code == 200:
        print("✅ Analysis stopped and archived successfully")
        result = response.json()
        print(f"   Response: {result}")
    else:
        print(f"❌ Failed to stop and archive: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 3: List archives
    print("\n6. Listing archived runs...")
    response = requests.get(f"{BASE_URL}/api/archives")
    if response.status_code == 200:
        archives = response.json()
        print(f"✅ Retrieved {len(archives.get('archives', []))} archived runs")
        for archive in archives.get('archives', []):
            print(f"   - {archive['run_name']} ({archive['timestamp']})")
    else:
        print(f"❌ Failed to list archives: {response.status_code}")
    
    # Test 4: Start fresh analysis (should have 0 nodes)
    print("\n7. Starting fresh analysis to test clean slate...")
    start_data = {
        "hypothesis": "This should start with zero nodes - testing fresh start"
    }
    
    response = requests.post(f"{BASE_URL}/api/start", json=start_data)
    if response.status_code == 200:
        print("✅ Fresh analysis started")
        
        # Wait a moment and check status
        time.sleep(3)
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Status: {status}")
            if status['total_nodes'] == 0:
                print("✅ Confirmed: Fresh start with 0 nodes")
            else:
                print(f"⚠️  Expected 0 nodes but found {status['total_nodes']}")
        
        # Stop this test run
        print("\n8. Stopping test analysis...")
        stop_data = {"run_name": ""}  # Empty name, should just clear data
        response = requests.post(f"{BASE_URL}/api/stop", json=stop_data)
        if response.status_code == 200:
            print("✅ Test analysis stopped")
        
    else:
        print(f"❌ Failed to start fresh analysis: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Archiving functionality test completed!")

if __name__ == "__main__":
    try:
        test_archiving_functionality()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
