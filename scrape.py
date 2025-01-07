from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import pandas as pd
import time
import random

# Initialize the WebDriver
firefox_options = Options()
firefox_options.add_argument('--headless')  # Run in headless mode
webdriver_service = Service('/Users/nickstgermain/Desktop/geckodriver')
browser = webdriver.Firefox(service=webdriver_service, options=firefox_options)

def get_product_info_selenium(url):
    # Access the product page
    print(f"Accessing product page: {url}")
    browser.get(url)
    time.sleep(random.uniform(2, 5))

    # Extract product details
    try:
        title = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#productTitle"))
        ).text.strip()
        print(f"Product title: {title}")
    except Exception as e:
        print(f"Failed to get title: {e}")
        title = None

    try:
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

    # Return product information
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
    # Fetch product information from a given link
    try:
        return get_product_info_selenium(link)
    except Exception as e:
        print(f"Error fetching product info: {e}")
        return None

def parse_listing_selenium(listing_url, pages):
    data = []
    browser.get(listing_url)
    time.sleep(random.uniform(2, 5))

    for page_number in range(1, pages + 1):
        print(f"Scraping page {page_number} of {pages}.")
        print(f"Current URL: {browser.current_url}")
        try:
            # Wait for product elements to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.s-main-slot div[data-asin]'))
            )

            # Scroll to the bottom of the page
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Collect product links
            products = browser.find_elements(By.CSS_SELECTOR, 'div.s-main-slot div[data-asin]')
            links = []
            for product in products:
                retry_count = 0
                max_retries = 5
                while retry_count < max_retries:
                    try:
                        link = product.find_element(By.CSS_SELECTOR, 'a.a-link-normal.s-no-outline').get_attribute('href')
                        links.append(link)
                        break
                    except StaleElementReferenceException:
                        print(f"Stale element reference, re-locating product link. Attempt {retry_count + 1} of {max_retries}.")
                        retry_count += 1
                        time.sleep(1)
                        products = WebDriverWait(browser, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.s-main-slot div[data-asin]'))
                        )
                        product = products[products.index(product)]
                    except Exception as e:
                        print(f"Failed to get product link: {e}")
                        break

            # Fetch and process product information
            for link in links:
                product_info = fetch_product_info(link)
                if product_info:
                    data.append(product_info)
                    print(f"Processed {len(data)} products.")
                time.sleep(random.uniform(1, 2))

            # Reload the listing page
            browser.get(listing_url)
            time.sleep(random.uniform(2, 5))

            # Scroll to the bottom of the page again
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Navigate to the next page
            try:
                next_page = WebDriverWait(browser, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.s-pagination-item.s-pagination-next.s-pagination-button.s-pagination-button-accessibility.s-pagination-separator'))
                )
                print("Next Page button found, attempting to click.")
                next_page.click()
                time.sleep(3)
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

def configure_proxy(proxy=None):
    # Configure the WebDriver with or without a proxy
    firefox_options = Options()
    firefox_options.add_argument('--headless')

    seleniumwire_options = None
    if proxy:
        proxy_host, proxy_port, proxy_user, proxy_pass = proxy.split(':')
        seleniumwire_options = {
            'proxy': {
                'http': f'http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
                'https': f'https://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}'
            }
        }

    webdriver_service = Service('/Users/nickstgermain/Desktop/geckodriver')

    return webdriver.Firefox(service=webdriver_service, options=firefox_options, seleniumwire_options=seleniumwire_options)

def main():
    global browser
    # Get user input for search term or specific URLs
    search = input("Enter the search term (leave blank if using specific URLs): ").strip()
    urls = []
    if not search:
        url_input = input("Enter specific URLs separated by commas: ").strip()
        urls = [url.strip() for url in url_input.split(',') if url.strip()]

    pages = int(input("Enter the number of pages to scrape: ").strip())

    proxies = []  # List of proxies (empty for no proxy)

    data = []
    if not proxies:
        print("No proxies provided, running without proxy.")
        browser = configure_proxy()
        try:
            if search:
                search_url = f"https://www.amazon.com/s?k={search}"
                data.extend(parse_listing_selenium(search_url, pages))
            elif urls:
                for url in urls:
                    data.extend(parse_listing_selenium(url, pages))
        except Exception as e:
            print(f"Error without proxy: {e}")
        finally:
            browser.quit()
    else:
        for proxy in proxies:
            print(f"Using proxy: {proxy}")
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

    # Save the scraped data to a CSV file
    df = pd.DataFrame(data)
    df.to_csv("amazon_data.csv", index=False, columns=["title", "price", "rating", "image", "description", "url"])
    print("Data saved to amazon_data.csv")

if __name__ == '__main__':
    main()
    browser.quit()
