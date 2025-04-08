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
    ounces = ozs_div.inner_text() if ozs_div.count() > 0 else "Not found"

    return {
        "Location": location,
        "Product Name": product_name,
        "Price": f"${price}" if not price.startswith("$") else price,
        "Ounces": ounces
    }

def scroll_to_load_all_items(page):
    last_height = page.evaluate("document.body.scrollHeight")
    max_scroll_attempts = 10
    scroll_attempts = 0
    
    while scroll_attempts < max_scroll_attempts:
        # Scroll down to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait to load more content
        page.wait_for_timeout(2000)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            # Try one more time to ensure everything is loaded
            page.wait_for_timeout(1000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            page.wait_for_timeout(1000)
            final_height = page.evaluate("document.body.scrollHeight")
            if final_height == new_height:
                break
        
        last_height = new_height
        scroll_attempts += 1
        
    # Check for "Show More" or "Load More" buttons
    try:
        load_more = page.locator("button:has-text('Load More')").first
        if load_more.count() > 0 and load_more.is_visible():
            load_more.click()
            page.wait_for_timeout(2000)
            # Recursive call to continue scrolling after loading more
            scroll_to_load_all_items(page)
    except Exception as e:
        pass 

def navigate_with_retry(page, url, max_retries=3):
    """Navigate to URL with retry logic"""
    for attempt in range(max_retries):
        try:
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(3000) 
            
            # Check if page loaded correctly
            if page.url.startswith(url.split("?")[0]):  
                return True
            else:
                pass
        except Exception as e:
            pass
        
        time.sleep(random.uniform(2, 5))  # Random delay between retries
    
    print(f"Failed to navigate to {url} after {max_retries} attempts")
    return False

def scrape_deli_items(page, location, category):
    """Enhanced scraping function with better product detection"""
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        page.screenshot(path=f"no_products_{location.replace(', ', '_')}_{timestamp}.png")
        return []

    deli_data = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Take a screenshot of the page with products
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    page.screenshot(path=f"products_page_{location.replace(', ', '_')}_{timestamp}.png")
    
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
                
                # Try to find ounces information
                ozs_element = item.locator('div.e-an4oxa, .product-size').first
                ounces = ozs_element.inner_text() if ozs_element.count() > 0 else "Not found"
                
                row = [
                    location,
                    category,
                    product_name,
                    price,
                    ounces,
                    current_date
                ]
            else:
                # Use original extraction logic
                item_details = extract_item_details(item, location)
                row = [
                    item_details["Location"],
                    category,
                    item_details["Product Name"],
                    item_details["Price"],
                    item_details["Ounces"],
                    current_date
                ]
            
            deli_data.append(row)
        except Exception as e:
            print(f"Error extracting item {i}: {e}")
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

def process_location(location_data, urls, output_file, lock, headless=False):
    """Process a single location in its own process"""
    location, worker_id = location_data
    
    try:
        
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=headless)
            context = browser.new_context(
                permissions=["geolocation"],
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()
            
            # Start at storefront with retry logic
            if not navigate_with_retry(page, "https://delivery.publix.com/store/publix/storefront"):
                browser.close()
                return

            # Handle Confirm button
            try:
                continue_button = page.get_by_role("button", name="Confirm")
                if continue_button.is_visible():
                    continue_button.click()

                else:
                    pass
            except Exception as e:
                print(f"Error with Confirm button for {location}: {e}")

            # Change location
            try:
                # Try multiple selectors for the location button
                location_button_selectors = ["button.e-1v873ap", "button.e-4jnww6"]
                zip_button = None
                
                for selector in location_button_selectors:
                    zip_button = page.locator(selector).first
                    if zip_button.count() > 0 and zip_button.is_visible(timeout=1000):
                        zip_button.click()
                        break
                
                if not zip_button or zip_button.count() == 0:
                    timestamp = datetime.now().strftime("%Y%m%d")
                    page.screenshot(path=f"zip_button_error_{location.replace(', ', '_')}_{timestamp}.png")
                    browser.close()
                    return

                address_input = page.locator("input#streetAddress").first
                
                if address_input.count() > 0:
                    address_input.click()
                    address_input.fill("")
                    time.sleep(0.5)
                    address_input.fill(location)
                    page.wait_for_timeout(2000)  

                    # Try to find suggestions
                    suggestion = page.locator("ul#address-suggestion-list li[role='option']").first
                    if suggestion.is_visible():
                        suggestion.click()
                        page.wait_for_timeout(2000)
                    else:
                        print(f"Worker {worker_id}: No suggestions found for {location}, pressing Enter")
                        address_input.press("Enter")
                        page.wait_for_timeout(2000)

                    # Take a screenshot to see what the page looks like at this point
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    page.screenshot(path=f"before_save_{location.replace(', ', '_')}_{timestamp}.png")
                    
                    # Try multiple approaches to find and click the save button
                    save_found = False
                    
                    # Approach 1: Try the exact selector from the HTML you provided
                    save_button = page.locator("button.e-129sec0:has(span:text('Save Address'))").first
                    if save_button.count() > 0 and save_button.is_visible(timeout=2000):
                        save_button.click()
                        save_found = True
                    
                    # Approach 2: Try specific selectors
                    if not save_found:
                        save_button_selectors = [
                            "button.e-129sec0", 
                            "button.e-y9ioae", 
                            "button:has-text('Save Address')",
                            "button[type='submit']"
                        ]
                        
                        for selector in save_button_selectors:
                            save_button = page.locator(selector).first
                            if save_button.count() > 0 and save_button.is_visible(timeout=1000):
                                save_button.click()
                                save_found = True
                                break
                    
                    # Approach 3: If no specific selector worked, try to find any visible button
                    if not save_found:
                        buttons = page.locator("button").all()
                        for button in buttons:
                            try:
                                if button.is_visible():
                                    button_text = button.inner_text()
                                    if any(keyword in button_text.lower() for keyword in ["save", "done", "confirm", "submit", "address"]):
                                        button.click()
                                        save_found = True
                                        break
                            except:
                                continue
                    
                    # Wait for page to update with new location
                    page.wait_for_timeout(5000)
                    
                    # Take another screenshot after attempting to save
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    page.screenshot(path=f"after_save_{location.replace(', ', '_')}_{timestamp}.png")

                    # Verify location - try multiple selectors
                    location_display_selectors = ["div.e-nhyndx", "div.e-h0ixs2", "button:has-text('Change')"]
                    location_verified = False
                    
                    for selector in location_display_selectors:
                        location_display = page.locator(selector).first
                        if location_display.count() > 0:
                            displayed = location_display.inner_text()
                            # Check if any part of the location is in the displayed text
                            location_parts = [part.strip().lower() for part in location.split(',')]
                            if any(part in displayed.lower() for part in location_parts):
                                location_verified = True
                                break
                    
                    if not location_verified:
                        timestamp = datetime.now().strftime("%Y%m%d")
                        page.screenshot(path=f"location_verify_error_{location.replace(', ', '_')}_{timestamp}.png")
                        # Continue anyway as the location might still be set correctly
                else:
                    timestamp = datetime.now().strftime("%Y%m%d")
                    page.screenshot(path=f"address_input_error_{location.replace(', ', '_')}_{timestamp}.png")
                    browser.close()
                    return
            except Exception as e:
                timestamp = datetime.now().strftime("%Y%m%d")
                page.screenshot(path=f"location_error_{location.replace(', ', '_')}_{timestamp}.png")
                browser.close()
                return

            # Scrape URLs
            all_data = []
            for url_idx, url_info in enumerate(urls, 1):
                url = url_info["url"]
                category = url_info["category"]
                
                try:
                    # Use retry navigation
                    if not navigate_with_retry(page, url):
                        continue
                    
                    # Add random delay to avoid detection
                    time.sleep(random.uniform(1, 3))
                    
                    # Check for confirm button again after navigation
                    try:
                        continue_button = page.get_by_role("button", name="Confirm")
                        if continue_button.is_visible(timeout=1000):
                            continue_button.click()
                            page.wait_for_timeout(1000)
                    except:
                        pass
                    
                    deli_data = scrape_deli_items(page, location, category)
                    all_data.extend(deli_data)
                except Exception as e:
                    timestamp = datetime.now().strftime("%Y%m%d")
                    page.screenshot(path=f"scrape_error_{location.replace(', ', '_')}_{url_idx}_{timestamp}.png")
                    continue
            
            # Save data for this location
            if all_data:
                append_to_csv(output_file, all_data, lock)
            else:
                print(f"Worker {worker_id}: No data collected for {location}")
            
            browser.close()
            print(f"Worker {worker_id}: Completed processing location: {location}")
    
    except Exception as e:
        print(traceback.format_exc())

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape Publix product data')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode (slower, more verbose)')
    args = parser.parse_args()
    
    # Use headless mode unless in debug mode
    headless = not args.debug
    
    # Read locations from CSV
    locations = []
    try:
        with open('publix_locations.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                locations.append(row['location'])
        print(f"Total locations to process: {len(locations)}")
    except Exception as e:
        print(f"Error reading publix_locations.csv: {e}")
        return

    # Hardcoded URLs with categories
    urls = [
    {"url": "https://delivery.publix.com/store/publix/collections/n-deli-meats-63527", "category": "Deli Meats"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-cheese-10478", "category": "Cheese"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-diapers-wipes-91418", "category": "Diapers Wipes"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-bottles-formula-45612", "category": "Bottles Formula"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-baby-food-drinks-22413", "category": "Baby Food Drinks"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-bread-15280", "category": "Bread"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-buns-rolls-36403", "category": "Buns Rolls"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-milk-22980", "category": "Milk"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-eggs-83685", "category": "Eggs"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-yogurt-92685", "category": "Yogurt"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-butter-51263", "category": "Butter"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-cereal-20111", "category": "Cereal"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-nut-butters-79822", "category": "Nut Butters"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-jams-jellies-32363", "category": "Jams Jellies"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-coffee-36369", "category": "Coffee"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-juice-50886", "category": "Juice"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-fresh-fruits-91006", "category": "Fresh Fruits"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-fresh-vegetables-3995", "category": "Fresh Vegetables"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-chicken-55925", "category": "Chicken"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-beef-17864", "category": "Beef"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-pork-41487", "category": "Pork"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-frozen-vegetables-13294", "category": "Frozen Vegetables"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-trash-bins-bags-84758", "category": "Trash Bins Bags"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-laundry-28031", "category": "Laundry"},
    {"url": "https://delivery.publix.com/store/publix/collections/rc-2025-spring-cleaning-wk1-dish-detergent", "category": "Dish Detergent"},
    {"url": "https://delivery.publix.com/store/publix/collections/rc-2025-spring-cleaning-wk1-paper-products", "category": "Paper Products"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-paper-goods-28545", "category": "Paper Goods"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-pasta-49998", "category": "Pasta"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-pasta-sauces-3560", "category": "Pasta Sauces"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-pasta-pizza-sauces-7430", "category": "Pasta Pizza Sauces"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-canned-tomatoes-23535", "category": "Canned Tomatoes"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-canned-tomato-93239", "category": "Canned Tomato"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-canned-beans-78884", "category": "Canned Beans"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-beans-35261", "category": "Beans"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-cooking-oils-4131", "category": "Cooking Oils"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-spices-seasoning-33818", "category": "Spices Seasoning"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-salt-pepper-98471", "category": "Salt Pepper"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-hair-care-55174", "category": "Hair Care"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-oral-hygiene-53356", "category": "Oral Hygiene"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-canned-fruits-40845", "category": "Canned Fruits"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-red-wine-5727", "category": "Red Wine"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-white-wine-76269", "category": "White Wine"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-light-beer-20466", "category": "Light Beer"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-lager-72005", "category": "Lager"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-ale-28670", "category": "Ale"},
    {"url": "https://delivery.publix.com/store/publix/collections/n-chips-55178", "category": "Chips"}
    ]

    # Set up output file
    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = f"publix_data_{timestamp}.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Location', 'Category', 'Product Name', 'Price', 'Ounces', 'Date'])

    # Create a lock for file access
    manager = multiprocessing.Manager()
    lock = manager.Lock()

    # Limit the number of processes
    num_processes = min(multiprocessing.cpu_count(), 105) 
    # Create a pool of workers
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Create tasks with location and worker_id
        tasks = []
        for i, location in enumerate(locations):
            tasks.append(((location, i+1), urls, output_file, lock, headless))
        
        # Execute tasks in parallel
        pool.starmap(process_location, tasks)

if __name__ == "__main__":
    # Set start method for multiprocessing
    multiprocessing.freeze_support()  # For Windows compatibility
    main()
