#!/usr/bin/env python3
"""
Comprehensive Dublin GAA Fixtures Scraper

This script collects fixture data for ALL sports, age groups, and competitions
for the next two weeks from today, using the SportLoMo AJAX API.

Based on the proven working example and enhanced with our scraper framework.
"""

from src.gaa_scraper import DublinGAAScraper
from datetime import datetime, timedelta
import pandas as pd
import json
import time


def main():
    """
    Main function to collect comprehensive GAA fixture data.
    """
    print("🏈 Dublin GAA Comprehensive Fixtures Scraper")
    print("=" * 60)
    print("Collecting data for ALL sports, age groups, and competitions")
    print("for the next 2 weeks from today...")
    print()
    
    # Initialize the scraper
    scraper = DublinGAAScraper()
    
    # Show what sports we'll be scraping
    print("📊 Sports to be scraped:")
    for sport_name, sport_code in scraper.sports_mapping.items():
        user_id, code_id = scraper._parse_sport_value(sport_code)
        print(f"  • {sport_name}: user_id={user_id}, code_id={code_id}")
    print()
    
    # Calculate date range
    today = datetime.now()
    start_date = today.strftime('%Y-%m-%d')
    end_date = (today + timedelta(days=13)).strftime('%Y-%m-%d')  # 14 days total
    
    print(f"📅 Date range: {start_date} to {end_date}")
    print(f"📅 Total days: 14")
    print()
    
    # Collect comprehensive data
    print("🔄 Starting comprehensive data collection...")
    print("-" * 60)
    
    start_time = time.time()
    comprehensive_data = scraper.get_two_weeks_all_sports(start_date)
    end_time = time.time()
    
    print()
    print("=" * 60)
    print("📈 COLLECTION COMPLETE!")
    print("=" * 60)
    
    if comprehensive_data.get('success'):
        total_fixtures = comprehensive_data['total_fixtures']
        print(f"✅ Total fixtures found: {total_fixtures}")
        print(f"📅 Date range covered: {comprehensive_data['date_range']}")
        print(f"⏱️  Collection time: {end_time - start_time:.2f} seconds")
        print()
        
        # Detailed breakdown by sport
        print("📊 Breakdown by sport:")
        print("-" * 40)
        for sport, result in comprehensive_data['by_sport'].items():
            fixture_count = len(result.get('fixtures', []))
            status = "✅" if result.get('success') else "❌"
            print(f"  {status} {sport:15} {fixture_count:3d} fixtures")
        print()
        
        # Save comprehensive data
        if comprehensive_data['fixtures']:
            print("💾 Saving data...")
            
            # Save to CSV
            csv_filename = f'dublin_gaa_comprehensive_{start_date}_to_{end_date}.csv'
            success = scraper.save_to_csv(comprehensive_data['fixtures'], csv_filename)
            
            # Save raw data as JSON for debugging
            json_filename = f'dublin_gaa_comprehensive_{start_date}_to_{end_date}.json'
            try:
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(comprehensive_data, f, indent=2, default=str)
                print(f"✅ Raw data saved to {json_filename}")
            except Exception as e:
                print(f"❌ Error saving JSON: {e}")
            
            if success:
                # Analyze the data
                df = scraper.to_dataframe(comprehensive_data['fixtures'])
                
                print("\n📊 DATA ANALYSIS:")
                print("-" * 40)
                print(f"Total records: {len(df)}")
                
                if not df.empty:
                    # Competition analysis
                    if 'competition' in df.columns:
                        competitions = df['competition'].value_counts()
                        print(f"Unique competitions: {len(competitions)}")
                        print("Top competitions:")
                        for comp, count in competitions.head(10).items():
                            print(f"  • {comp}: {count} fixtures")
                    
                    # Team analysis
                    teams = set()
                    if 'home_team' in df.columns:
                        teams.update(df['home_team'].dropna().unique())
                    if 'away_team' in df.columns:
                        teams.update(df['away_team'].dropna().unique())
                    print(f"Unique teams involved: {len(teams)}")
                    
                    # Date distribution
                    if 'date' in df.columns:
                        date_counts = df['date'].value_counts().sort_index()
                        print(f"Fixtures distributed across {len(date_counts)} different dates")
                        print("Daily fixture count:")
                        for date, count in date_counts.items():
                            print(f"  • {date}: {count} fixtures")
                
                print()
                print("🎯 FILES CREATED:")
                print(f"  • {csv_filename} - Main data file (CSV)")
                print(f"  • {json_filename} - Raw data with metadata (JSON)")
        
        else:
            print("❌ No fixtures data to save")
    
    else:
        print("❌ Data collection failed!")
        error_msg = comprehensive_data.get('error', 'Unknown error')
        print(f"Error: {error_msg}")
    
    print()
    print("=" * 60)
    print("✨ Comprehensive scraping complete!")
    print()
    print("💡 Usage tips:")
    print("  • Open the CSV file in Excel or Google Sheets for analysis")
    print("  • Filter by sport, date, or competition as needed")
    print("  • Use the JSON file for programmatic access to all data")
    print("  • Run this script regularly to keep data up to date")


def analyze_data(csv_filename: str):
    """
    Optional function to perform additional analysis on the collected data.
    
    Args:
        csv_filename: Path to the CSV file with fixture data
    """
    try:
        df = pd.read_csv(csv_filename)
        
        print(f"\n📊 DETAILED ANALYSIS OF {csv_filename}")
        print("=" * 60)
        
        # Basic statistics
        print(f"Total fixtures: {len(df)}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"Sports covered: {df['sport'].nunique() if 'sport' in df.columns else 'N/A'}")
        
        # Sport breakdown
        if 'sport' in df.columns:
            print("\nFixtures by sport:")
            sport_counts = df['sport'].value_counts()
            for sport, count in sport_counts.items():
                percentage = (count / len(df)) * 100
                print(f"  • {sport}: {count} ({percentage:.1f}%)")
        
        # Competition analysis
        if 'competition' in df.columns:
            print(f"\nTotal competitions: {df['competition'].nunique()}")
            top_competitions = df['competition'].value_counts().head(10)
            print("Top 10 competitions by fixture count:")
            for comp, count in top_competitions.items():
                print(f"  • {comp}: {count}")
        
        # Time analysis
        if 'time' in df.columns:
            # Most common kickoff times
            time_counts = df['time'].value_counts().head(10)
            print("\nMost common kickoff times:")
            for time_val, count in time_counts.items():
                print(f"  • {time_val}: {count} fixtures")
        
        # Venue analysis
        if 'venue' in df.columns:
            venue_counts = df['venue'].value_counts()
            print(f"\nTotal venues: {len(venue_counts)}")
            print("Top 10 venues by fixture count:")
            for venue, count in venue_counts.head(10).items():
                print(f"  • {venue}: {count}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")
        return None


if __name__ == "__main__":
    main()
    
    # Optionally run additional analysis
    csv_file = f'dublin_gaa_comprehensive_{datetime.now().strftime("%Y-%m-%d")}_to_{(datetime.now() + timedelta(days=13)).strftime("%Y-%m-%d")}.csv'
    
    # Uncomment the next line to run detailed analysis after data collection
    # analyze_data(csv_file) 