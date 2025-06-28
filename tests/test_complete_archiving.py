#!/usr/bin/env python3

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_archiving_with_working_analysis():
    """Test the complete archiving workflow with a working analysis"""
    
    print("🧪 Testing GOT-AI Complete Archiving Workflow")
    print("=" * 60)
    
    # Step 1: Clear any existing data
    print("\n1. Clearing existing data...")
    response = requests.post(f"{BASE_URL}/api/clear")
    print(f"   Clear response: {response.status_code}")
    
    # Step 2: Start analysis
    print("\n2. Starting analysis...")
    start_data = {
        "hypothesis": "Social media algorithms influence democratic discourse and voter behavior"
    }
    
    response = requests.post(f"{BASE_URL}/api/start", json=start_data)
    if response.status_code == 200:
        print("✅ Analysis started successfully")
        result = response.json()
        print(f"   Response: {result}")
    else:
        print(f"❌ Failed to start analysis: {response.status_code}")
        return
    
    # Step 3: Monitor analysis progress
    print("\n3. Monitoring analysis progress...")
    max_wait = 60  # Wait up to 60 seconds
    check_interval = 5  # Check every 5 seconds
    
    for i in range(0, max_wait, check_interval):
        time.sleep(check_interval)
        
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   {i+check_interval}s: Running={status['is_running']}, Nodes={status['total_nodes']}")
            
            # If analysis stopped and we have nodes, break
            if not status['is_running'] and status['total_nodes'] > 0:
                print(f"✅ Analysis completed with {status['total_nodes']} nodes!")
                break
            elif not status['is_running'] and status['total_nodes'] == 0:
                print("⚠️  Analysis stopped but no nodes generated")
                break
                
        else:
            print(f"❌ Failed to get status: {response.status_code}")
    
    # Step 4: Get final status
    print("\n4. Getting final analysis status...")
    response = requests.get(f"{BASE_URL}/api/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Final Status: Running={status['is_running']}, Nodes={status['total_nodes']}")
        
        if status['total_nodes'] > 0:
            # Step 5: Get analysis results
            print("\n5. Getting analysis results...")
            response = requests.get(f"{BASE_URL}/api/analysis")
            if response.status_code == 200:
                analysis = response.json()
                print(f"   Analysis summary:")
                print(f"   - Total nodes: {analysis.get('total_nodes', 0)}")
                print(f"   - Average score: {analysis.get('average_score', 0):.3f}")
                print(f"   - Best trajectory score: {analysis.get('best_trajectory', {}).get('cumulative_score', 0):.3f}")
                
            # Step 6: Test archiving
            print("\n6. Testing archiving functionality...")
            stop_data = {
                "run_name": "Social Media Democracy Analysis"
            }
            
            response = requests.post(f"{BASE_URL}/api/stop", json=stop_data)
            if response.status_code == 200:
                result = response.json()
                print("✅ Successfully archived analysis!")
                print(f"   Archive result: {result}")
                
                # Step 7: Verify archive listing
                print("\n7. Verifying archived runs...")
                response = requests.get(f"{BASE_URL}/api/archives")
                if response.status_code == 200:
                    archives = response.json()
                    print(f"✅ Found {len(archives.get('archives', []))} archived runs:")
                    for archive in archives.get('archives', []):
                        print(f"   - '{archive['run_name']}'")
                        print(f"     Timestamp: {archive['timestamp']}")
                        print(f"     Hypothesis: {archive['hypothesis'][:60]}...")
                        print(f"     Size: {archive['size_bytes']} bytes")
                        
                # Step 8: Test fresh start
                print("\n8. Testing fresh start...")
                response = requests.get(f"{BASE_URL}/api/status")
                if response.status_code == 200:
                    status = response.json()
                    if status['total_nodes'] == 0:
                        print("✅ Confirmed: Data cleared after archiving - ready for fresh start!")
                    else:
                        print(f"⚠️  Expected 0 nodes after archiving but found {status['total_nodes']}")
                        
            else:
                print(f"❌ Failed to archive: {response.status_code}")
                print(f"   Error: {response.text}")
        else:
            print("❌ No nodes were generated to archive")
    
    print("\n" + "=" * 60)
    print("🎉 Complete archiving workflow test completed!")

if __name__ == "__main__":
    try:
        test_archiving_with_working_analysis()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
