from bs4 import BeautifulSoup
import sqlite3
import re

# -------------------------------
# Read Amazon.html
# -------------------------------
with open("Amazon.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "lxml")

# -------------------------------
# Connect to SQLite Database
# -------------------------------
conn = sqlite3.connect("amazon_products.db")
cursor = conn.cursor()

# Drop old table if exists
cursor.execute("DROP TABLE IF EXISTS products")

# Create table
cursor.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT,
    product_name TEXT,
    product_price TEXT,
    product_reviews TEXT,
    inches TEXT,
    display_type TEXT,
    launch_year TEXT,
    image_url TEXT
)
""")
conn.commit()

# -------------------------------
# Find all product divs
# -------------------------------
product_divs = soup.find_all(
    "div",
    class_="puis-card-container s-card-container s-overflow-hidden aok-relative desktop-list-view puis-include-content-margin puis puis-v2j5rsb4gli0782rvtpm6mc0r70 s-latency-cf-section puis-card-border"
)

print("Total products found:", len(product_divs))

# -------------------------------
# Extract data and insert into DB
# -------------------------------
for div in product_divs:

    # Product Name
    try:
        Product_Name = div.find(
            "h2",
            class_="a-size-medium a-spacing-none a-color-base a-text-normal"
        ).get_text(strip=True)
    except:
        Product_Name = " "

    # Brand Name
    Brand_Name = Product_Name.split()[0] if Product_Name.strip() else " "

    # Product Price
    try:
        Product_Price = div.find("span", class_="a-price-whole").get_text(strip=True)
    except:
        Product_Price = " "

    # Product Reviews
    try:
        Product_Reviews = div.find(
            "span",
            class_="a-size-small a-color-base",
            attrs={"aria-hidden": "true"}
        ).get_text(strip=True)
    except:
        Product_Reviews = " "

    # Inches
    inch_match = re.search(r'(\d+\.?\d*)\s*(inch|")', Product_Name, re.IGNORECASE)
    Inches = inch_match.group(1) if inch_match else " "

    # Display Type (LED / QLED / OLED)
    display_match = re.search(r'\b(QLED|OLED|LED)\b', Product_Name, re.IGNORECASE)
    Display_Type = display_match.group(1).upper() if display_match else " "

    # Launch Year
    year_match = re.search(r'(20[1-2][0-9])', Product_Name)
    Launch_Year = year_match.group(1) if year_match else " "

    # Image URL
    try:
        Image_URL = div.find("img")["src"]
    except:
        Image_URL = " "

    # Insert into DB
    cursor.execute("""
        INSERT INTO products 
        (brand_name, product_name, product_price, product_reviews, inches, display_type, launch_year, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        Brand_Name,
        Product_Name,
        Product_Price,
        Product_Reviews,
        Inches,
        Display_Type,
        Launch_Year,
        Image_URL
    ))

conn.commit()

# -------------------------------
# Display row by row
# -------------------------------
cursor.execute("SELECT * FROM products")
rows = cursor.fetchall()

for row in rows:
    print("Brand_Name     :", row[1])
    print("Product_Name   :", row[2])
    print("Product_Price  :", row[3])
    print("Product_Reviews:", row[4])
    print("Inches         :", row[5])
    print("Display_Type   :", row[6])
    print("Launch_Year    :", row[7])
    print("Image_URL      :", row[8])
    print("-" * 60)

conn.close()
