# Amazon Scraper

Welcome to the Amazon Scraper project! 🚀 This handy tool is designed to help you gather product information from Amazon with ease. Whether you're a data enthusiast, a developer, or just curious, this scraper is here to assist you.

## Prerequisites

- Python 3.x
- [GeckoDriver](https://github.com/mozilla/geckodriver/releases) (for Firefox)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure GeckoDriver is installed and the path is set correctly in `scrape.py`.

## Ways to Scrape

This script offers flexible scraping options:

1. **Search by Term**: Enter a search term, and the scraper will navigate through Amazon's search results, gathering data from multiple pages.

2. **Specific URLs**: Have specific product URLs in mind? Just input them, and the scraper will fetch the details for you.

3. **Proxy Support**: If you have proxies, you can input them to help manage requests and avoid detection.

## Usage

Run the script:
```bash
python scrape.py
```

Follow the prompts to enter search terms, page numbers, specific links, and proxy information.

## Output

The scraped data will be saved to `amazon_data.csv`. 🎉

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Happy scraping! 😊 