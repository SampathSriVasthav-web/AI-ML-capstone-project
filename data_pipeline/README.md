# Data Pipeline Assignment

# Data Source

Books to Scrape:
https://books.toscrape.com/

# Pipeline

The project performs:

1.Web scraping using requests and BeautifulSoup
2.Data cleaning using pandas
3.GBP to INR conversion
4.SQLite database storage
5.SQL querying
6.SQL JOIN verification using pandas merge

# Currency Conversion

The project-defined fixed conversion rate is:

1 GBP = 105.50 INR

No external currency API is required.

# Data Cleaning

1.Removed £ symbol from prices.
2.Converted prices to float.
3.Converted star ratings from text to integers 1–5.
4.Converted availability into boolean `in_stock`.

# Run

Install dependencies:

pip install requests beautifulsoup4 pandas

Run:

python pipeline.py


# Verification


Project verified and final SQL queries completed.