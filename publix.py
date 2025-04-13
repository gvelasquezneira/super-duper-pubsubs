from playwright.sync_api import sync_playwright
import csv
import time
from datetime import datetime
import multiprocessing
import os
from functools import partial
import traceback
import random
import argparse
import hashlib
import re

# Define a list of user agents to rotate between
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/121.0.0.0",
    
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    
    # Mobile user agents
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.90 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.90 Mobile Safari/537.36",
]

# Define the target products to find in each category
TARGET_PRODUCTS = {
    "Beef": [
        "publix lean ground beef",
        "publix bottom round roast",
        "publix beef patties",
        "usda choice beef"
    ],
    "Bread": [
        "pepperidge farm white bread",
        "publix bread 100% whole wheat",
        "publix bakery sourdough round",
        "publix bread white old fashioned enriched"
    ],
    "Butter": [
        "publix butter sweet cream unsalted",
        "publix butter salted sweet cream",
        "land o lakes butter with canola oil",
        "land o lakes salted butter"
    ],
    "Canned Beans": [
        "publix black beans",
        "publix kidney beans light red",
        "bush's best pinto beans",
        "old el paso refried beans black bean",
        "goya premium black beans",
        "goya premium pinto beans"
    ],
    "Cereal": [
        "quaker original multigrain cereal",
        "kellogg's special k",
        "cap'n crunch cereal",
        "general mills honey nut cheerios",
        "frosted flakes"
    ],
    "Chicken": [
        "publix boneless skinless chicken breast",
        "publix chicken all natural boneless skinless chicken thighs",
        "publix whole young chicken"
    ],
    "Chips": [
        "lay's potato chips classic",
        "tostitos tortilla chips original scoops party size",
        "frito lay snacks classic mix variety",
        "lay's potato chips barbecue",
        "cape cod sea salt & vinegar chips"
    ],
    "Coffee": [
        "maxwell house house blend medium roast",
        "café bustelo roast & ground coffee",
        "publix coffee espresso cafe espresso",
        "nescafé clásico dark roast instant coffee",
        "dunkin' decaf original blend ground coffee"
    ],
    "Cooking Oils": [
        "publix vegetable oil",
        "bertolli olive oil extra virgin",
        "publix canola oil",
        "publix coconut oil",
        "pam non stick butter cooking spray",
        "publix olive oil extra virgin",
        "crisco oil pure canola"
    ],
    "Deli Meats": [
        "prime fresh honey ham",
        "smithfield turkey breast",
        "publix chicken rotisserie seasoned thin sliced",
        "publix deli salami genoa sliced",
        "hormel pepperoni original"
    ],
    "Eggs": [
        "publix eggs large",
        "publix large grade a eggs",
        "eggland's best grade a large white eggs",
        "publix eggs medium",
        "eggland's best classic extra large white eggs"
    ],
    "Fresh Fruits": [
        "gala apple",
        "bananas",
        "navel oranges",
        "strawberries",
        "red seedless grapes",
        "lemon"
    ],
    "Fresh Vegetables": [
        "russet potatoes",
        "publix yellow onions",
        "publix carrots sticks",
        "romaine lettuce",
        "asparagus",
        "red onion",
        "cucumber",
        "broccoli",
        "garlic",
        "shallot",
        "greenwise organic spinach",
        "tomatoes on the vine"
    ],
    "Jams Jellies": [
        "smucker's strawberry jelly",
        "publix jelly concord grape",
        "welch's concord grape jelly",
        "smucker's jam"
    ],
    "Juice": [
        "tropicana pure premium 100% orange juice",
        "publix original orange juice",
        "welch's passion fruit",
        "mott's 100% original apple juice",
        "simply lemonade"
    ],
    "Lager": [
        "budweiser american lager beer",
        "corona extra mexican lager",
        "heineken original lager beer"
    ],
    "Light Beer": [
        "bud light platinum",
        "coors light american light lager beer",
        "miller lite american light lager beer",
        "michelob ultra superior light american lager beer"
    ],
    "Milk": [
        "publix milk whole",
        "publix milk reduced fat 2% milkfat",
        "silk soy milk original",
        "publix milk chocolate", 
        "%"
    ],
    "Pasta": [
        "publix spaghetti",
        "barilla whole grain spaghetti",
        "barilla penne",
        "publix pasta penne rigate",
        "publix angel hair"
    ],
    "Red Wine": [
        "josh cellars cabernet sauvignon",
        "robert mondavi private selection bourbon barrel aged cabernet sauvignon",
        "apothic red blend",
        "yellow tail merlot",
        "barefoot pinot noir"
    ],
    "Spices Seasoning": [
        "mccormick black pepper ground",
        "mccormick gourmet organic paprika",
        "publix onion powder",
        "publix paprika",
        "publix garlic powder",
        "spice islands cilantro",
        "mccormick ground cinnamon",
        "mccormick gourmet organic italian seasoning"
    ],
    "White Wine": [
        "kendall-jackson chardonnay",
        "santa margherita pinot grigio",
        "barefoot chardonnay",
        "yellow tail pinot grigio",
        "yellow tail chardonnay"
    ],
    "Cheese": [
        "kraft shredded cheese mozzarella",
        "publix cheese singles american",
        "publix cheese swiss",
        "publix cheese grated parmesan",
        "boar's head irish cheddar cheese"
    ],
    "Baby Food Drinks": [
        "gerber apples 2nd foods",
        "gerber stage 2"
    ],
    "Paper Goods": [
        "bounty full sheet paper towels",
        "charmin ultra soft toilet paper mega rolls",
        "vanity fair napkin"
    ],
    "Trash Bins Bags": [
        "publix tall kitchen garbage bags",
        "hefty trash bags",
        "glad kitchen bags"
    ]
}

