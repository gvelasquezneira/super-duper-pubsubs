# super-duper-pubsubs
**Purpose**
- The scraper was created to check for price gouging, inflation and to compare local supermarket prices. 

**Features**
- Scrapes product details from various categories, creating a personal CPI. 
- Supports parallel processing of multiple locations using Python's multiprocessing.
- Handles dynamic page loading with scrolling and "Load More" buttons.
- Saves data to CSV file.
- Has unique identifiers to build a database. 
- Automated via GitHub Actions for scheduled runs.

**Prerequisites**
- Python: 3.10 or higher
- Playwright: For browser automation
- Operating System: Tested on Ubuntu (via GitHub Actions); should work on Windows/Mac with minor adjustments

**Performance**
- 900 Locations in total.
- Completes the work in about 18 hours (This is to not hit rate limits)
- Parallel Processing set up to reduce wait-times.
