#!/usr/bin/env python3
"""
Test script for Dublin GAA Scraper

Simple test to verify the scraper is working correctly.
"""

from src.gaa_scraper import DublinGAAScraper
import json


def test_basic_functionality():
    """Test basic scraper functionality."""
    print("Testing Dublin GAA Scraper")
    print("=" * 50)
    
    # Initialize scraper
    scraper = DublinGAAScraper()
    
    print(f"Base URL: {scraper.base_url}")
    print(f"Datafeed URL: {scraper.datafeed_url}")
    
    # Test 1: Basic fixtures request
    print("\n1. Testing basic fixtures request...")
    try:
        result = scraper.get_fixtures(
            from_date="2025-07-05",
            to_date="2025-07-05"
        )
        
        print(f"Success: {result.get('success', False)}")
        print(f"Method: {result.get('method', 'api')}")
        print(f"Keys: {list(result.keys())}")
        
        if 'raw_data' in result:
            data_preview = result['raw_data'][:300] if len(result['raw_data']) > 300 else result['raw_data']
            print(f"Raw data preview: {data_preview}")
        
        if 'fixtures' in result:
            print(f"Fixtures found: {len(result['fixtures'])}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Try different approach - check if we can access the main page
    print("\n2. Testing website accessibility...")
    try:
        import requests
        response = requests.get("https://www.dublingaa.ie/mens-football/club-fixtures-results", timeout=10)
        print(f"Main page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Website is accessible")
            print(f"Content length: {len(response.text)} characters")
            
            # Look for any fixture-related content
            content = response.text.lower()
            if 'fixture' in content:
                print("✓ Found 'fixture' in page content")
            if 'datafeed' in content or 'ajax' in content:
                print("✓ Found AJAX/datafeed references")
                
        else:
            print(f"✗ Website returned status {response.status_code}")
            
    except Exception as e:
        print(f"Error accessing website: {e}")
    
    # Test 3: Check if we can find alternative endpoints
    print("\n3. Testing alternative approaches...")
    try:
        # Try the SportLoMo URL we found in the search results
        import requests
        alternative_url = "https://dublingaa.sportlomo.com/fixtures/"
        response = requests.get(alternative_url, timeout=10)
        
        print(f"SportLoMo status: {response.status_code}")
        if response.status_code == 200:
            print("✓ SportLoMo site is accessible")
            print(f"Content length: {len(response.text)} characters")
            
    except Exception as e:
        print(f"Error with SportLoMo: {e}")
    
    print("\n" + "=" * 50)
    print("Test complete!")


if __name__ == "__main__":
    test_basic_functionality() 