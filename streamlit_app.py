#!/usr/bin/env python3
"""
Streamlit Web App for Dublin GAA Fixtures Scraper

A beautiful, user-friendly web interface for collecting and analyzing
Dublin GAA fixture data across all sports, age groups, and competitions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json
import time
import io
from src.gaa_scraper import DublinGAAScraper
import base64


# Page configuration
st.set_page_config(
    page_title="Dublin GAA Fixtures Scraper",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'scraper' not in st.session_state:
        st.session_state.scraper = DublinGAAScraper()
    if 'last_scraped_data' not in st.session_state:
        st.session_state.last_scraped_data = None
    if 'scraping_in_progress' not in st.session_state:
        st.session_state.scraping_in_progress = False


def create_download_link(df, filename):
    """Create a download link for a DataFrame."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    return href


def display_metrics(data):
    """Display key metrics in a nice layout."""
    if not data or not data.get('success'):
        return
    
    total_fixtures = data.get('total_fixtures', 0)
    sports_count = len(data.get('sports_scraped', []))
    date_range = data.get('date_range', 'N/A')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏈 Total Fixtures",
            value=total_fixtures,
            help="Total number of fixtures collected"
        )
    
    with col2:
        st.metric(
            label="🏆 Sports Covered",
            value=f"{sports_count}/4",
            help="Number of sports with fixture data"
        )
    
    with col3:
        st.metric(
            label="📅 Date Range",
            value="14 days",
            delta=date_range,
            help="Coverage period for fixtures"
        )
    
    with col4:
        competitions = len(set([f.get('competition', '') for f in data.get('fixtures', [])]))
        st.metric(
            label="🏟️ Competitions",
            value=competitions,
            help="Number of unique competitions"
        )


