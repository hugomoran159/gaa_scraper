"""
Dublin GAA Fixtures Scraper

A Python scraper for extracting fixtures and results from the Dublin GAA website.
Uses the WordPress datafeed endpoint to retrieve structured data.
Enhanced with SportLoMo AJAX API support for comprehensive data collection.
"""

import requests
from datetime import datetime, timedelta
import pandas as pd
import json
from typing import Dict, List, Optional
import time
from urllib.parse import urlencode
import re
from bs4 import BeautifulSoup


class DublinGAAScraper:
    """Scraper for Dublin GAA fixtures and results data."""
    
    def __init__(self, base_url: str = "https://www.dublingaa.ie"):
        """
        Initialize the scraper.
        
        Args:
            base_url: Base URL of the Dublin GAA website
        """
        self.base_url = base_url
        self.sportlomo_url = "https://dublingaa.sportlomo.com"
        self.sportlomo_ajax_url = "https://dublingaa.sportlomo.com/wp-admin/admin-ajax.php"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # WordPress datafeed endpoint
        self.datafeed_url = f"{base_url}/wp-admin/admin-ajax.php"
        
        # Sports mapping from the example script - this is the key to getting all data
        self.sports_mapping = {
            "Male Football": "3,7167,7130_26",
            "Hurling": "3,7167,7130_27", 
            "Ladies Football": "7046",
            "Camogie": "7282"
        }
        
        # Default parameters structure
        self.default_params = {
            'action': 'get_fixtures',
            'user_id': '3,7167,7130',  # User IDs for permissions
            'code_id': '26',           # Football code
            'code_name': 'Football',
            'spage_id': '1',
            'debug': '1',
            'is_fixture': '1',
            'age_id': '',
            'club_search_id': '',
            'comp_search_id': ''
        }
    
    def _parse_sport_value(self, sport_value: str) -> tuple:
        """
        Parse the sport value to get user_id and code_id.
        
        Args:
            sport_value: Sport value from mapping (e.g., "3,7167,7130_26")
            
        Returns:
            Tuple of (user_id, code_id)
        """
        user_id = ''
        code_id = ''
        if "_" in sport_value:
            user_id, code_id = sport_value.split('_')
        else:
            user_id = sport_value
        return user_id, code_id
    
    def _parse_sportlomo_match_data(self, html_content: str) -> List[Dict]:
        """
        Parse the HTML fragment returned by SportLoMo AJAX call.
        Based on the example script's parsing logic.
        
        Args:
            html_content: HTML content from AJAX response
            
        Returns:
            List of match dictionaries
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        matches = []
        
        # Find all competition headers
        competition_headers = soup.find_all('thead', class_='divider')
        
        for header in competition_headers:
            # Get competition name and date from header
            comp_name_tag = header.find('div', class_='comp-name')
            comp_name = comp_name_tag.get_text(strip=True) if comp_name_tag else "N/A"
            
            match_date_tag = header.find('div', class_='date')
            match_date = match_date_tag.get_text(strip=True).replace("st", "").replace("nd", "").replace("rd", "").replace("th", "") if match_date_tag else "N/A"
            
            # Find match rows that belong to this competition
            current_element = header.find_next_sibling()
            while current_element and current_element.name == 'tbody':
                match_row = current_element
                
                # Extract match data
                time_tag = match_row.find('td', class_='time')
                match_time = time_tag.get_text(strip=True) if time_tag else "N/A"
                
                home_team_tag = match_row.find('td', class_='align-right')
                if home_team_tag:
                    home_team_span = home_team_tag.find('span', class_='team-name')
                    home_team = home_team_span.get_text(strip=True) if home_team_span else "N/A"
                else:
                    home_team = "N/A"
                
                away_team_tag = match_row.find('td', class_='align-left')
                if away_team_tag:
                    away_team_span = away_team_tag.find('span', class_='team-name')
                    away_team = away_team_span.get_text(strip=True) if away_team_span else "N/A"
                else:
                    away_team = "N/A"
                
                # Venue and referee info
                venue_tag = match_row.find('div', class_='venue')
                venue = venue_tag.find('span').get_text(strip=True) if venue_tag and venue_tag.find('span') else "N/A"
                
                referee_tag = match_row.find('div', class_='referee')
                referee = referee_tag.find('span').get_text(strip=True) if referee_tag and referee_tag.find('span') else "N/A"
                
                matches.append({
                    "date": match_date,
                    "time": match_time,
                    "competition": comp_name,
                    "home_team": home_team,
                    "away_team": away_team,
                    "venue": venue,
                    "referee": referee
                })
                
                current_element = current_element.find_next_sibling()
        
        return matches
    
    def get_sportlomo_fixtures(self, sport_name: str, from_date: str, to_date: str = None) -> Dict:
        """
        Get fixtures from SportLoMo using the proper AJAX API.
        
        Args:
            sport_name: Sport name from sports_mapping
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD), defaults to from_date
            
        Returns:
            Dictionary with fixtures data
        """
        if to_date is None:
            to_date = from_date
            
        if sport_name not in self.sports_mapping:
            return {
                'success': False,
                'error': f"Unknown sport: {sport_name}. Available: {list(self.sports_mapping.keys())}"
            }
        
        sport_value = self.sports_mapping[sport_name]
        user_id, code_id = self._parse_sport_value(sport_value)
        
        all_matches = []
        
        # Get fixtures for each date in the range
        current_date = datetime.strptime(from_date, '%Y-%m-%d')
        end_date = datetime.strptime(to_date, '%Y-%m-%d')
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            payload = {
                'action': 'get_fixtures',
                'fdate': date_str,
                'tdate': date_str,
                'user_id': user_id,
                'code_id': code_id,
                'age_id': '',  # Get all age grades
                'spage_id': '1',
                'is_fixture': '1',
            }
            
            try:
                response = self.session.post(
                    self.sportlomo_ajax_url,
                    data=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                html_content = data.get('html', '')
                
                if html_content and "not_found" not in html_content:
                    parsed_matches = self._parse_sportlomo_match_data(html_content)
                    if parsed_matches:
                        # Add sport and date info to each match
                        for match in parsed_matches:
                            match['sport'] = sport_name
                            match['scraped_date'] = date_str
                        all_matches.extend(parsed_matches)
                
                # Be respectful with requests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error getting {sport_name} fixtures for {date_str}: {e}")
            
            current_date += timedelta(days=1)
        
        return {
            'success': True,
            'fixtures': all_matches,
            'method': 'sportlomo_ajax',
            'sport': sport_name,
            'date_range': f"{from_date} to {to_date}",
            'source': 'sportlomo'
        }
    
    def get_all_sports_fixtures(self, from_date: str, to_date: str = None, sports: List[str] = None) -> Dict:
        """
        Get fixtures for all sports for the specified date range.
        
        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD), defaults to from_date
            sports: List of sports to scrape, defaults to all available
            
        Returns:
            Dictionary with all fixtures data
        """
        if to_date is None:
            to_date = from_date
            
        if sports is None:
            sports = list(self.sports_mapping.keys())
        
        all_fixtures = []
        results_by_sport = {}
        
        for sport in sports:
            print(f"Scraping {sport} fixtures from {from_date} to {to_date}...")
            
            result = self.get_sportlomo_fixtures(sport, from_date, to_date)
            results_by_sport[sport] = result
            
            if result.get('success') and result.get('fixtures'):
                all_fixtures.extend(result['fixtures'])
                print(f"  Found {len(result['fixtures'])} matches for {sport}")
            else:
                print(f"  No matches found for {sport}")
        
        return {
            'success': True,
            'total_fixtures': len(all_fixtures),
            'fixtures': all_fixtures,
            'by_sport': results_by_sport,
            'date_range': f"{from_date} to {to_date}",
            'sports_scraped': sports,
            'method': 'comprehensive_sportlomo'
        }
    
    def get_two_weeks_all_sports(self, start_date: str = None) -> Dict:
        """
        Get fixtures for all sports for the next two weeks.
        
        Args:
            start_date: Start date (YYYY-MM-DD), defaults to today
            
        Returns:
            Dictionary with comprehensive fixtures data
        """
        if start_date is None:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        # Calculate end date (14 days from start)
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = start_dt + timedelta(days=13)  # 13 days after start = 14 days total
        end_date = end_dt.strftime('%Y-%m-%d')
        
        print(f"Collecting comprehensive GAA fixtures data for 2 weeks:")
        print(f"Date range: {start_date} to {end_date}")
        print(f"Sports: {list(self.sports_mapping.keys())}")
        print("-" * 60)
        
        return self.get_all_sports_fixtures(start_date, end_date)
    
    def _get_csrf_token(self) -> Optional[str]:
        """
        Get CSRF token from the main page for authenticated requests.
        
        Returns:
            CSRF token string or None if not found
        """
        try:
            response = self.session.get(f"{self.base_url}/mens-football/club-fixtures-results")
            response.raise_for_status()
            
            # Look for common CSRF token patterns in WordPress
            import re
            content = response.text
            
            # Try to find nonce in various formats
            patterns = [
                r'wpAjaxNonce["\']?\s*:\s*["\']([^"\']+)["\']',
                r'nonce["\']?\s*:\s*["\']([^"\']+)["\']',
                r'_wpnonce["\']?\s*:\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
                    
            return None
        except Exception as e:
            print(f"Error getting CSRF token: {e}")
            return None
    
    def get_fixtures(self, 
                    from_date: str = None, 
                    to_date: str = None,
                    **kwargs) -> Dict:
        """
        Get fixtures data from the Dublin GAA datafeed.
        
        Args:
            from_date: Start date in YYYY-MM-DD format (defaults to today)
            to_date: End date in YYYY-MM-DD format (defaults to today)
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Dictionary containing the fixtures data
        """
        # Set default dates if not provided
        if not from_date:
            from_date = datetime.now().strftime('%Y-%m-%d')
        if not to_date:
            to_date = from_date
            
        # Try the main Dublin GAA site first
        result = self._try_main_site(from_date, to_date, **kwargs)
        
        # If main site fails, try SportLoMo AJAX (new improved method)
        if not result.get('success'):
            print("Main site failed, trying SportLoMo AJAX...")
            # Default to Male Football if no sport specified
            sport = kwargs.get('sport', 'Male Football')
            result = self.get_sportlomo_fixtures(sport, from_date, to_date)
        
        return result
    
    def _try_main_site(self, from_date: str, to_date: str, **kwargs) -> Dict:
        """Try to get data from the main Dublin GAA WordPress site."""
        # Prepare parameters
        params = self.default_params.copy()
        params.update({
            'fdate': from_date,
            'tdate': to_date,
            **kwargs
        })
        
        # Get CSRF token
        csrf_token = self._get_csrf_token()
        if csrf_token:
            params['_wpnonce'] = csrf_token
        
        try:
            # Make the request
            response = self.session.post(
                self.datafeed_url,
                data=params,
                timeout=30
            )
            
            # Handle different response scenarios
            if response.status_code == 403:
                return {'success': False, 'error': 'Access forbidden to main site'}
            
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                data = response.json()
                return {'success': True, 'data': data, 'source': 'main_site'}
            except json.JSONDecodeError:
                # If not JSON, return raw text
                return {
                    'success': True,
                    'raw_data': response.text,
                    'content_type': response.headers.get('content-type', ''),
                    'source': 'main_site'
                }
                
        except requests.RequestException as e:
            return {'success': False, 'error': f"Main site request failed: {str(e)}"}
    
    def _try_sportlomo(self, from_date: str, to_date: str, **kwargs) -> Dict:
        """Try to get data from the SportLoMo site."""
        try:
            # First, get the fixtures page to understand the structure
            fixtures_url = f"{self.sportlomo_url}/fixtures/"
            response = self.session.get(fixtures_url, timeout=30)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for fixtures data
            fixtures = self._extract_sportlomo_fixtures(soup, from_date, to_date)
            
            return {
                'success': True,
                'fixtures': fixtures,
                'method': 'sportlomo_scraping',
                'date_range': f"{from_date} to {to_date}",
                'source': 'sportlomo'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"SportLoMo scraping failed: {str(e)}"
            }
    
    def _extract_sportlomo_fixtures(self, soup, from_date: str, to_date: str) -> List[Dict]:
        """
        Extract fixtures from SportLoMo HTML.
        
        Args:
            soup: BeautifulSoup object of the page
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            List of fixture dictionaries
        """
        fixtures = []
        
        # Look for common fixture table/list patterns
        fixture_selectors = [
            'div.fixture-item',
            'tr.fixture-row',
            'div[class*="fixture"]',
            'div[class*="match"]',
            'tbody tr',
            '.fixture',
            '.match-row'
        ]
        
        for selector in fixture_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                
                for element in elements:
                    fixture = self._parse_sportlomo_fixture(element)
                    if fixture and self._is_date_in_range(fixture.get('date', ''), from_date, to_date):
                        fixtures.append(fixture)
                
                if fixtures:
                    break  # Use the first selector that finds fixtures
        
        # If no structured fixtures found, try to extract any date/match information
        if not fixtures:
            fixtures = self._extract_general_match_info(soup, from_date, to_date)
        
        return fixtures
    
    def _parse_sportlomo_fixture(self, element) -> Optional[Dict]:
        """
        Parse a fixture element from SportLoMo.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Dictionary with fixture data or None
        """
        try:
            fixture = {}
            
            # Try to extract date
            date_patterns = [
                r'(\d{2}/\d{2}/\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{1,2}/\d{1,2}/\d{4})'
            ]
            
            element_text = element.get_text()
            for pattern in date_patterns:
                match = re.search(pattern, element_text)
                if match:
                    fixture['date'] = match.group(1)
                    break
            
            # Try to extract time
            time_match = re.search(r'(\d{1,2}:\d{2})', element_text)
            if time_match:
                fixture['time'] = time_match.group(1)
            
            # Try to extract team names (look for patterns like "Team A V Team B")
            teams_match = re.search(r'([A-Za-z\s]+)\s+V\s+([A-Za-z\s]+)', element_text)
            if teams_match:
                fixture['team1'] = teams_match.group(1).strip()
                fixture['team2'] = teams_match.group(2).strip()
            
            # Try to extract venue
            venue_keywords = ['Park', 'Ground', 'Pitch', 'Field', 'GAA']
            words = element_text.split()
            for i, word in enumerate(words):
                if any(keyword in word for keyword in venue_keywords):
                    # Take this and maybe next few words as venue
                    venue_parts = words[i:i+3]
                    fixture['venue'] = ' '.join(venue_parts)
                    break
            
            # Add competition info if available
            if 'AFL' in element_text or 'Football' in element_text:
                fixture['competition'] = 'Football'
            elif 'Hurling' in element_text or 'HL' in element_text:
                fixture['competition'] = 'Hurling'
            
            # Only return if we found at least some useful data
            if any(key in fixture for key in ['date', 'team1', 'team2']):
                return fixture
                
            return None
            
        except Exception as e:
            print(f"Error parsing fixture element: {e}")
            return None
    
    def _extract_general_match_info(self, soup, from_date: str, to_date: str) -> List[Dict]:
        """
        Extract any match/fixture information from the page using general patterns.
        
        Args:
            soup: BeautifulSoup object
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            List of fixture dictionaries
        """
        fixtures = []
        
        # Look for any text that mentions dates and teams
        text_content = soup.get_text()
        
        # Find potential fixture lines
        lines = text_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for lines with dates and team patterns
            if re.search(r'\d{1,2}/\d{1,2}/\d{4}', line) and ('V' in line or 'v' in line):
                fixture = self._parse_fixture_line(line)
                if fixture and self._is_date_in_range(fixture.get('date', ''), from_date, to_date):
                    fixtures.append(fixture)
        
        return fixtures
    
    def _parse_fixture_line(self, line: str) -> Optional[Dict]:
        """Parse a single line that might contain fixture information."""
        try:
            fixture = {}
            
            # Extract date
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', line)
            if date_match:
                fixture['date'] = date_match.group(1)
            
            # Extract time
            time_match = re.search(r'(\d{1,2}:\d{2})', line)
            if time_match:
                fixture['time'] = time_match.group(1)
            
            # Extract teams (before and after V/v)
            teams_match = re.search(r'([A-Za-z\s]+?)\s*[Vv]\s*([A-Za-z\s]+)', line)
            if teams_match:
                fixture['team1'] = teams_match.group(1).strip()
                fixture['team2'] = teams_match.group(2).strip()
            
            # Add source line for debugging
            fixture['source_line'] = line
            
            return fixture if fixture else None
            
        except Exception:
            return None
    
    def _is_date_in_range(self, date_str: str, from_date: str, to_date: str) -> bool:
        """
        Check if a date string falls within the specified range.
        
        Args:
            date_str: Date string to check
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            
        Returns:
            True if date is in range
        """
        try:
            if not date_str:
                return False
                
            # Convert date_str to standard format
            if '/' in date_str:
                # Assume DD/MM/YYYY or MM/DD/YYYY format
                parts = date_str.split('/')
                if len(parts) == 3:
                    # Try DD/MM/YYYY first (more common in Ireland)
                    try:
                        check_date = datetime.strptime(date_str, '%d/%m/%Y')
                    except ValueError:
                        # Try MM/DD/YYYY
                        check_date = datetime.strptime(date_str, '%m/%d/%Y')
                else:
                    return False
            else:
                # Assume YYYY-MM-DD format
                check_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            
            return from_date_obj <= check_date <= to_date_obj
            
        except Exception:
            return True  # Include if we can't parse the date
    
    def _fallback_scrape(self, from_date: str, to_date: str) -> Dict:
        """
        Fallback method to scrape fixtures using HTML parsing when API is blocked.
        
        Args:
            from_date: Start date
            to_date: End date
            
        Returns:
            Dictionary with scraped data
        """
        try:
            from bs4 import BeautifulSoup
            
            # Try the filter URL format
            filter_url = f"{self.base_url}/fixtures/filter/{to_date}/{from_date}/all/all/all/all"
            response = self.session.get(filter_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract fixtures data from HTML
                fixtures = []
                # This would need to be customized based on the actual HTML structure
                fixture_elements = soup.find_all('div', class_='fixture-item')  # Example selector
                
                for element in fixture_elements:
                    # Extract fixture details
                    fixture = self._extract_fixture_from_element(element)
                    if fixture:
                        fixtures.append(fixture)
                
                return {
                    'success': True,
                    'method': 'html_scraping',
                    'fixtures': fixtures,
                    'date_range': f"{from_date} to {to_date}"
                }
            else:
                return {
                    'success': False,
                    'error': f"Fallback scraping failed with status {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Fallback scraping error: {str(e)}"
            }
    
    def _extract_fixture_from_element(self, element) -> Optional[Dict]:
        """
        Extract fixture information from an HTML element.
        
        Args:
            element: BeautifulSoup element containing fixture data
            
        Returns:
            Dictionary with fixture details or None
        """
        try:
            # This is a template - would need to be customized based on actual HTML structure
            fixture_data = {
                'date': element.get('data-date', ''),
                'competition': element.get('data-competition', '')
            }
            
            # Safely extract text from elements
            time_elem = element.find('span', class_='time')
            if time_elem:
                fixture_data['time'] = time_elem.text.strip()
            else:
                fixture_data['time'] = ''
                
            team1_elem = element.find('span', class_='team1')
            if team1_elem:
                fixture_data['team1'] = team1_elem.text.strip()
            else:
                fixture_data['team1'] = ''
                
            team2_elem = element.find('span', class_='team2')
            if team2_elem:
                fixture_data['team2'] = team2_elem.text.strip()
            else:
                fixture_data['team2'] = ''
                
            venue_elem = element.find('span', class_='venue')
            if venue_elem:
                fixture_data['venue'] = venue_elem.text.strip()
            else:
                fixture_data['venue'] = ''
            
            return fixture_data
        except Exception:
            return None
    
    def get_date_range_fixtures(self, 
                               start_date: str, 
                               end_date: str, 
                               batch_size: int = 7) -> List[Dict]:
        """
        Get fixtures for a date range, making multiple requests if needed.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            batch_size: Number of days to request in each batch
            
        Returns:
            List of all fixtures in the date range
        """
        all_fixtures = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current_date <= end_date_obj:
            batch_end = min(current_date + timedelta(days=batch_size - 1), end_date_obj)
            
            print(f"Fetching fixtures from {current_date.strftime('%Y-%m-%d')} to {batch_end.strftime('%Y-%m-%d')}")
            
            result = self.get_fixtures(
                from_date=current_date.strftime('%Y-%m-%d'),
                to_date=batch_end.strftime('%Y-%m-%d')
            )
            
            if result.get('success'):
                if 'fixtures' in result:
                    all_fixtures.extend(result['fixtures'])
                else:
                    all_fixtures.append(result)
            else:
                print(f"Failed to get fixtures for {current_date.strftime('%Y-%m-%d')}: {result.get('error')}")
            
            current_date = batch_end + timedelta(days=1)
            time.sleep(1)  # Be respectful with requests
        
        return all_fixtures
    
    def to_dataframe(self, fixtures_data: List[Dict]) -> pd.DataFrame:
        """
        Convert fixtures data to a pandas DataFrame.
        
        Args:
            fixtures_data: List of fixture dictionaries
            
        Returns:
            pandas DataFrame with fixtures data
        """
        if not fixtures_data:
            return pd.DataFrame()
        
        # Normalize the data structure
        normalized_data = []
        for fixture in fixtures_data:
            if isinstance(fixture, dict):
                normalized_data.append(fixture)
        
        df = pd.DataFrame(normalized_data)
        
        # Reorder columns for cleaner output if they exist
        preferred_order = ['sport', 'date', 'time', 'competition', 'home_team', 'away_team', 'venue', 'referee']
        existing_cols = [col for col in preferred_order if col in df.columns]
        other_cols = [col for col in df.columns if col not in preferred_order]
        
        if existing_cols:
            df = df[existing_cols + other_cols]
        
        return df
    
    def save_to_csv(self, fixtures_data: List[Dict], filename: str) -> bool:
        """
        Save fixtures data to a CSV file.
        
        Args:
            fixtures_data: List of fixture dictionaries
            filename: Output CSV filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            df = self.to_dataframe(fixtures_data)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False
    
    def get_specific_competitions(self, competition_codes: List[str] = None) -> Dict:
        """
        Get fixtures for specific competitions.
        
        Args:
            competition_codes: List of competition codes to filter by
            
        Returns:
            Dictionary with competition fixtures
        """
        if not competition_codes:
            # Default to main football competitions
            competition_codes = ['26']  # Football code
        
        results = {}
        for code in competition_codes:
            print(f"Fetching fixtures for competition code: {code}")
            result = self.get_fixtures(code_id=code)
            results[code] = result
            time.sleep(1)
        
        return results


def main():
    """Example usage of the Dublin GAA scraper."""
    scraper = DublinGAAScraper()
    
    # Get comprehensive data for the next two weeks
    print("Fetching comprehensive GAA fixtures for the next 2 weeks...")
    comprehensive_data = scraper.get_two_weeks_all_sports()
    
    if comprehensive_data.get('success'):
        print(f"\nTotal fixtures found: {comprehensive_data['total_fixtures']}")
        print(f"Date range: {comprehensive_data['date_range']}")
        print(f"Sports covered: {comprehensive_data['sports_scraped']}")
        
        # Save comprehensive data
        if comprehensive_data['fixtures']:
            scraper.save_to_csv(comprehensive_data['fixtures'], 'comprehensive_gaa_fixtures.csv')
        
        # Show summary by sport
        print("\nSummary by sport:")
        for sport, result in comprehensive_data['by_sport'].items():
            fixture_count = len(result.get('fixtures', []))
            print(f"  {sport}: {fixture_count} fixtures")
    
    print(f"\nScraping complete!")


if __name__ == "__main__":
    main() 