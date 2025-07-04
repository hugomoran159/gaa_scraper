#!/usr/bin/env python3
"""
Advanced Usage Example for Dublin GAA Scraper

This script demonstrates advanced features and data processing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gaa_scraper import DublinGAAScraper
from datetime import datetime, timedelta
import pandas as pd
import json


def custom_parameters_example():
    """Example using custom parameters for the datafeed."""
    print("Advanced Example: Custom Parameters")
    print("-" * 40)
    
    scraper = DublinGAAScraper()
    
    # Test different parameter combinations
    parameter_sets = [
        {
            'from_date': '2025-01-10',
            'to_date': '2025-01-10',
            'code_id': '26',  # Football
            'is_fixture': '1',
            'debug': '1'
        },
        {
            'from_date': '2025-01-15',
            'to_date': '2025-01-20',
            'code_name': 'Football',
            'age_id': '',  # All ages
        }
    ]
    
    for i, params in enumerate(parameter_sets, 1):
        print(f"\nParameter set {i}: {params}")
        result = scraper.get_fixtures(**params)
        
        if result.get('success'):
            print(f"✓ Success! Data type: {type(result)}")
            if 'raw_data' in result:
                print(f"  Raw data length: {len(result['raw_data'])}")
        else:
            print(f"✗ Failed: {result.get('error')}")


def data_processing_example():
    """Example of processing and analyzing the scraped data."""
    print("\nData Processing Example")
    print("-" * 40)
    
    scraper = DublinGAAScraper()
    
    # Get a week's worth of data
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    fixtures = scraper.get_date_range_fixtures(start_date, end_date)
    
    if fixtures:
        print(f"Processing {len(fixtures)} fixture records...")
        
        # Convert to DataFrame for analysis
        df = scraper.to_dataframe(fixtures)
        
        if not df.empty:
            print(f"DataFrame shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            # Basic analysis
            print("\nBasic Analysis:")
            print(f"- Total fixtures: {len(df)}")
            
            if 'date' in df.columns:
                print(f"- Date range: {df['date'].min()} to {df['date'].max()}")
            
            if 'competition' in df.columns:
                competitions = df['competition'].value_counts()
                print(f"- Competitions: {len(competitions)} unique")
                print("  Top competitions:")
                for comp, count in competitions.head(3).items():
                    print(f"    {comp}: {count} fixtures")
        else:
            print("No structured data available for analysis")
    else:
        print("No fixtures data retrieved")


def error_handling_example():
    """Example demonstrating error handling and retry logic."""
    print("\nError Handling Example")
    print("-" * 40)
    
    scraper = DublinGAAScraper()
    
    # Test with potentially problematic dates/parameters
    test_cases = [
        {'from_date': '2025-12-31', 'to_date': '2025-12-31'},  # Future date
        {'from_date': '2020-01-01', 'to_date': '2020-01-01'},  # Old date
        {'code_id': '999', 'from_date': '2025-01-10'},         # Invalid code
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: {test_case}")
        
        try:
            result = scraper.get_fixtures(**test_case)
            
            if result.get('success'):
                print("✓ Request succeeded")
                if 'method' in result:
                    print(f"  Method used: {result['method']}")
            else:
                print(f"✗ Request failed: {result.get('error')}")
                
        except Exception as e:
            print(f"✗ Exception occurred: {str(e)}")


def custom_session_example():
    """Example of customizing the session for special requirements."""
    print("\nCustom Session Example")
    print("-" * 40)
    
    # Create scraper with custom base URL (if needed)
    scraper = DublinGAAScraper()
    
    # Modify session settings
    scraper.session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-IE,en;q=0.8',
    })
    
    # Set custom timeout
    original_timeout = 30
    scraper.session.timeout = 60
    
    print("Modified session headers and timeout")
    print(f"User-Agent: {scraper.session.headers.get('User-Agent', 'Not set')}")
    
    # Test with modified session
    result = scraper.get_fixtures()
    
    if result.get('success'):
        print("✓ Custom session worked")
    else:
        print(f"✗ Custom session failed: {result.get('error')}")


if __name__ == "__main__":
    custom_parameters_example()
    data_processing_example()
    error_handling_example()
    custom_session_example()
    print("\nAdvanced usage examples complete!") 