def extract_item_details(deli_item, location):
    """Extract item details from a product element."""
    price = "Not found"
    for price_class in ['div.e-2feaft', 'div.e-s71gfs']:
        price_div = deli_item.locator(price_class).first
        price_span = price_div.locator('span.screen-reader-only').first
        if price_span.count() > 0:
            full_price = price_span.inner_text()
            price = full_price.split('$')[1] if '$' in full_price else full_price
            break

    grocery_div = deli_item.locator('div.e-147kl2c').first
    product_name = grocery_div.inner_text() if grocery_div.count() > 0 else "Not found"

    ozs_div = deli_item.locator('div.e-an4oxa').first
    size = ozs_div.inner_text() if ozs_div.count() > 0 else "Not found"

    return {
        "Location": location,
        "Product Name": product_name,
        "Price": price,  
        "Size": size  
    }

def scroll_to_load_all_items(page):
    last_height = page.evaluate("document.body.scrollHeight")
    max_scroll_attempts = 5 
    scroll_attempts = 0
    
    while scroll_attempts < max_scroll_attempts:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        
        # Add randomized delay between scrolls to appear more human-like
        page.wait_for_timeout(random.randint(700, 1200))  
        
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            final_height = page.evaluate("document.body.scrollHeight")
            if final_height == new_height:
                break
        
        last_height = new_height
        scroll_attempts += 1
        
    # Check for "Load More" buttons
    try:
        load_more = page.locator("button:has-text('Load More')").first
        if load_more.count() > 0 and load_more.is_visible():
            load_more.click()
            # Wait longer after clicking "Load More"
            page.wait_for_timeout(random.randint(1200, 2000))
    except Exception as e:
        pass 

def navigate_with_retry(page, url, max_retries=3):
    """Navigate to URL with retry logic and exponential backoff"""
    for attempt in range(max_retries):
        try:
            page.goto(url, wait_until="domcontentloaded")
            
            # Add randomized delay to appear more human-like
            wait_time = random.uniform(1.0, 3.0)  # More substantial wait after navigation
            time.sleep(wait_time)
            
            if page.url.startswith(url.split("?")[0]):  
                return True
            else:
                # If we're redirected, wait longer before retrying
                time.sleep(random.uniform(3.0, 5.0))
        except Exception as e:
            # Implement exponential backoff
            backoff_time = (2 ** attempt) + random.uniform(0.5, 1.5)
            print(f"Navigation attempt {attempt+1} failed. Waiting {backoff_time:.2f}s before retry...")
            time.sleep(backoff_time)
    
    print(f"Failed to navigate to {url} after {max_retries} attempts")
    return False


def is_target_product(product_name, category):
    """Check if the product is one of our target products for this category"""
    if category not in TARGET_PRODUCTS:
        return False
        
    product_name_lower = product_name.lower()

    for target in TARGET_PRODUCTS[category]:
        if target in product_name_lower:
            return True
    
    return False

def clean_price(price_str):
    """Convert price string to float, removing $ and any other non-numeric characters except decimal."""
    if price_str == "Not found":
        return ""
    
    price_match = re.search(r'(\d+\.\d+|\d+)', price_str)
    if price_match:
        return float(price_match.group(1))
    return ""

