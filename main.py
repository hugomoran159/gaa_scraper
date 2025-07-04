#!/usr/bin/env python3
"""
Dublin GAA Scraper - Main Entry Point

Example usage of the Dublin GAA fixtures scraper.
"""

from src.gaa_scraper import DublinGAAScraper
from datetime import datetime, timedelta
import json


def main():
    """Main function demonstrating the scraper usage."""
    print("Dublin GAA Fixtures Scraper")
    print("=" * 40)
    
    # Initialize the scraper
    scraper = DublinGAAScraper()
    
    # Test 1: Get today's fixtures
    print("\n1. Testing today's fixtures...")
    today_fixtures = scraper.get_fixtures()
    
    if today_fixtures.get('success'):
        print("✓ Successfully retrieved today's fixtures")
        print(f"Data type: {type(today_fixtures)}")
        print(f"Keys: {list(today_fixtures.keys())}")
        
        # Show some sample data
        if 'raw_data' in today_fixtures:
            print(f"Raw data length: {len(today_fixtures['raw_data'])} characters")
            print("First 200 characters:")
            print(today_fixtures['raw_data'][:200])
        elif 'fixtures' in today_fixtures:
            print(f"Found {len(today_fixtures['fixtures'])} fixtures")
    else:
        print(f"✗ Failed: {today_fixtures.get('error', 'Unknown error')}")
    
    # Test 2: Try a specific date range
    print("\n2. Testing date range (next 7 days)...")
    today = datetime.now()
    next_week = today + timedelta(days=7)
    
    weekly_fixtures = scraper.get_date_range_fixtures(
        start_date=today.strftime('%Y-%m-%d'),
        end_date=next_week.strftime('%Y-%m-%d'),
        batch_size=3  # Smaller batches for testing
    )
    
    print(f"Retrieved {len(weekly_fixtures)} fixture records")
    
    # Test 3: Try different parameters
    print("\n3. Testing with different parameters...")
    custom_fixtures = scraper.get_fixtures(
        from_date="2025-01-10",
        to_date="2025-01-10",
        code_id="26",  # Football
        is_fixture="1"
    )
    
    if custom_fixtures.get('success'):
        print("✓ Custom parameters worked")
    else:
        print(f"✗ Custom parameters failed: {custom_fixtures.get('error')}")
    
    # Test 4: Save results if we have data
    if weekly_fixtures:
        print("\n4. Saving to CSV...")
        success = scraper.save_to_csv(weekly_fixtures, 'gaa_fixtures_sample.csv')
        if success:
            print("✓ Data saved to gaa_fixtures_sample.csv")
        else:
            print("✗ Failed to save CSV")
    
    print("\n" + "=" * 40)
    print("Scraper testing complete!")


if __name__ == "__main__":
    main()
