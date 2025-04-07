# super-duper-pubsubs
**Purpose**
- The scraper was created to check for price gouging, inflation and to compare local supermarket prices. 

**Features**
- Scrapes product details from various categories. The 
- Supports parallel processing of multiple locations using Python's multiprocessing.
- Handles dynamic page loading with scrolling and "Load More" buttons.
- Saves data to CSV files (one main file and location-specific backups).
- Includes retry logic for robust navigation and error handling with screenshots for debugging.
- Automated via GitHub Actions for scheduled runs.

**Prerequisites**
- Python: 3.10 or higher
- Playwright: For browser automation
- Operating System: Tested on Ubuntu (via GitHub Actions); should work on Windows/Mac with minor adjustments

**Performance**
- Single Location: ~42 minutes (This is a work in progress).
- 900 Locations in total.
- Parallel Processing set up to reduce wait-times.
