#!/usr/bin/env python3

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_existing_data_archive():
    """Test archiving with existing data in the system"""
    
    print("🧪 Testing GOT-AI Archiving with Existing Data")
    print("=" * 50)
    
    # Check current status
    print("1. Checking current status...")
    response = requests.get(f"{BASE_URL}/api/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Status: Running={status['is_running']}, Nodes={status['total_nodes']}")
        
        if status['total_nodes'] > 0:
            print(f"✅ Found {status['total_nodes']} nodes - perfect for testing archiving!")
            
            # Get analysis results
            print("\n2. Getting analysis results...")
            response = requests.get(f"{BASE_URL}/api/analysis")
            if response.status_code == 200:
                analysis = response.json()
                print(f"   Analysis summary:")
                print(f"   - Total nodes: {analysis.get('total_nodes', 0)}")
                print(f"   - Average score: {analysis.get('average_score', 0):.3f}")
                print(f"   - Best trajectory score: {analysis.get('best_trajectory', {}).get('cumulative_score', 0):.3f}")
                print(f"   - Final insight: {analysis.get('best_trajectory', {}).get('final_insight', 'N/A')[:100]}...")
                
            # Test archiving
            print("\n3. Testing archiving functionality...")
            stop_data = {
                "run_name": "Intelligent Agents World Models Analysis"
            }
            
            response = requests.post(f"{BASE_URL}/api/stop", json=stop_data)
            if response.status_code == 200:
                result = response.json()
                print("✅ Successfully archived analysis!")
                print(f"   Archive result: {result}")
                
                # Verify archive listing
                print("\n4. Verifying archived runs...")
                response = requests.get(f"{BASE_URL}/api/archives")
                if response.status_code == 200:
                    archives = response.json()
                    print(f"✅ Found {len(archives.get('archives', []))} archived runs:")
                    for archive in archives.get('archives', []):
                        print(f"   - '{archive['run_name']}'")
                        print(f"     Timestamp: {archive['timestamp']}")
                        print(f"     Hypothesis: {archive['hypothesis'][:60]}...")
                        print(f"     Size: {(archive['size_bytes']/1024):.1f} KB")
                        print()
                        
                # Test fresh start verification
                print("5. Verifying fresh start...")
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
            print("⚠️  No nodes found - need to run analysis first")
    else:
        print(f"❌ Failed to get status: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Archiving test completed!")

if __name__ == "__main__":
    try:
        test_existing_data_archive()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
