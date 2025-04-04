# This is an auto-generated script for Lake Wales Publix locations
# Generated on: 2025-04-04 13:56:46

from playwright.sync_api import sync_playwright, Playwright
import csv
import time
from datetime import datetime

def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(permissions=["geolocation"])
    page = context.new_page()
    
    # Read locations
    locations = []
    with open('publix_LakeWales.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            locations.append(row['location'])

    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = f"publix_deli_test_{timestamp}.csv"
    
    # Initialize CSV with headers once
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Location', 'Category', 'Product Name', 'Price', 'Ounces', 'Date'])

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
    
    for location in locations:
        deli_data = []
        
        # Set location once per location
        try:
            page.goto(urls[0]["url"], wait_until="domcontentloaded")  # Go to first URL to set location
            if not set_location(page, location):
                print(f"Failed to set location {location}")
                continue

            # Scrape all URLs for this location
            for url_info in urls:
                url = url_info["url"]
                category = url_info["category"]
                
                try:
                    page.goto(url, wait_until="domcontentloaded")
                    page.wait_for_load_state("domcontentloaded")  # Wait only for initial HTML
                    scroll_to_load_all_items(page)
                    deli_data.extend(scrape_deli_items(page, location, category))
                except Exception as e:
                    print(f"Error processing {url} for {location}: {str(e)}")
                    continue
                    
            # Write data to CSV after processing each location
            append_to_csv(output_file, deli_data)
                    
        except Exception as e:
            print(f"Error processing location {location}: {str(e)}")
            continue

    browser.close()

def set_location(page, location):
    try:
        continue_button = page.get_by_role("button", name="Confirm")
        if continue_button.is_visible(timeout=3000):
            continue_button.click()

        zip_button = page.locator("button.e-4jnww6").first
        if zip_button.is_visible():
            zip_button.click()

        address_input = page.locator("input#streetAddress")
        if address_input.count() > 0:
            address_input.click()
            address_input.fill(location)

            page.wait_for_selector("ul#address-suggestion-list li[role='option']")
            loc_list = page.locator("ul#address-suggestion-list")
            first_loc = loc_list.locator("li[role='option']").first
            first_loc.click()

            save_button = page.locator("button.e-y9ioae")
            if save_button.is_visible():
                save_button.click()
                page.wait_for_timeout(2000)  # Wait for location to be applied
            return True
        return False
    except Exception as e:
        print(f"Location setting error: {str(e)}")
        return False

def scroll_to_load_all_items(page):
    prev_height = page.evaluate("document.body.scrollHeight")
    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  # Reduced from 2 seconds to 1 second
        curr_height = page.evaluate("document.body.scrollHeight")
        if curr_height == prev_height:
            break
        prev_height = curr_height

def extract_item_details(deli_item, location):
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

def scrape_deli_items(page, location, category):
    current_date = datetime.now().strftime("%Y-%m-%d")
    deli_data = []

    deli = page.locator('h3.e-ti75j2')
    deli_count = deli.count()

    if deli_count > 0:
        for i in range(deli_count):
            try:
                deli_item = deli.nth(i)
                item_details = extract_item_details(deli_item, location)
                item_details["Category"] = category
                item_details["Date"] = current_date
                row = [item_details[k] for k in ['Location', 'Category', 'Product Name', 'Price', 'Ounces', 'Date']]
                deli_data.append(row)
            except Exception as e:
                print(f"Error scraping item {i}: {str(e)}")
                continue
    else:
        alt_products = page.locator('div.e-17gn4qg')
        alt_count = alt_products.count()
        if alt_count > 0:
            for i in range(alt_count):
                try:
                    deli_item = alt_products.nth(i)
                    item_details = extract_item_details(deli_item, location)
                    item_details["Category"] = category
                    item_details["Date"] = current_date
                    row = [item_details[k] for k in ['Location', 'Category', 'Product Name', 'Price', 'Ounces', 'Date']]
                    deli_data.append(row)
                except Exception as e:
                    print(f"Error scraping alt item {i}: {str(e)}")
                    continue

    return deli_data

def append_to_csv(filename, data):
    if not data:
        return
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)