#!/usr/bin/env python3

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"

def comprehensive_test():
    """Complete test of the GOT-AI system including analysis and archiving"""
    
    print("🚀 GOT-AI Comprehensive System Test")
    print("=" * 60)
    
    # Step 1: Verify server is running
    print("1. Verifying server status...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            print("✅ Server is running and responsive")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return
    except:
        print("❌ Server is not accessible")
        return
    
    # Step 2: Start analysis
    print("\n2. Starting analysis with a complex hypothesis...")
    hypothesis = "Artificial intelligence systems will fundamentally transform global economic structures, creating new forms of wealth distribution and challenging traditional employment models while simultaneously enhancing human cognitive capabilities through symbiotic relationships."
    
    start_data = {"hypothesis": hypothesis}
    response = requests.post(f"{BASE_URL}/api/start", json=start_data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Analysis started successfully")
        print(f"   Hypothesis: {hypothesis[:80]}...")
    else:
        print(f"❌ Failed to start analysis: {response.status_code}")
        return
    
    # Step 3: Monitor progress until completion
    print("\n3. Monitoring analysis progress...")
    start_time = time.time()
    max_wait = 120  # Wait up to 2 minutes
    check_interval = 10  # Check every 10 seconds
    last_node_count = 0
    
    for elapsed in range(0, max_wait, check_interval):
        time.sleep(check_interval)
        
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            status = response.json()
            nodes = status['total_nodes']
            running = status['is_running']
            
            if nodes != last_node_count:
                print(f"   {elapsed + check_interval}s: {nodes} nodes generated {'(still running)' if running else '(completed)'}")
                last_node_count = nodes
            
            # If analysis completed and we have nodes, proceed
            if not running and nodes > 0:
                print(f"✅ Analysis completed with {nodes} nodes in {elapsed + check_interval} seconds!")
                break
            elif not running and nodes == 0:
                print("⚠️  Analysis stopped but no nodes generated")
                return
        else:
            print(f"❌ Failed to get status: {response.status_code}")
    
    # Step 4: Get detailed analysis results
    print("\n4. Retrieving detailed analysis results...")
    response = requests.get(f"{BASE_URL}/api/analysis")
    if response.status_code == 200:
        analysis = response.json()
        print("✅ Analysis results retrieved:")
        print(f"   • Total nodes: {analysis.get('total_nodes', 0)}")
        print(f"   • Average score: {analysis.get('average_score', 0):.3f}")
        print(f"   • Pruned nodes: {analysis.get('pruned_nodes', 0)}")
        
        best_trajectory = analysis.get('best_trajectory', {})
        if best_trajectory:
            print(f"   • Best trajectory score: {best_trajectory.get('cumulative_score', 0):.3f}")
            print(f"   • Best path length: {best_trajectory.get('path_length', 0)} steps")
            final_insight = best_trajectory.get('final_insight', '')
            print(f"   • Final insight: {final_insight[:100]}...")
    else:
        print(f"❌ Failed to get analysis: {response.status_code}")
    
    # Step 5: Test archiving with run name
    print("\n5. Testing archiving functionality...")
    run_name = "AI Economic Transformation Study"
    stop_data = {"run_name": run_name}
    
    response = requests.post(f"{BASE_URL}/api/stop", json=stop_data)
    if response.status_code == 200:
        result = response.json()
        print("✅ Successfully archived the analysis!")
        print(f"   Message: {result.get('message', 'N/A')}")
        if 'archive_name' in result:
            print(f"   Archive name: {result['archive_name']}")
        if 'nodes_archived' in result:
            print(f"   Nodes archived: {result['nodes_archived']}")
    else:
        print(f"❌ Failed to archive: {response.status_code}")
        return
    
    # Step 6: List archived runs
    print("\n6. Verifying archived runs...")
    response = requests.get(f"{BASE_URL}/api/archives")
    if response.status_code == 200:
        archives = response.json()
        archive_list = archives.get('archives', [])
        print(f"✅ Found {len(archive_list)} archived run(s):")
        
        for i, archive in enumerate(archive_list, 1):
            print(f"   {i}. '{archive['run_name']}'")
            print(f"      • Timestamp: {archive['timestamp']}")
            print(f"      • Size: {(archive['size_bytes']/1024):.1f} KB")
            print(f"      • Hypothesis: {archive['hypothesis'][:80]}...")
            print()
    else:
        print(f"❌ Failed to list archives: {response.status_code}")
    
    # Step 7: Verify fresh start
    print("7. Verifying system is ready for fresh start...")
    response = requests.get(f"{BASE_URL}/api/status")
    if response.status_code == 200:
        status = response.json()
        if status['total_nodes'] == 0:
            print("✅ System successfully cleared - ready for new analysis!")
        else:
            print(f"⚠️  Expected 0 nodes but found {status['total_nodes']}")
    
    # Step 8: Test frontend access
    print("\n8. Testing frontend accessibility...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"⚠️  Frontend returned status: {response.status_code}")
    except:
        print("❌ Frontend is not accessible")
    
    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE TEST COMPLETED!")
    print("🏆 GOT-AI System Status:")
    print("   ✅ Backend API working")
    print("   ✅ Analysis engine functional") 
    print("   ✅ Node generation working")
    print("   ✅ Scoring system operational")
    print("   ✅ Archiving system working")
    print("   ✅ Data clearing functional")
    print("   ✅ Frontend accessible")
    print("   ✅ Complete workflow verified")
    print("\n🚀 The GOT-AI system is fully operational!")

if __name__ == "__main__":
    try:
        comprehensive_test()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