def generate_store_id(location):
    """Generate a consistent unique ID for a store location."""
    # Use MD5 hash of location string to generate a unique but consistent ID
    hash_obj = hashlib.md5(location.encode())
    return hash_obj.hexdigest()[:8]

def scrape_deli_items(page, location, category, store_id):
    """Enhanced scraping function that filters for target products only"""
    scroll_to_load_all_items(page)
    
    # Try multiple selectors to find products
    selectors = ['h3.e-ti75j2', 'div.e-1qh5kfx', 'div.product-item', 'li.product-item']
    
    items = None
    items_count = 0
    used_selector = ""
    
    for selector in selectors:
        items = page.locator(selector)
        items_count = items.count()
        if items_count > 0:
            used_selector = selector
            break
    
    if items_count == 0:
        return []

    deli_data = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for i in range(items_count):
        try:
            item = items.nth(i)
            
            # If using a different selector than the original, adjust extraction logic
            if used_selector != 'h3.e-ti75j2':
                # Try to find the product name and price within this item
                name_element = item.locator('h3, .product-name, div.e-147kl2c').first
                price_element = item.locator('.product-price, div.e-2feaft, div.e-s71gfs').first
                
                product_name = name_element.inner_text() if name_element.count() > 0 else "Not found"
                price = price_element.inner_text() if price_element.count() > 0 else "Not found"
                
                # Try to find size information (previously ounces)
                size_element = item.locator('div.e-an4oxa, .product-size').first
                size = size_element.inner_text() if size_element.count() > 0 else "Not found"
                
                # Only add if it's a target product
                if is_target_product(product_name, category):
                    # Generate unique row ID with timestamp and index
                    row_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}"
                    
                    # Clean price to remove $ and convert to float
                    clean_price_val = clean_price(price)
                    
                    row = [
                        row_id,              # Unique ID for row
                        store_id,            # Unique store ID
                        location,
                        category,
                        product_name,
                        clean_price_val,     # Price as float without $
                        size,                # Renamed from "ounces"
                        current_date
                    ]
                    deli_data.append(row)
            else:
                item_details = extract_item_details(item, location)
                
                # Only add if it's a target product
                if is_target_product(item_details["Product Name"], category):
                    # Generate unique row ID with timestamp and index
                    row_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}"
                    
                    # Clean price to remove $ and convert to float
                    clean_price_val = clean_price(item_details["Price"])
                    
                    row = [
                        row_id,            
                        store_id,           
                        item_details["Location"],
                        category,
                        item_details["Product Name"],
                        clean_price_val,  
                        item_details["Size"],
                        current_date
                    ]
                    deli_data.append(row)
        except Exception as e:
            continue
    
    return deli_data

def append_to_csv(filename, data, lock=None):
    if not data:
        return
    
    if lock:
        lock.acquire()
    
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(data)
    finally:
        if lock:
            lock.release()

