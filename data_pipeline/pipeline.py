#Step 1 — Scrape 60+ books:

import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL="https://books.toscrape.com/"

books = []

categories=[
    ("Travel", "catalogue/category/books/travel_2/index.html"),
    ("Mystery", "catalogue/category/books/mystery_3/index.html"),
    ("Historical Fiction", "catalogue/category/books/historical-fiction_4/index.html")
]
for category_name,category_url in categories:
    url=BASE_URL+category_url

    while url:
        response=requests.get(url,timeout=10)
        response.raise_for_status()
        soup=BeautifulSoup(response.text,"html.parser")
        products=soup.select("article.product_pod")

        for product in products:
            title=product.h3.a["title"]
            price=product.select_one(".price_color").text
            availability=product.select_one(".availability").text.strip()
            star_class=product.select_one(".star-rating")["class"]
            star_rating=star_class[1]

            books.append({
                "title":title,
                "price":price,
                "star_rating":star_rating,
                "availability":availability,
                "category":category_name
            })

        next_button=soup.select_one("li.next a")

        if next_button:
            from urllib.parse import urljoin
            url=urljoin(url,next_button["href"])
        else:
            url=None

df=pd.DataFrame(books)

print(df.head())
print("Total books:",len(df))
print(df["category"].value_counts())
print(df.dtypes)

#Step 2 — Clean the data:

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

df["price_gbp"] = (
    df["price"]
    .str.replace("Â£", "", regex=False)
    .str.replace("£", "", regex=False)
    .str.replace("Â", "", regex=False)
    .astype(float)
)
df["rating"] = df["star_rating"].map(rating_map)

df["in_stock"] = (
    df["availability"]
    .str.contains("In stock", case=False, na=False)
)

print(df[[
    "title",
    "price_gbp",
    "rating",
    "in_stock",
    "category"
]].head())

#Step 3 — GBP → INR:

GBP_TO_INR = 105.50

df["price_inr"] = df["price_gbp"] * GBP_TO_INR

df["price_inr"] = df["price_inr"].round(2)

#Step 4 — SQLite database:

import sqlite3
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS categories(
category_id INTEGER PRIMARY KEY AUTOINCREMENT,
category_name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
book_id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
  price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock INTEGER,
    category_id INTEGER,
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
)
""")

conn.commit()

for category in df["category"].unique():

    cursor.execute(
        "INSERT OR IGNORE INTO categories (category_name) VALUES(?)",(category,)
    
    )

conn.commit()

for _, row in df.iterrows():

    cursor.execute(
        "SELECT category_id FROM categories WHERE category_name = ?",
        (row["category"],)
    )

    category_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO books
        (title, price_gbp, price_inr, rating, in_stock, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row["title"],
        row["price_gbp"],
        row["price_inr"],
        int(row["rating"]),
        int(row["in_stock"]),
        category_id
    ))

conn.commit()

#Step 5 — 5 SQL Queries:

output_file = open("query_outputs.txt", "w", encoding="utf-8")

def save_query(title, query):
    output_file.write("=" * 60 + "\n")
    output_file.write(title + "\n")
    output_file.write("=" * 60 + "\n\n")
    output_file.write(query.strip() + "\n\n")

    result = pd.read_sql(query, conn)

    output_file.write(result.to_string(index=False))
    output_file.write("\n\n")

    print(f"\n{title}")
    print(result)

    return result

# Query 1
q1 = """
SELECT title, price_inr
FROM books
WHERE rating = 5;
"""
save_query("QUERY 1 - WHERE", q1)

# Query 2
q2 = """
SELECT title, price_inr
FROM books
ORDER BY price_inr DESC
LIMIT 10;
"""
save_query("QUERY 2 - ORDER BY + LIMIT", q2)

# Query 3
q3 = """
SELECT DISTINCT rating
FROM books
ORDER BY rating;
"""
save_query("QUERY 3 - DISTINCT", q3)

# Query 4
q4 = """
SELECT title, price_gbp
FROM books
WHERE price_gbp BETWEEN 20 AND 40;
"""
save_query("QUERY 4 - BETWEEN", q4)

# Query 5
q5 = """
SELECT
    b.title,
    b.rating,
    b.price_inr,
    c.category_name
FROM books b
JOIN categories c
ON b.category_id = c.category_id
ORDER BY b.rating DESC;
"""
join_sql = save_query("QUERY 5 - JOIN", q5)

output_file.close()

#Step 6 — pd.read_sql() vs pd.merge():

books_df = pd.read_sql(
    "SELECT * FROM books",
    conn
)

categories_df = pd.read_sql(
    "SELECT * FROM categories",
    conn
)

merged_df = pd.merge(
    books_df,
    categories_df,
    on="category_id"
)

sql_join = pd.read_sql("""
SELECT
    b.*,
    c.category_name
FROM books b
JOIN categories c
ON b.category_id = c.category_id
""", conn)

print(sql_join.head())
print(merged_df.head())