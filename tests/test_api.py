#!/usr/bin/env python3
"""
Test script for GOT-AI API endpoints
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_status():
    """Test the status endpoint"""
    print("Testing /api/status...")
    response = requests.get(f"{BASE_URL}/api/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_start_analysis():
    """Test starting an analysis"""
    print("\nTesting /api/start...")
    data = {"hypothesis": "Artificial intelligence will transform education in the next decade"}
    response = requests.post(f"{BASE_URL}/api/start", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_graph_data():
    """Test getting graph data"""
    print("\nTesting /api/graph_data...")
    response = requests.get(f"{BASE_URL}/api/graph_data")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Nodes: {len(data.get('nodes', []))}")
    print(f"Links: {len(data.get('links', []))}")
    return response.status_code == 200

def main():
    print("GOT-AI API Test Script")
    print("=" * 30)
    
    # Test basic status
    if not test_status():
        print("❌ Status endpoint failed")
        return
    
    print("✅ Status endpoint working")
    
    # Start an analysis
    if not test_start_analysis():
        print("❌ Start analysis failed")
        return
    
    print("✅ Analysis started successfully")
    
    # Wait a bit for some processing
    print("\n⏳ Waiting 10 seconds for analysis to generate some nodes...")
    time.sleep(10)
    
    # Check graph data
    if not test_graph_data():
        print("❌ Graph data endpoint failed")
        return
    
    print("✅ Graph data endpoint working")
    
    # Test analysis endpoint
    print("\nTesting /api/analysis...")
    response = requests.get(f"{BASE_URL}/api/analysis")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        analysis = response.json()
        print(f"Total nodes: {analysis.get('total_nodes', 'N/A')}")
        print("✅ Analysis endpoint working")
    else:
        print("❌ Analysis endpoint failed")
    
    print("\n🎉 All tests completed! The GOT-AI system is working!")
    print("\n📊 You can now open http://localhost:8000 in your browser to use the full interface!")

if __name__ == "__main__":
    main()