def process_location(location_data, urls, output_file, lock, headless=True):
    """Process a single location in its own process"""
    location, worker_id = location_data
    
    try:
        # Select a random user agent
        user_agent = random.choice(USER_AGENTS)
        print(f"Worker {worker_id}: Using user agent: {user_agent}")
        
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=headless)
            
            # Create context with the randomized user agent and viewport
            viewport_width = random.randint(1280, 1920)
            viewport_height = random.randint(800, 1080)
            
            context = browser.new_context(
                permissions=["geolocation"],
                viewport={"width": viewport_width, "height": viewport_height},
                user_agent=user_agent
            )
            
            page = context.new_page()
            
            # Generate store ID for this location
            store_id = generate_store_id(location)
            
            # Add some randomness to timings to appear more human-like
            page.set_default_timeout(30000)  # Generous timeout for operations
            
            if not navigate_with_retry(page, "https://delivery.publix.com/store/publix/storefront"):
                browser.close()
                return

            # Handle Confirm button
            try:
                continue_button = page.get_by_role("button", name="Confirm")
                if continue_button.is_visible():
                    continue_button.click()
                    # Add random delay after clicking button
                    time.sleep(random.uniform(1.0, 2.0))
            except Exception as e:
                print(f"Error with Confirm button for {location}: {e}")

            # Change location
            try:
                # Try to click on the location/address selector first
                location_button_selectors = ["button.e-16343ho", "div.e-1w159j"]
                print(f"Worker {worker_id}: Trying to change location to {location}")
                
                zip_button = None
                for selector in location_button_selectors:
                    zip_button = page.locator(selector).first
                    if zip_button.count() > 0 and zip_button.is_visible(timeout=1000):
                        print(f"Worker {worker_id}: Found and clicking location button with selector: {selector}")
                        zip_button.click()
                        # Add random delay after clicking
                        time.sleep(random.uniform(0.8, 1.5))
                        break
                
                # Now try to click the "Edit" button in the new interface
                edit_button = page.locator("div.e-mf50rh").filter(has_text="Edit").first
                if edit_button.count() > 0 and edit_button.is_visible(timeout=1000):
                    print(f"Worker {worker_id}: Found and clicking 'Edit' button")
                    edit_button.click()
                    # Add random delay after clicking
                    time.sleep(random.uniform(0.8, 1.5))
                else:
                    print(f"Worker {worker_id}: 'Edit' button not found or not visible")
                    # Try some alternative selectors if the Edit div isn't found
                    alternative_edit_selectors = [
                        "div:has-text('Edit'):not(:has(div, span))",  # Edit text without nested elements
                        "div.e-mf50rh",                               # The class you mentioned
                        "div[role='button']:has-text('Edit')"         # Edit with button role
                    ]
                    
                    for selector in alternative_edit_selectors:
                        edit_elem = page.locator(selector).first
                        if edit_elem.count() > 0 and edit_elem.is_visible(timeout=1000):
                            print(f"Worker {worker_id}: Found and clicking alternative Edit button: {selector}")
                            edit_elem.click()
                            # Add random delay after clicking
                            time.sleep(random.uniform(0.8, 1.5))
                            break

                address_input = page.locator("input#streetAddress").first
                if address_input.count() == 0:
                    # Try additional input selectors if the original one isn't found
                    address_input = page.locator("input[placeholder*='address'], input[aria-label*='address'], input[type='text']:visible").first
                
                if address_input.count() > 0:
                    address_input.click()
                    # Type more like a human with variable delays between characters
                    address_input.fill("")
                    time.sleep(random.uniform(0.2, 0.4))
                    
                    # Type the address with human-like timing
                    for char in location:
                        address_input.type(char, delay=random.randint(30, 100))
                    
                    time.sleep(random.uniform(0.8, 1.5))

                    # Try to find suggestions
                    suggestion = page.locator("ul#address-suggestion-list li[role='option'], div.autocomplete-item").first
                    if suggestion.is_visible():
                        suggestion.click()
                        time.sleep(random.uniform(0.8, 1.5))
                    else:
                        print(f"Worker {worker_id}: No suggestions found for {location}, pressing Enter")
                        address_input.press("Enter")
                        time.sleep(random.uniform(1.0, 2.0))
                    
                    # Try multiple approaches to find and click the save button
                    save_found = False
                    
                    # Updated save button selectors
                    save_button_selectors = [
                        "button.e-129sec0:has(span:text('Save Address'))",
                        "button.e-129sec0", 
                        "button.e-y9ioae", 
                        "button:has-text('Save Address')",
                        "button:has-text('Save')",
                        "button[type='submit']"
                    ]
                    
                    for selector in save_button_selectors:
                        save_button = page.locator(selector).first
                        if save_button.count() > 0 and save_button.is_visible(timeout=1000):
                            save_button.click()
                            save_found = True
                            print(f"Worker {worker_id}: Clicked save button with selector: {selector}")
                            break
                    
                    # Approach for any visible button with save-like text
                    if not save_found:
                        buttons = page.locator("button").all()
                        for button in buttons:
                            try:
                                if button.is_visible():
                                    button_text = button.inner_text()
                                    if any(keyword in button_text.lower() for keyword in ["save", "done", "confirm", "submit", "address"]):
                                        button.click()
                                        save_found = True
                                        print(f"Worker {worker_id}: Clicked button with text: {button_text}")
                                        break
                            except:
                                continue
                    
                    # Wait longer for page to update with new location
                    time.sleep(random.uniform(1.5, 3.0))
                else:
                    print(f"Worker {worker_id}: Could not find address input field")
                    browser.close()
                    return
            except Exception as e:
                print(f"Worker {worker_id}: Error changing location: {str(e)}")
                browser.close()
                return

            # Scrape URLs with added delays between categories
            all_data = []
            for url_index, url_info in enumerate(urls):
                url = url_info["url"]
                category = url_info["category"]
                
                # Skip categories that aren't in our target list
                if category not in TARGET_PRODUCTS:
                    continue
                
                try:
                    print(f"Worker {worker_id}: Processing category {category} ({url_index+1}/{len(urls)})")
                    
                    # Wait longer between categories
                    if url_index > 0:
                        delay = random.uniform(2.0, 4.0)
                        print(f"Worker {worker_id}: Waiting {delay:.1f}s before next category...")
                        time.sleep(delay)
                    
                    # Use retry navigation
                    if not navigate_with_retry(page, url):
                        continue
                    
                    # Check for confirm button again after navigation
                    try:
                        continue_button = page.get_by_role("button", name="Confirm")
                        if continue_button.is_visible():
                            continue_button.click()
                            time.sleep(random.uniform(0.8, 1.5))
                    except:
                        pass

                    store_id = generate_store_id(location)
                    
                    deli_data = scrape_deli_items(page, location, category, store_id)
                    all_data.extend(deli_data)
                    
                    # Report progress
                    print(f"Worker {worker_id}: Found {len(deli_data)} products for {category} in {location}")
                    
                except Exception as e:
                    print(f"Worker {worker_id}: Error processing category {category}: {str(e)}")
                    continue
            
            # Save data for this location
            if all_data:
                append_to_csv(output_file, all_data, lock)
                print(f"Worker {worker_id}: Added {len(all_data)} products for {location}")
            else:
                print(f"Worker {worker_id}: No target products found for {location}")
            
            browser.close()
            print(f"Worker {worker_id}: Completed processing location: {location}")
    
    except Exception as e:
        print(f"Worker {worker_id}: Fatal error: {str(e)}")
        print(traceback.format_exc())

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape Publix product data')
    parser.add_argument('--input_file', type=str, default='publix_locations.csv', help='Input CSV with locations')
    parser.add_argument('--output_file', type=str, default=f'publix_targeted_data_{datetime.now().strftime("%Y%m%d")}.csv', help='Output CSV file')
    parser.add_argument('--workers', type=int, default=5, help='Number of worker processes (0=auto)')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode (slower, more verbose)')
    parser.add_argument('--headless', type=lambda x: (str(x).lower() in ['true', '1']), default=True, help='Run in headless mode')
    args = parser.parse_args()
    
    # Use headless mode unless in debug mode
    headless = args.headless if not args.debug else False
    
    # Read locations from CSV
    locations = []
    try:
        with open(args.input_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                locations.append(row['location'])
        print(f"Total locations to process: {len(locations)}")
    except Exception as e:
        print(f"Error reading {args.input_file}: {e}")
        return
    urls = [
        {"url": "https://delivery.publix.com/store/publix/collections/n-beef-17864", "category": "Beef"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-bread-15280", "category": "Bread"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-butter-51263", "category": "Butter"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-canned-beans-78884", "category": "Canned Beans"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-cereal-20111", "category": "Cereal"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-chicken-59213", "category": "Chicken"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-chips-55178", "category": "Chips"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-coffee-36369", "category": "Coffee"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-cooking-oils-4131", "category": "Cooking Oils"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-deli-meats-63527", "category": "Deli Meats"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-eggs-83685", "category": "Eggs"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-fresh-fruits-91006", "category": "Fresh Fruits"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-fresh-vegetables-3995", "category": "Fresh Vegetables"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-jams-jellies-32363", "category": "Jams Jellies"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-juice-50886", "category": "Juice"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-lager-72005", "category": "Lager"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-light-beer-20466", "category": "Light Beer"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-milk-22980", "category": "Milk"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-pasta-49998", "category": "Pasta"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-red-wine-5727", "category": "Red Wine"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-spices-seasoning-33818", "category": "Spices Seasoning"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-white-wine-76269", "category": "White Wine"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-cheese-10478", "category": "Cheese"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-baby-food-drinks-22413", "category": "Baby Food Drinks"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-paper-goods-28545", "category": "Paper Goods"},
        {"url": "https://delivery.publix.com/store/publix/collections/n-trash-bins-bags-84758", "category": "Trash Bins Bags"}
    ]

    # Set up output file with updated headers
    output_file = args.output_file
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Store ID', 'Location', 'Category', 'Product Name', 'Price', 'Size', 'Date'])

    # Create a lock for file access
    manager = multiprocessing.Manager()
    lock = manager.Lock()

    # Determine number of processes
    if args.workers > 0:
        num_processes = args.workers
    else:
        # Use more workers by default
        num_processes = min(multiprocessing.cpu_count() * 2, len(locations))
    
    print(f"Using {num_processes} worker processes to search for targeted products")
    
    # Create a pool of workers
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Create tasks with location and worker_id
        tasks = []
        for i, location in enumerate(locations):
            tasks.append(((location, i+1), urls, output_file, lock, headless))
        
        # Execute tasks in parallel
        pool.starmap(process_location, tasks)

if __name__ == "__main__":
    main()
