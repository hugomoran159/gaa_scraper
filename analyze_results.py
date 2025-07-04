#!/usr/bin/env python3
"""
Analysis Script for Dublin GAA Comprehensive Fixture Data

This script analyzes the collected fixture data and provides detailed insights
about the sports, competitions, teams, and scheduling patterns.
"""

import pandas as pd
import json
from datetime import datetime
from collections import Counter
import re


def load_and_analyze_data(csv_file: str, json_file: str = None):
    """
    Load and perform comprehensive analysis of the GAA fixture data.
    
    Args:
        csv_file: Path to the CSV file with fixture data
        json_file: Optional path to JSON file with metadata
    """
    print("🏈 Dublin GAA Fixture Data Analysis")
    print("=" * 60)
    
    # Load the CSV data
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(df)} fixtures from {csv_file}")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Load JSON metadata if available
    metadata = None
    if json_file:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"✅ Loaded metadata from {json_file}")
        except Exception as e:
            print(f"⚠️  Could not load JSON metadata: {e}")
    
    print()
    
    # Basic Statistics
    print("📊 BASIC STATISTICS")
    print("-" * 40)
    print(f"Total fixtures: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print()
    
    # Sport Analysis
    print("🏆 SPORT BREAKDOWN")
    print("-" * 40)
    if 'sport' in df.columns:
        sport_counts = df['sport'].value_counts()
        total_fixtures = len(df)
        
        for sport, count in sport_counts.items():
            percentage = (count / total_fixtures) * 100
            print(f"  • {sport:20} {count:3d} fixtures ({percentage:5.1f}%)")
        
        print(f"\nTotal sports covered: {len(sport_counts)}")
    print()
    
    # Competition Analysis
    print("🏟️ COMPETITION ANALYSIS")
    print("-" * 40)
    if 'competition' in df.columns:
        competitions = df['competition'].value_counts()
        print(f"Total unique competitions: {len(competitions)}")
        print("\nTop 15 competitions by fixture count:")
        
        for i, (comp, count) in enumerate(competitions.head(15).items(), 1):
            print(f"  {i:2d}. {comp:35} {count:3d} fixtures")
        
        # Competition categories
        print("\nCompetition categories:")
        categories = analyze_competition_categories(competitions.index.tolist())
        for category, count in categories.items():
            print(f"  • {category:20} {count:3d} competitions")
    print()
    
    # Team Analysis
    print("👥 TEAM ANALYSIS")
    print("-" * 40)
    all_teams = set()
    if 'home_team' in df.columns:
        home_teams = set(df['home_team'].dropna().unique())
        all_teams.update(home_teams)
        print(f"Unique home teams: {len(home_teams)}")
    
    if 'away_team' in df.columns:
        away_teams = set(df['away_team'].dropna().unique())
        all_teams.update(away_teams)
        print(f"Unique away teams: {len(away_teams)}")
    
    print(f"Total unique teams: {len(all_teams)}")
    
    # Team participation analysis
    if 'home_team' in df.columns and 'away_team' in df.columns:
        team_participation = Counter()
        team_participation.update(df['home_team'].dropna())
        team_participation.update(df['away_team'].dropna())
        
        print(f"\nTop 10 most active teams:")
        for i, (team, count) in enumerate(team_participation.most_common(10), 1):
            print(f"  {i:2d}. {team:30} {count:3d} fixtures")
    print()
    
    # Time Analysis
    print("⏰ SCHEDULING ANALYSIS")
    print("-" * 40)
    if 'time' in df.columns:
        time_counts = df['time'].value_counts()
        print(f"Different kickoff times: {len(time_counts)}")
        print("Most common kickoff times:")
        
        for i, (time_val, count) in enumerate(time_counts.head(10).items(), 1):
            print(f"  {i:2d}. {time_val:10} {count:3d} fixtures")
    
    # Date distribution
    if 'date' in df.columns:
        date_counts = df['date'].value_counts().sort_index()
        print(f"\nFixtures across {len(date_counts)} different dates:")
        for date, count in date_counts.items():
            day_name = parse_day_from_date(date)
            print(f"  • {date:20} ({day_name:9}) {count:3d} fixtures")
    print()
    
    # Venue Analysis
    print("🏟️ VENUE ANALYSIS")
    print("-" * 40)
    if 'venue' in df.columns:
        venues = df['venue'].value_counts()
        print(f"Total unique venues: {len(venues)}")
        print("Top 10 most used venues:")
        
        for i, (venue, count) in enumerate(venues.head(10).items(), 1):
            print(f"  {i:2d}. {venue:30} {count:3d} fixtures")
    print()
    
    # Age Group Analysis
    print("👶 AGE GROUP ANALYSIS")
    print("-" * 40)
    age_groups = analyze_age_groups(df)
    if age_groups:
        for age_group, count in age_groups.items():
            print(f"  • {age_group:15} {count:3d} fixtures")
    print()
    
    # Quality Assessment
    print("✅ DATA QUALITY ASSESSMENT")
    print("-" * 40)
    assess_data_quality(df)
    print()
    
    # Metadata Analysis
    if metadata:
        print("📋 COLLECTION METADATA")
        print("-" * 40)
        print(f"Collection method: {metadata.get('method', 'N/A')}")
        print(f"Total collection time: {metadata.get('collection_time', 'N/A')}")
        print(f"Sports scraped: {metadata.get('sports_scraped', [])}")
        
        if 'by_sport' in metadata:
            print("\nCollection success by sport:")
            for sport, result in metadata['by_sport'].items():
                success = "✅" if result.get('success') else "❌"
                fixture_count = len(result.get('fixtures', []))
                print(f"  {success} {sport:20} {fixture_count:3d} fixtures")
    
    print()
    print("=" * 60)
    print("🎯 ANALYSIS COMPLETE!")
    print()
    
    return df


def analyze_competition_categories(competitions):
    """
    Categorize competitions by type.
    
    Args:
        competitions: List of competition names
        
    Returns:
        Dictionary with category counts
    """
    categories = {
        'Adult Football League': 0,
        'Adult Football Cup': 0,
        'Youth Football': 0,
        'Adult Hurling': 0,
        'Youth Hurling': 0,
        'Ladies Football': 0,
        'Camogie': 0,
        'Other': 0
    }
    
    for comp in competitions:
        comp_lower = comp.lower()
        
        if 'lgfa' in comp_lower and 'adult' in comp_lower:
            if 'cup' in comp_lower:
                categories['Adult Football Cup'] += 1
            else:
                categories['Ladies Football'] += 1
        elif 'lgfa' in comp_lower:
            categories['Ladies Football'] += 1
        elif 'afl' in comp_lower or ('football' in comp_lower and 'div' in comp_lower):
            categories['Adult Football League'] += 1
        elif ('u8' in comp_lower or 'u9' in comp_lower or 'u10' in comp_lower or 
              'u11' in comp_lower or 'u12' in comp_lower or 'u13' in comp_lower or 
              'u14' in comp_lower or 'u15' in comp_lower or 'u16' in comp_lower or
              'minor' in comp_lower) and 'football' in comp_lower:
            categories['Youth Football'] += 1
        elif 'hurling' in comp_lower or 'hl' in comp_lower:
            if ('u8' in comp_lower or 'u9' in comp_lower or 'u10' in comp_lower or 
                'u11' in comp_lower or 'u12' in comp_lower or 'u13' in comp_lower or 
                'u14' in comp_lower or 'u15' in comp_lower or 'u16' in comp_lower or
                'minor' in comp_lower):
                categories['Youth Hurling'] += 1
            else:
                categories['Adult Hurling'] += 1
        elif 'camogie' in comp_lower:
            categories['Camogie'] += 1
        else:
            categories['Other'] += 1
    
    return categories


def analyze_age_groups(df):
    """
    Analyze age groups from competition names.
    
    Args:
        df: DataFrame with fixture data
        
    Returns:
        Dictionary with age group counts
    """
    age_groups = Counter()
    
    if 'competition' in df.columns:
        for comp in df['competition'].dropna():
            comp_lower = comp.lower()
            
            # Look for age patterns
            age_patterns = [
                (r'u(\d+)', 'U{}'),
                (r'under (\d+)', 'Under {}'),
                (r'minor', 'Minor'),
                (r'senior', 'Senior'),
                (r'adult', 'Adult'),
                (r'junior', 'Junior')
            ]
            
            found_age = False
            for pattern, template in age_patterns:
                match = re.search(pattern, comp_lower)
                if match:
                    if '{}' in template:
                        age_group = template.format(match.group(1))
                    else:
                        age_group = template
                    age_groups[age_group] += 1
                    found_age = True
                    break
            
            if not found_age:
                age_groups['Unknown'] += 1
    
    return dict(age_groups.most_common())


def parse_day_from_date(date_str):
    """
    Extract day name from date string.
    
    Args:
        date_str: Date string from the data
        
    Returns:
        Day name or original string if parsing fails
    """
    # The dates in our data are like "Friday July 4"
    if any(day in date_str for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
        return date_str.split()[0]
    elif any(day in date_str for day in ['Moay', 'Satuay', 'Suay']):  # Handle the typos in the data
        day_map = {'Moay': 'Monday', 'Satuay': 'Saturday', 'Suay': 'Sunday'}
        for typo, correct in day_map.items():
            if typo in date_str:
                return correct
    
    return 'Unknown'


def assess_data_quality(df):
    """
    Assess the quality of the collected data.
    
    Args:
        df: DataFrame with fixture data
    """
    total_rows = len(df)
    
    print(f"Total records: {total_rows}")
    
    # Check for missing values
    for column in df.columns:
        missing_count = df[column].isnull().sum()
        missing_pct = (missing_count / total_rows) * 100
        status = "✅" if missing_pct < 5 else "⚠️" if missing_pct < 20 else "❌"
        print(f"  {status} {column:15} {missing_count:3d} missing ({missing_pct:5.1f}%)")
    
    # Check for data consistency
    if 'home_team' in df.columns and 'away_team' in df.columns:
        same_team_matches = df[df['home_team'] == df['away_team']]
        if len(same_team_matches) > 0:
            print(f"⚠️  Found {len(same_team_matches)} fixtures where home and away teams are the same")
    
    # Check for reasonable time formats
    if 'time' in df.columns:
        time_pattern = r'\d{1,2}:\d{2}'
        valid_times = df['time'].str.match(time_pattern, na=False).sum()
        invalid_times = total_rows - valid_times - df['time'].isnull().sum()
        if invalid_times > 0:
            print(f"⚠️  Found {invalid_times} fixtures with non-standard time formats")


def main():
    """Run the analysis on the most recent comprehensive data file."""
    import glob
    
    # Find the most recent comprehensive CSV file
    csv_files = glob.glob('dublin_gaa_comprehensive_*.csv')
    if not csv_files:
        print("❌ No comprehensive CSV files found!")
        print("Run the comprehensive_scraper.py first to collect data.")
        return
    
    # Use the most recent file
    csv_file = sorted(csv_files)[-1]
    json_file = csv_file.replace('.csv', '.json')
    
    print(f"📁 Analyzing file: {csv_file}")
    if glob.glob(json_file):
        print(f"📁 Metadata file: {json_file}")
    else:
        json_file = None
    
    print()
    
    # Run the analysis
    df = load_and_analyze_data(csv_file, json_file)
    
    # Offer to save analysis results
    if df is not None:
        analysis_file = csv_file.replace('.csv', '_analysis.txt')
        print(f"💾 Analysis complete! Consider saving results to {analysis_file}")


if __name__ == "__main__":
    main() 