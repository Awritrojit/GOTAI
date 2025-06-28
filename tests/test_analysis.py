#!/usr/bin/env python3

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_simple_analysis():
    """Test if the analysis actually runs and generates nodes"""
    
    print("🧪 Testing if analysis actually generates nodes")
    print("=" * 50)
    
    # Clear any existing data first
    print("1. Clearing existing data...")
    response = requests.post(f"{BASE_URL}/api/clear")
    print(f"   Clear response: {response.status_code}")
    
    # Start analysis
    print("\n2. Starting analysis...")
    start_data = {
        "hypothesis": "Artificial intelligence will transform education"
    }
    
    response = requests.post(f"{BASE_URL}/api/start", json=start_data)
    if response.status_code == 200:
        print("✅ Analysis started successfully")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Failed to start analysis: {response.status_code}")
        return
    
    # Monitor for a longer period
    for i in range(6):  # Check every 10 seconds for 1 minute
        time.sleep(10)
        print(f"\n3.{i+1} Checking status after {(i+1)*10} seconds...")
        
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   Status: Running={status['is_running']}, Nodes={status['total_nodes']}")
            
            if status['total_nodes'] > 0:
                print("✅ Nodes are being generated!")
                break
        else:
            print(f"❌ Failed to get status: {response.status_code}")
    
    # Final check
    print("\n4. Final status check...")
    response = requests.get(f"{BASE_URL}/api/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Final Status: Running={status['is_running']}, Nodes={status['total_nodes']}")
        
        if status['total_nodes'] > 0:
            # Test archiving with actual data
            print("\n5. Testing archiving with real data...")
            stop_data = {
                "run_name": "AI Education Analysis"
            }
            
            response = requests.post(f"{BASE_URL}/api/stop", json=stop_data)
            if response.status_code == 200:
                result = response.json()
                print("✅ Successfully archived run!")
                print(f"   Archive result: {result}")
                
                # Check archives
                print("\n6. Checking archived runs...")
                response = requests.get(f"{BASE_URL}/api/archives")
                if response.status_code == 200:
                    archives = response.json()
                    print(f"✅ Found {len(archives.get('archives', []))} archived runs")
                    for archive in archives.get('archives', []):
                        print(f"   - '{archive['run_name']}' at {archive['timestamp']}")
            else:
                print(f"❌ Failed to archive: {response.status_code}")
        else:
            print("⚠️  No nodes were generated during the analysis")
    
    print("\n" + "=" * 50)
    print("🎉 Analysis test completed!")

if __name__ == "__main__":
    try:
        test_simple_analysis()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