def create_visualizations(df):
    """Create interactive visualizations for the fixture data."""
    if df.empty:
        st.warning("No data available for visualization.")
        return
    
    st.subheader("📊 Data Visualizations")
    
    # Sport distribution pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        if 'sport' in df.columns:
            sport_counts = df['sport'].value_counts()
            fig_pie = px.pie(
                values=sport_counts.values,
                names=sport_counts.index,
                title="Fixtures by Sport",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        if 'date' in df.columns:
            # Daily fixture distribution
            date_counts = df['date'].value_counts().sort_index()
            fig_bar = px.bar(
                x=date_counts.index,
                y=date_counts.values,
                title="Fixtures by Date",
                labels={'x': 'Date', 'y': 'Number of Fixtures'}
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Competition analysis
    if 'competition' in df.columns:
        st.subheader("🏟️ Top Competitions")
        comp_counts = df['competition'].value_counts().head(10)
        fig_comp = px.bar(
            x=comp_counts.values,
            y=comp_counts.index,
            orientation='h',
            title="Top 10 Competitions by Fixture Count",
            labels={'x': 'Number of Fixtures', 'y': 'Competition'}
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    # Time distribution
    if 'time' in df.columns:
        st.subheader("⏰ Kickoff Time Distribution")
        time_counts = df['time'].value_counts().head(10)
        fig_time = px.bar(
            x=time_counts.index,
            y=time_counts.values,
            title="Most Common Kickoff Times",
            labels={'x': 'Time', 'y': 'Number of Fixtures'}
        )
        st.plotly_chart(fig_time, use_container_width=True)


def display_sport_breakdown(data):
    """Display detailed breakdown by sport."""
    if not data or not data.get('by_sport'):
        return
    
    st.subheader("🏆 Sport-by-Sport Breakdown")
    
    for sport, result in data['by_sport'].items():
        with st.expander(f"{sport} ({len(result.get('fixtures', []))} fixtures)"):
            if result.get('success') and result.get('fixtures'):
                sport_df = pd.DataFrame(result['fixtures'])
                
                # Show key stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    competitions = sport_df['competition'].nunique() if 'competition' in sport_df.columns else 0
                    st.metric("Competitions", competitions)
                with col2:
                    teams = set()
                    if 'home_team' in sport_df.columns:
                        teams.update(sport_df['home_team'].dropna())
                    if 'away_team' in sport_df.columns:
                        teams.update(sport_df['away_team'].dropna())
                    st.metric("Teams", len(teams))
                with col3:
                    venues = sport_df['venue'].nunique() if 'venue' in sport_df.columns else 0
                    st.metric("Venues", venues)
                
                # Show sample fixtures
                st.write("**Sample Fixtures:**")
                display_cols = ['date', 'time', 'competition', 'home_team', 'away_team', 'venue']
                available_cols = [col for col in display_cols if col in sport_df.columns]
                st.dataframe(sport_df[available_cols].head(5), use_container_width=True)
                
            else:
                st.warning(f"No fixtures found for {sport}")


def main():
    """Main Streamlit application."""
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🏈 Dublin GAA Fixtures Scraper</h1>', unsafe_allow_html=True)
    st.markdown("### Comprehensive fixture data for all Dublin GAA sports, age groups, and competitions")
    
    # Sidebar controls
    st.sidebar.header("🎛️ Control Panel")
    
    # Date range selection
    st.sidebar.subheader("📅 Date Range")
    default_start = date.today()
    default_end = default_start + timedelta(days=13)
    
    date_option = st.sidebar.radio(
        "Choose date range:",
        ["Next 2 weeks (default)", "Custom range", "Today only"]
    )
    
    if date_option == "Custom range":
        start_date = st.sidebar.date_input("Start date", default_start)
        end_date = st.sidebar.date_input("End date", default_end)
    elif date_option == "Today only":
        start_date = end_date = default_start
    else:  # Next 2 weeks
        start_date = default_start
        end_date = default_end
    
    # Sport selection
    st.sidebar.subheader("🏆 Sports Selection")
    available_sports = list(st.session_state.scraper.sports_mapping.keys())
    selected_sports = st.sidebar.multiselect(
        "Select sports to scrape:",
        available_sports,
        default=available_sports,
        help="Choose which sports to include in the data collection"
    )
    
    # Action buttons
    st.sidebar.subheader("🚀 Actions")
    
    if st.sidebar.button("🔄 Scrape Fixtures", type="primary", disabled=st.session_state.scraping_in_progress):
        if not selected_sports:
            st.sidebar.error("Please select at least one sport!")
        else:
            st.session_state.scraping_in_progress = True
            scrape_fixtures(start_date, end_date, selected_sports)
            st.session_state.scraping_in_progress = False
    
    if st.sidebar.button("📊 Load Sample Data"):
        load_sample_data()
    
    # Main content area
    if st.session_state.scraping_in_progress:
        st.info("🔄 Scraping in progress... Please wait.")
        st.balloons()
    
    # Display results if available
    if st.session_state.last_scraped_data:
        display_results()
    else:
        display_welcome_message()
    
    # Footer
    st.markdown("---")
    st.markdown("**Dublin GAA Fixtures Scraper** | Built with ❤️ using Streamlit")


def scrape_fixtures(start_date, end_date, selected_sports):
    """Scrape fixtures with progress tracking."""
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text(f"🔄 Initializing scraper...")
        progress_bar.progress(10)
        
        status_text.text(f"📅 Collecting data from {start_date_str} to {end_date_str}...")
        progress_bar.progress(30)
        
        # Perform the scraping
        if len(selected_sports) == len(st.session_state.scraper.sports_mapping) and \
           start_date == date.today() and (end_date - start_date).days == 13:
            # Use the optimized comprehensive method
            result = st.session_state.scraper.get_two_weeks_all_sports(start_date_str)
        else:
            # Use custom collection
            result = st.session_state.scraper.get_all_sports_fixtures(
                start_date_str, 
                end_date_str, 
                selected_sports
            )
        
        progress_bar.progress(80)
        status_text.text("📊 Processing results...")
        
        if result.get('success'):
            st.session_state.last_scraped_data = result
            progress_bar.progress(100)
            status_text.text("✅ Scraping completed successfully!")
            
            # Success message
            st.success(f"""
            🎉 **Scraping Completed Successfully!**
            
            - **{result.get('total_fixtures', 0)} fixtures** collected
            - **{len(selected_sports)} sports** scraped
            - **Date range:** {start_date_str} to {end_date_str}
            """)
            
        else:
            st.error(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"❌ An error occurred during scraping: {str(e)}")
    finally:
        progress_bar.empty()
        status_text.empty()


def load_sample_data():
    """Load sample data for demonstration."""
    try:
        # Try to load the existing comprehensive data file
        import glob
        csv_files = glob.glob('dublin_gaa_comprehensive_*.csv')
        if csv_files:
            latest_csv = sorted(csv_files)[-1]
            df = pd.read_csv(latest_csv)
            
            # Create a mock result structure
            sample_result = {
                'success': True,
                'total_fixtures': len(df),
                'fixtures': df.to_dict('records'),
                'date_range': f"{df['date'].min()} to {df['date'].max()}",
                'sports_scraped': df['sport'].unique().tolist() if 'sport' in df.columns else [],
                'method': 'sample_data'
            }
            
            st.session_state.last_scraped_data = sample_result
            st.success(f"📊 Loaded sample data: {len(df)} fixtures from {latest_csv}")
        else:
            st.warning("No sample data files found. Please run the scraper first.")
            
    except Exception as e:
        st.error(f"❌ Error loading sample data: {str(e)}")


def display_results():
    """Display the scraped results with analysis."""
    data = st.session_state.last_scraped_data
    
    # Key metrics
    display_metrics(data)
    
    # Create DataFrame from fixtures
    if data.get('fixtures'):
        df = pd.DataFrame(data['fixtures'])
        
        # Tabbed interface for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Data Table", "📊 Visualizations", "🏆 By Sport", "📥 Download", "🔍 Analysis"])
        
        with tab1:
            st.subheader("📋 Complete Fixtures Data")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'sport' in df.columns:
                    sport_filter = st.selectbox(
                        "Filter by Sport:",
                        ['All'] + list(df['sport'].unique())
                    )
                else:
                    sport_filter = 'All'
            
            with col2:
                if 'competition' in df.columns:
                    comp_filter = st.selectbox(
                        "Filter by Competition:",
                        ['All'] + list(df['competition'].unique())
                    )
                else:
                    comp_filter = 'All'
            
            with col3:
                if 'date' in df.columns:
                    date_filter = st.selectbox(
                        "Filter by Date:",
                        ['All'] + list(df['date'].unique())
                    )
                else:
                    date_filter = 'All'
            
            # Apply filters
            filtered_df = df.copy()
            if sport_filter != 'All' and 'sport' in df.columns:
                filtered_df = filtered_df[filtered_df['sport'] == sport_filter]
            if comp_filter != 'All' and 'competition' in df.columns:
                filtered_df = filtered_df[filtered_df['competition'] == comp_filter]
            if date_filter != 'All' and 'date' in df.columns:
                filtered_df = filtered_df[filtered_df['date'] == date_filter]
            
            st.write(f"Showing {len(filtered_df)} of {len(df)} fixtures")
            st.dataframe(filtered_df, use_container_width=True, height=400)
        
        with tab2:
            create_visualizations(df)
        
        with tab3:
            display_sport_breakdown(data)
        
        with tab4:
            st.subheader("📥 Download Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV download
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📊 Download CSV",
                    data=csv,
                    file_name=f"dublin_gaa_fixtures_{datetime.now().strftime('%Y-%m-%d')}.csv",
                    mime="text/csv"
                )
                
                # Excel download
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Fixtures', index=False)
                    
                    # Add summary sheet
                    summary_data = {
                        'Metric': ['Total Fixtures', 'Sports', 'Competitions', 'Teams', 'Venues'],
                        'Count': [
                            len(df),
                            df['sport'].nunique() if 'sport' in df.columns else 0,
                            df['competition'].nunique() if 'competition' in df.columns else 0,
                            len(set(list(df.get('home_team', [])) + list(df.get('away_team', [])))),
                            df['venue'].nunique() if 'venue' in df.columns else 0
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                st.download_button(
                    label="📋 Download Excel",
                    data=buffer.getvalue(),
                    file_name=f"dublin_gaa_fixtures_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col2:
                # JSON download
                json_data = json.dumps(data, indent=2, default=str)
                st.download_button(
                    label="🔧 Download JSON (Raw Data)",
                    data=json_data,
                    file_name=f"dublin_gaa_fixtures_{datetime.now().strftime('%Y-%m-%d')}.json",
                    mime="application/json"
                )
                
                # Team list download
                if 'home_team' in df.columns and 'away_team' in df.columns:
                    all_teams = sorted(set(list(df['home_team'].dropna()) + list(df['away_team'].dropna())))
                    team_csv = '\n'.join(['Team Name'] + all_teams)
                    st.download_button(
                        label="👥 Download Team List",
                        data=team_csv,
                        file_name=f"dublin_gaa_teams_{datetime.now().strftime('%Y-%m-%d')}.csv",
                        mime="text/csv"
                    )
        
        with tab5:
            st.subheader("🔍 Detailed Analysis")
            
            # Data quality metrics
            st.write("**Data Quality Assessment:**")
            quality_metrics = []
            for col in df.columns:
                missing_count = df[col].isnull().sum()
                missing_pct = (missing_count / len(df)) * 100
                quality_metrics.append({
                    'Field': col,
                    'Missing Count': missing_count,
                    'Missing %': f"{missing_pct:.1f}%",
                    'Quality': '✅ Excellent' if missing_pct < 5 else '⚠️ Good' if missing_pct < 20 else '❌ Poor'
                })
            
            quality_df = pd.DataFrame(quality_metrics)
            st.dataframe(quality_df, use_container_width=True)
            
            # Additional insights
            col1, col2 = st.columns(2)
            
            with col1:
                if 'competition' in df.columns:
                    st.write("**Top Competitions:**")
                    top_comps = df['competition'].value_counts().head(10)
                    for comp, count in top_comps.items():
                        st.write(f"• {comp}: {count} fixtures")
            
            with col2:
                if 'venue' in df.columns:
                    st.write("**Most Used Venues:**")
                    top_venues = df['venue'].value_counts().head(10)
                    for venue, count in top_venues.items():
                        st.write(f"• {venue}: {count} fixtures")


def display_welcome_message():
    """Display welcome message and instructions."""
    st.markdown("""
    ## 👋 Welcome to the Dublin GAA Fixtures Scraper!
    
    This tool helps you collect comprehensive fixture data for Dublin GAA across:
    - **All Sports**: Male Football, Hurling, Ladies Football, Camogie
    - **All Age Groups**: U8 through Adult competitions
    - **All Competition Types**: Leagues, cups, championships
    
    ### 🚀 How to Get Started:
    
    1. **Choose your date range** in the sidebar (default: next 2 weeks)
    2. **Select sports** you want to include (default: all sports)
    3. **Click "Scrape Fixtures"** to collect the data
    4. **Explore the results** using the interactive tabs
    5. **Download your data** in CSV, Excel, or JSON format
    
    ### 📊 What You'll Get:
    
    - **Interactive data table** with filtering options
    - **Beautiful visualizations** showing patterns and distributions
    - **Sport-by-sport breakdown** with detailed statistics
    - **Multiple download formats** for further analysis
    - **Data quality assessment** and insights
    
    ### 💡 Pro Tips:
    
    - Use **"Load Sample Data"** to see the interface with existing data
    - **Filter the data table** to find specific fixtures
    - **Download Excel files** for advanced analysis in spreadsheet software
    - **Check the Analysis tab** for data quality insights
    
    Ready to start? Use the controls in the sidebar! 👈
    """)
    
    # Show sample of available sports
    with st.expander("🏆 Available Sports & Competitions"):
        scraper = st.session_state.scraper
        for sport, code in scraper.sports_mapping.items():
            user_id, code_id = scraper._parse_sport_value(code)
            st.write(f"**{sport}**")
            st.write(f"- User ID: `{user_id}`")
            st.write(f"- Code ID: `{code_id}`")
            st.write("")


if __name__ == "__main__":
    main() 