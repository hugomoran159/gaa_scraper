# Dublin GAA Fixtures Scraper

A Python scraper for extracting fixtures and results data from the Dublin GAA website. This tool interfaces with the WordPress datafeed endpoint to retrieve structured GAA fixtures information.

## Features

- **WordPress Datafeed Integration**: Direct access to the Dublin GAA WordPress datafeed API
- **Flexible Date Ranges**: Retrieve fixtures for specific dates or date ranges
- **Multiple Data Formats**: Support for JSON and CSV output
- **Error Handling**: Robust error handling with fallback HTML scraping
- **Competition Filtering**: Filter fixtures by specific competitions or codes
- **Rate Limiting**: Built-in delays to be respectful to the server
- **Session Management**: Proper session handling with CSRF token support

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Prerequisites

- Python 3.8+
- uv package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd gaa_scraper
```

2. Install dependencies:
```bash
uv sync
```

3. Activate the virtual environment:
```bash
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

## Quick Start

### Basic Usage

```python
from src.gaa_scraper import DublinGAAScraper
from datetime import datetime, timedelta

# Initialize the scraper
scraper = DublinGAAScraper()

# Get today's fixtures
fixtures = scraper.get_fixtures()
print(fixtures)

# Get fixtures for a date range
start_date = datetime.now().strftime('%Y-%m-%d')
end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

weekly_fixtures = scraper.get_date_range_fixtures(start_date, end_date)

# Save to CSV
scraper.save_to_csv(weekly_fixtures, 'gaa_fixtures.csv')
```

### Command Line Usage

Run the main script:
```bash
python main.py
```

Run example scripts:
```bash
python examples/basic_usage.py
python examples/advanced_usage.py
```

## API Reference

### DublinGAAScraper Class

#### Constructor

```python
DublinGAAScraper(base_url: str = "https://www.dublingaa.ie")
```

#### Methods

##### `get_fixtures(from_date=None, to_date=None, **kwargs)`

Retrieve fixtures data from the Dublin GAA datafeed.

**Parameters:**
- `from_date` (str): Start date in YYYY-MM-DD format (defaults to today)
- `to_date` (str): End date in YYYY-MM-DD format (defaults to today)
- `**kwargs`: Additional parameters for the datafeed

**Available kwargs:**
- `code_id` (str): Competition code (default: '26' for Football)
- `code_name` (str): Competition name (default: 'Football')
- `user_id` (str): User IDs for permissions (default: '3,7167,7130')
- `age_id` (str): Age group filter
- `club_search_id` (str): Club filter
- `comp_search_id` (str): Competition filter
- `is_fixture` (str): '1' for fixtures, '0' for results
- `debug` (str): '1' to enable debug mode

**Returns:** Dictionary with fixtures data

##### `get_date_range_fixtures(start_date, end_date, batch_size=7)`

Get fixtures for a date range with automatic batching.

**Parameters:**
- `start_date` (str): Start date in YYYY-MM-DD format
- `end_date` (str): End date in YYYY-MM-DD format
- `batch_size` (int): Number of days per batch request

**Returns:** List of fixture dictionaries

##### `to_dataframe(fixtures_data)`

Convert fixtures data to a pandas DataFrame.

**Parameters:**
- `fixtures_data` (List[Dict]): List of fixture dictionaries

**Returns:** pandas DataFrame

##### `save_to_csv(fixtures_data, filename)`

Save fixtures data to a CSV file.

**Parameters:**
- `fixtures_data` (List[Dict]): List of fixture dictionaries
- `filename` (str): Output CSV filename

**Returns:** Boolean indicating success

## Configuration

### Default Parameters

The scraper uses these default parameters for the WordPress datafeed:

```python
{
    'action': 'get_fixtures',
    'user_id': '3,7167,7130',
    'code_id': '26',           # Football
    'code_name': 'Football',
    'spage_id': '1',
    'debug': '1',
    'is_fixture': '1',
    'age_id': '',
    'club_search_id': '',
    'comp_search_id': ''
}
```

### Competition Codes

Common competition codes:
- `26`: Football
- Add other codes as discovered

## Error Handling

The scraper includes robust error handling:

1. **CSRF Token Management**: Automatically retrieves and uses CSRF tokens
2. **Fallback Scraping**: Falls back to HTML parsing if API access is blocked
3. **Network Timeouts**: Configurable request timeouts
4. **Rate Limiting**: Built-in delays between requests

## Examples

### Example 1: Get Weekly Fixtures

```python
from src.gaa_scraper import DublinGAAScraper
from datetime import datetime, timedelta

scraper = DublinGAAScraper()

# Get next week's fixtures
today = datetime.now()
next_week = today + timedelta(days=7)

fixtures = scraper.get_date_range_fixtures(
    start_date=today.strftime('%Y-%m-%d'),
    end_date=next_week.strftime('%Y-%m-%d')
)

print(f"Found {len(fixtures)} fixtures")
```

### Example 2: Filter by Competition

```python
scraper = DublinGAAScraper()

# Get football fixtures only
football_fixtures = scraper.get_fixtures(
    from_date='2025-01-10',
    to_date='2025-01-15',
    code_id='26',
    code_name='Football'
)
```

### Example 3: Process with Pandas

```python
import pandas as pd

scraper = DublinGAAScraper()
fixtures = scraper.get_date_range_fixtures('2025-01-01', '2025-01-31')

# Convert to DataFrame
df = scraper.to_dataframe(fixtures)

# Analyze data
if not df.empty:
    print(f"Total fixtures: {len(df)}")
    print(f"Competitions: {df['competition'].nunique()}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
```

## Development

### Project Structure

```
gaa_scraper/
├── src/
│   ├── __init__.py
│   └── gaa_scraper.py      # Main scraper class
├── examples/
│   ├── basic_usage.py      # Basic usage examples
│   └── advanced_usage.py   # Advanced usage examples
├── main.py                 # Main entry point
├── pyproject.toml         # Project configuration
├── uv.lock               # Dependency lock file
└── README.md             # This file
```

### Adding New Features

1. Extend the `DublinGAAScraper` class
2. Add new methods for specific functionality
3. Update tests and examples
4. Update documentation

### Testing

Run the main test script:
```bash
python main.py
```

Run specific examples:
```bash
python examples/basic_usage.py
python examples/advanced_usage.py
```

## Troubleshooting

### Common Issues

1. **403 Forbidden Errors**: The datafeed endpoint may block requests without proper CSRF tokens. The scraper automatically handles this with fallback methods.

2. **Empty Results**: Check that the date range and competition codes are valid.

3. **Network Timeouts**: Increase the timeout in the session configuration.

4. **Rate Limiting**: The scraper includes built-in delays. Avoid making too many rapid requests.

### Debug Mode

Enable debug mode for more verbose output:

```python
fixtures = scraper.get_fixtures(debug='1')
```

## Dependencies

- `requests`: HTTP client library
- `beautifulsoup4`: HTML parsing for fallback scraping
- `lxml`: XML parser for BeautifulSoup
- `pandas`: Data manipulation and analysis

## License

[Add your license here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review the examples
3. Create an issue on GitHub

## Changelog

### v1.0.0
- Initial release
- WordPress datafeed integration
- CSV export functionality
- Error handling and fallback scraping
- Date range support
