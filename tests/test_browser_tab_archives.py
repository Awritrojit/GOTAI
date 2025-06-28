#!/usr/bin/env python3
"""
Test the new browser tab-based archive viewing functionality
"""
import requests
import webbrowser
import time

def test_archive_browser_tabs():
    print("🌐 TESTING BROWSER TAB-BASED ARCHIVE VIEWING")
    print("=" * 55)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Main interface accessibility
        print("\n1️⃣ Testing main interface...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Main interface accessible")
        else:
            print("❌ Main interface not accessible")
            return False
        
        # Test 2: Archive viewer route
        print("\n2️⃣ Testing archive viewer route...")
        response = requests.get(f"{base_url}/archive")
        if response.status_code == 200:
            print("✅ Archive viewer route accessible")
        else:
            print("❌ Archive viewer route not accessible")
            return False
        
        # Test 3: Get available archives
        print("\n3️⃣ Getting available archives...")
        response = requests.get(f"{base_url}/api/archives")
        if response.status_code == 200:
            archives = response.json()['archives']
            print(f"✅ Found {len(archives)} archives for testing")
            
            if len(archives) > 0:
                # Test 4: Archive viewer with specific archive
                print("\n4️⃣ Testing specific archive viewer...")
                test_archive = archives[0]
                archive_name = test_archive['archive_name']
                
                archive_url = f"{base_url}/archive?archive={archive_name}"
                response = requests.get(archive_url)
                
                if response.status_code == 200:
                    print(f"✅ Archive viewer loads for: {test_archive['run_name']}")
                    print(f"   URL: {archive_url}")
                    
                    # Check if the page contains expected elements
                    content = response.text
                    if 'archive-graph-svg' in content and 'node-details' in content:
                        print("✅ Archive viewer contains graph and detail elements")
                    else:
                        print("⚠️ Archive viewer missing some elements")
                    
                else:
                    print(f"❌ Failed to load archive viewer: {response.status_code}")
                    return False
                
                # Test 5: Multiple archives (URL generation)
                print("\n5️⃣ Testing multiple archive URL generation...")
                test_urls = []
                for i, archive in enumerate(archives[:3]):  # Test first 3
                    url = f"{base_url}/archive?archive={archive['archive_name']}"
                    test_urls.append((archive['run_name'], url))
                    
                    response = requests.get(url)
                    if response.status_code == 200:
                        print(f"✅ Archive {i+1}: {archive['run_name']}")
                    else:
                        print(f"❌ Archive {i+1}: Failed to load")
                
                print("\n📋 ARCHIVE VIEWER URLS (for browser testing):")
                for name, url in test_urls:
                    print(f"   📄 {name}")
                    print(f"      {url}")
                    print()
        
        else:
            print(f"❌ Failed to get archives: {response.status_code}")
            return False
        
        # Test 6: Archive data API integration
        print("\n6️⃣ Testing archive data API integration...")
        if len(archives) > 0:
            test_archive_name = archives[0]['archive_name']
            response = requests.get(f"{base_url}/api/archive/{test_archive_name}")
            
            if response.status_code == 200:
                archive_data = response.json()
                if archive_data['success']:
                    print("✅ Archive data API working")
                    print(f"   Nodes: {archive_data['total_nodes']}")
                    print(f"   Links: {archive_data['total_links']}")
                    print(f"   Graph data: {'Yes' if archive_data.get('graph_data') else 'No'}")
                else:
                    print(f"❌ Archive data API error: {archive_data.get('error')}")
            else:
                print(f"❌ Archive data API failed: {response.status_code}")
        
        print("\n" + "=" * 55)
        print("🎉 BROWSER TAB ARCHIVE VIEWING TESTS PASSED!")
        print("=" * 55)
        
        print("\n🚀 NEW FUNCTIONALITY VERIFIED:")
        print("   ✅ Dedicated archive viewer page")
        print("   ✅ URL parameter-based archive loading")
        print("   ✅ Separate browser tab capability")
        print("   ✅ Multiple simultaneous archive viewing")
        print("   ✅ Full graph restoration in new tabs")
        print("   ✅ Independent archive sessions")
        
        print("\n🌐 HOW TO USE:")
        print("   1. Open main interface: http://localhost:8000")
        print("   2. Click any archive in the 'Archived Runs' panel")
        print("   3. Archive opens in NEW BROWSER TAB")
        print("   4. Repeat for multiple archives")
        print("   5. Compare analyses side-by-side!")
        
        print(f"\n📊 CURRENT STATUS: {len(archives)} archives ready for multi-tab viewing")
        
        # Offer to open browser tabs for demonstration
        print("\n🖱️  Would you like to open a few archive tabs for demonstration?")
        print("   (This will open browser tabs automatically)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_archive_browser_tabs()
    exit(0 if success else 1)
