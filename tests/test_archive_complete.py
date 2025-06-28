#!/usr/bin/env python3

import requests
import json
import urllib.parse
from pathlib import Path

def test_archive_system():
    base_url = "http://localhost:8000"
    
    print("=== Testing GOT-AI Archive System ===\n")
    
    # Test 1: Check if archives list API works
    print("1. Testing archives list API...")
    try:
        response = requests.get(f"{base_url}/api/archives")
        if response.status_code == 200:
            archives = response.json()
            print(f"   ✓ Found {len(archives['archives'])} archives")
            if archives['archives']:
                test_archive = archives['archives'][0]['archive_name']
                print(f"   ✓ Test archive: {test_archive}")
        else:
            print(f"   ✗ Failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Test 2: Check specific archive API
    print("\n2. Testing specific archive API...")
    try:
        encoded_name = urllib.parse.quote(test_archive)
        response = requests.get(f"{base_url}/api/archive/{encoded_name}")
        if response.status_code == 200:
            archive_data = response.json()
            print(f"   ✓ Archive loaded successfully: {archive_data.get('success', False)}")
            print(f"   ✓ Total nodes: {archive_data.get('total_nodes', 0)}")
            print(f"   ✓ Graph nodes: {len(archive_data.get('graph_data', {}).get('nodes', []))}")
            print(f"   ✓ Graph links: {len(archive_data.get('graph_data', {}).get('links', []))}")
        else:
            print(f"   ✗ Failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Test 3: Check archive viewer HTML page
    print("\n3. Testing archive viewer page...")
    try:
        response = requests.get(f"{base_url}/archive")
        if response.status_code == 200:
            html_content = response.text
            print(f"   ✓ Archive viewer page loads ({len(html_content)} bytes)")
            
            # Check for key elements
            checks = [
                ("D3.js CDN", "d3js.org/d3.v7.min.js" in html_content),
                ("Graph.js script", "/static/js/graph.js" in html_content),
                ("Archive title element", 'id="archive-title-text"' in html_content),
                ("Graph container", 'id="archive-graph-svg"' in html_content),
                ("Node details", 'id="node-details"' in html_content),
                ("ArchiveViewer class", "class ArchiveViewer" in html_content),
            ]
            
            for check_name, result in checks:
                status = "✓" if result else "✗"
                print(f"     {status} {check_name}")
                
        else:
            print(f"   ✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Check static files
    print("\n4. Testing static file access...")
    static_files = [
        "/static/js/graph.js",
        "/static/css/style.css"
    ]
    
    for file_path in static_files:
        try:
            response = requests.head(f"{base_url}{file_path}")
            status = "✓" if response.status_code == 200 else "✗"
            print(f"   {status} {file_path} ({response.status_code})")
        except Exception as e:
            print(f"   ✗ {file_path} - Error: {e}")
    
    # Test 5: Check archive viewer with parameters
    print("\n5. Testing archive viewer with parameters...")
    try:
        encoded_name = urllib.parse.quote(test_archive)
        response = requests.get(f"{base_url}/archive?archive={encoded_name}")
        if response.status_code == 200:
            print(f"   ✓ Archive viewer with parameters loads")
        else:
            print(f"   ✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print(f"\n=== Test Complete ===")
    print(f"Test archive URL: {base_url}/archive?archive={urllib.parse.quote(test_archive)}")

if __name__ == "__main__":
    test_archive_system()
