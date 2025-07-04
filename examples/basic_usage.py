#!/usr/bin/env python3
"""
Basic Usage Example for Dublin GAA Scraper

This script demonstrates the most common usage patterns.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gaa_scraper import DublinGAAScraper
from datetime import datetime, timedelta


def basic_example():
    """Basic example: Get fixtures for today."""
    print("Basic Example: Today's Fixtures")
    print("-" * 40)
    
    # Create scraper instance
    scraper = DublinGAAScraper()
    
    # Get today's fixtures
    fixtures = scraper.get_fixtures()
    
    # Display results
    if fixtures.get('success'):
        print("✓ Success!")
        print(f"Retrieved data with keys: {list(fixtures.keys())}")
        
        if 'raw_data' in fixtures:
            print(f"Raw HTML/data length: {len(fixtures['raw_data'])} characters")
    else:
        print(f"✗ Error: {fixtures.get('error')}")


def date_range_example():
    """Example: Get fixtures for a specific date range."""
    print("\nDate Range Example: Next Week")
    print("-" * 40)
    
    scraper = DublinGAAScraper()
    
    # Calculate date range
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"Fetching fixtures from {start_date} to {end_date}")
    
    # Get fixtures for the range
    fixtures = scraper.get_date_range_fixtures(start_date, end_date)
    
    print(f"Found {len(fixtures)} fixture records")
    
    # Save to CSV if we have data
    if fixtures:
        success = scraper.save_to_csv(fixtures, 'weekly_fixtures.csv')
        if success:
            print("✓ Saved to weekly_fixtures.csv")


def specific_competition_example():
    """Example: Get fixtures for specific competitions."""
    print("\nSpecific Competition Example")
    print("-" * 40)
    
    scraper = DublinGAAScraper()
    
    # Football competitions
    football_fixtures = scraper.get_specific_competitions(['26'])
    
    print("Football competition results:")
    for code, result in football_fixtures.items():
        print(f"  Competition {code}: {'Success' if result.get('success') else 'Failed'}")


if __name__ == "__main__":
    basic_example()
    date_range_example()
    specific_competition_example()
    print("\nBasic usage examples complete!") 