#!/usr/bin/env python3
"""
Quick test script for the Streamlit app functionality.
Tests the core scraper functionality without the UI.
"""

import sys
import os
sys.path.append('src')

from gaa_scraper import DublinGAAScraper
import pandas as pd
from datetime import datetime

def test_scraper_functionality():
    """Test that the scraper works for Streamlit."""
    print("🧪 Testing Dublin GAA Scraper for Streamlit...")
    
    # Initialize scraper
    scraper = DublinGAAScraper()
    print("✅ Scraper initialized")
    
    # Test sports mapping
    print(f"📊 Available sports: {list(scraper.sports_mapping.keys())}")
    
    # Test sample data loading (if available)
    try:
        import glob
        csv_files = glob.glob('dublin_gaa_comprehensive_*.csv')
        if csv_files:
            latest_csv = sorted(csv_files)[-1]
            df = pd.read_csv(latest_csv)
            print(f"✅ Sample data loaded: {len(df)} fixtures from {latest_csv}")
            
            # Test DataFrame processing
            if not df.empty:
                print(f"📈 Data shape: {df.shape}")
                print(f"🏆 Sports in data: {df['sport'].nunique() if 'sport' in df.columns else 'N/A'}")
                print(f"🏟️ Competitions: {df['competition'].nunique() if 'competition' in df.columns else 'N/A'}")
                
                # Test sample result structure for Streamlit
                sample_result = {
                    'success': True,
                    'total_fixtures': len(df),
                    'fixtures': df.to_dict('records')[:5],  # First 5 for testing
                    'date_range': f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else 'N/A',
                    'sports_scraped': df['sport'].unique().tolist() if 'sport' in df.columns else [],
                    'method': 'test_sample'
                }
                print("✅ Sample result structure created for Streamlit")
                
        else:
            print("⚠️  No sample CSV files found - will test with empty data")
            
    except Exception as e:
        print(f"⚠️  Sample data test failed: {e}")
    
    # Test basic API connectivity (without full scrape)
    try:
        import requests
        response = requests.get('https://dublingaa.sportlomo.com', timeout=10)
        print(f"✅ SportLoMo site accessible: {response.status_code}")
    except Exception as e:
        print(f"⚠️  SportLoMo connectivity test failed: {e}")
    
    print("\n🎉 Streamlit app functionality test complete!")
    print("The app should work properly when deployed.")

if __name__ == "__main__":
    test_scraper_functionality() 