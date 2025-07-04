#!/usr/bin/env python3
"""
Practical Demo for Dublin GAA Scraper

This script demonstrates practical usage with current fixture data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gaa_scraper import DublinGAAScraper
from datetime import datetime, timedelta
import json


def practical_demo():
    """Practical demonstration of the scraper."""
    print("Dublin GAA Scraper - Practical Demo")
    print("=" * 50)
    
    scraper = DublinGAAScraper()
    
    # Demo 1: Get fixtures for this weekend
    print("\n1. Getting fixtures for this weekend...")
    today = datetime.now()
    
    # Find next Saturday (or this Saturday if today is before Saturday)
    days_until_saturday = (5 - today.weekday()) % 7  # Saturday is 5
    if days_until_saturday == 0 and today.weekday() != 5:
        days_until_saturday = 7
    
    saturday = today + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=1)
    
    print(f"Looking for fixtures from {saturday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')}")
    
    weekend_fixtures = scraper.get_fixtures(
        from_date=saturday.strftime('%Y-%m-%d'),
        to_date=sunday.strftime('%Y-%m-%d')
    )
    
    print(f"Result: {weekend_fixtures.get('success', False)}")
    print(f"Source: {weekend_fixtures.get('source', 'unknown')}")
    print(f"Method: {weekend_fixtures.get('method', 'api')}")
    
    if weekend_fixtures.get('fixtures'):
        print(f"Found {len(weekend_fixtures['fixtures'])} fixtures")
        
        # Show first few fixtures as examples
        for i, fixture in enumerate(weekend_fixtures['fixtures'][:3]):
            print(f"\nFixture {i+1}:")
            for key, value in fixture.items():
                print(f"  {key}: {value}")
    else:
        print("No fixtures found for this weekend")
    
    # Demo 2: Search for fixtures in a broader time range
    print(f"\n2. Searching for fixtures in the next month...")
    next_month = today + timedelta(days=30)
    
    monthly_fixtures = scraper.get_date_range_fixtures(
        start_date=today.strftime('%Y-%m-%d'),
        end_date=next_month.strftime('%Y-%m-%d'),
        batch_size=10  # Larger batches for efficiency
    )
    
    print(f"Found {len(monthly_fixtures)} total fixture records")
    
    if monthly_fixtures:
        # Analyze the data
        dates = set()
        competitions = set()
        teams = set()
        
        for fixture in monthly_fixtures:
            if 'date' in fixture and fixture['date']:
                dates.add(fixture['date'])
            if 'competition' in fixture and fixture['competition']:
                competitions.add(fixture['competition'])
            if 'team1' in fixture and fixture['team1']:
                teams.add(fixture['team1'])
            if 'team2' in fixture and fixture['team2']:
                teams.add(fixture['team2'])
        
        print(f"\nData Analysis:")
        print(f"- Unique dates: {len(dates)}")
        print(f"- Competitions: {list(competitions)}")
        print(f"- Unique teams: {len(teams)}")
        
        if dates:
            print(f"- Date range: {min(dates)} to {max(dates)}")
        
        # Save to CSV for further analysis
        success = scraper.save_to_csv(monthly_fixtures, 'practical_demo_fixtures.csv')
        if success:
            print(f"- Data saved to practical_demo_fixtures.csv")
    
    # Demo 3: Test specific date known to have fixtures (based on the search results)
    print(f"\n3. Testing specific dates with known fixtures...")
    test_dates = [
        "2025-07-04",  # From the search results we saw fixtures on these dates
        "2025-07-05",
        "2025-07-06",
        "2025-01-04",  # Try a date in January
        "2025-01-05"
    ]
    
    for test_date in test_dates:
        print(f"\nTesting {test_date}:")
        result = scraper.get_fixtures(from_date=test_date, to_date=test_date)
        
        if result.get('success'):
            fixture_count = len(result.get('fixtures', []))
            print(f"  ✓ Success - {fixture_count} fixtures found")
            
            # Show one example fixture if available
            if fixture_count > 0:
                example = result['fixtures'][0]
                print(f"  Example: {example.get('team1', 'Team1')} vs {example.get('team2', 'Team2')}")
                if 'time' in example:
                    print(f"  Time: {example['time']}")
                if 'venue' in example:
                    print(f"  Venue: {example['venue']}")
        else:
            print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
    
    # Demo 4: Show data structure example
    print(f"\n4. Example data structure:")
    sample_result = scraper.get_fixtures()
    if sample_result.get('success'):
        print("Sample result structure:")
        print(json.dumps(sample_result, indent=2, default=str)[:1000] + "...")
    
    print("\n" + "=" * 50)
    print("Practical demo complete!")
    print("\nNext steps:")
    print("- Check practical_demo_fixtures.csv for exported data")
    print("- Modify date ranges to find fixtures in your desired period")
    print("- Use the scraper in your own applications")


if __name__ == "__main__":
    practical_demo() 