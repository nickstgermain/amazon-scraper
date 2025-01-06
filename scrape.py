from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import pandas as pd
import time
import random
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup Firefox options
firefox_options = Options()
firefox_options.add_argument('--headless')  # Run in headless mode

# Path to your GeckoDriver
webdriver_service = Service('/Users/nickstgermain/Desktop/geckodriver')  # Update this path

# Initialize the WebDriver
browser = webdriver.Firefox(service=webdriver_service, options=firefox_options)

def get_product_info_selenium(url):
    print(f"Accessing product page: {url}")
    browser.get(url)
    time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior

    try:
        title = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#productTitle"))
        ).text.strip()
        print(f"Product title: {title}")
    except Exception as e:
        print(f"Failed to get title: {e}")
        title = None

    try:
        # Try multiple selectors to find the price
        price = None
        price_whole = browser.find_element(By.CSS_SELECTOR, 'span.a-price-whole').text.strip()
        price_fraction = browser.find_element(By.CSS_SELECTOR, 'span.a-price-fraction').text.strip()
        price = f"{price_whole}.{price_fraction}"
    except Exception as e:
        print(f"Failed to get price: {e}")
        price = None

    try:
        rating = browser.find_element(By.ID, "acrPopover").get_attribute("title").replace("out of 5 stars", "")
    except Exception as e:
        print(f"Failed to get rating: {e}")
        rating = None

    try:
        image = browser.find_element(By.ID, "landingImage").get_attribute("src")
    except Exception as e:
        print(f"Failed to get image: {e}")
        image = None

    try:
        description = browser.find_element(By.ID, "productDescription").text.strip()
    except Exception as e:
        print(f"Failed to get description: {e}")
        description = None

    product_info = {
        "title": title,
        "price": price,
        "rating": rating,
        "image": image,
        "description": description,
        "url": url
    }
    print(f"Scraped product info: {product_info}")
    return product_info

def fetch_product_info(link):
    try:
        return get_product_info_selenium(link)
    except Exception as e:
        print(f"Error fetching product info: {e}")
        return None

def parse_listing_selenium(listing_url, pages):
    data = []
    base_url = 'https://www.amazon.com'
    browser.get(listing_url)
    time.sleep(random.uniform(2, 5))  # Random delay

    for page_number in range(1, pages + 1):
        print(f"Scraping page {page_number} of {pages}.")  # Log current page
        print(f"Current URL: {browser.current_url}")  # Log current URL to verify pagination
        try:
            # Wait for a specific element to ensure the page is fully loaded
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.s-main-slot div[data-asin]'))
            )

            # Scroll to the bottom of the page
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Short delay to allow elements to render

            products = browser.find_elements(By.CSS_SELECTOR, 'div.s-main-slot div[data-asin]')
            links = []
            for product in products:
                retry_count = 0
                max_retries = 5  # Increase the number of retries
                while retry_count < max_retries:  # Retry mechanism for stale elements
                    try:
                        link = product.find_element(By.CSS_SELECTOR, 'a.a-link-normal.s-no-outline').get_attribute('href')
                        links.append(link)
                        break  # Exit the retry loop if successful
                    except StaleElementReferenceException:
                        print(f"Stale element reference, re-locating product link. Attempt {retry_count + 1} of {max_retries}.")
                        retry_count += 1
                        time.sleep(1)  # Short delay before retrying
                        # Re-locate the product element
                        products = WebDriverWait(browser, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.s-main-slot div[data-asin]'))
                        )
                        product = products[products.index(product)]  # Re-locate the specific product element
                    except Exception as e:
                        print(f"Failed to get product link: {e}")
                        break

            # Fetch product info sequentially
            for link in links:
                product_info = fetch_product_info(link)
                if product_info:
                    data.append(product_info)
                    print(f"Processed {len(data)} products.")  # Log number of products processed
                time.sleep(random.uniform(1, 2))  # Add a delay after processing each product

            # Reload the listing page to ensure we are on the main products page
            browser.get(listing_url)
            time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior

            # Scroll to the bottom of the page to load all elements
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Short delay to allow elements to render

            # Re-locate the 'Next Page' button after processing products
            try:
                next_page = WebDriverWait(browser, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.s-pagination-item.s-pagination-next.s-pagination-button.s-pagination-button-accessibility.s-pagination-separator'))
                )
                print("Next Page button found, attempting to click.")  # Log when button is found
                next_page.click()
                time.sleep(3)  # Pause for 3 seconds before making the next request
            except NoSuchElementException:
                print("No more pages to navigate.")
                break
            except Exception as e:
                print(f"Failed to navigate to next page: {e}")
                break
        except Exception as e:
            print(f"Failed to load products: {e}")
            break

    return data

def configure_proxy(proxy):
    firefox_options = Options()
    firefox_options.add_argument('--headless')  # Run in headless mode

    proxy_host, proxy_port, proxy_user, proxy_pass = proxy.split(':')
    seleniumwire_options = {
        'proxy': {
            'http': f'http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
            'https': f'https://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }

    # Path to your GeckoDriver
    webdriver_service = Service('/Users/nickstgermain/Desktop/geckodriver')  # Update this path

    return webdriver.Firefox(service=webdriver_service, options=firefox_options, seleniumwire_options=seleniumwire_options)

def main():
    search = input("Enter the search term (leave blank if using specific URLs): ").strip()
    urls = []
    if not search:
        url_input = input("Enter specific URLs separated by commas: ").strip()
        urls = [url.strip() for url in url_input.split(',') if url.strip()]

    pages = int(input("Enter the number of pages to scrape: ").strip())

    # Predefined list of proxies
    proxies = []

    data = []
    for proxy in proxies:
        print(f"Using proxy: {proxy}")
        global browser
        browser = configure_proxy(proxy)
        try:
            if search:
                search_url = f"https://www.amazon.com/s?k={search}"
                data.extend(parse_listing_selenium(search_url, pages))
            elif urls:
                for url in urls:
                    data.extend(parse_listing_selenium(url, pages))
        except Exception as e:
            print(f"Error with proxy {proxy}: {e}")
        finally:
            browser.quit()

    df = pd.DataFrame(data)
    df.to_csv("amazon_data.csv", index=False, columns=["title", "price", "rating", "image", "description", "url"])
    print("Data saved to amazon_data.csv")

def get_product_title(url):
    print(f"Accessing product page: {url}")
    browser.get(url)
    time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior

    try:
        title = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#productTitle"))
        ).text.strip()
        print(f"Product title: {title}")
    except Exception as e:
        print(f"Failed to get title: {e}")
        title = None

    return title

if __name__ == '__main__':
    main()
    browser.quit()
