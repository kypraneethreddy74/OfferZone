import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import pymysql


# ---------------- CONFIG ----------------
BASE_URL = "https://www.flipkart.com/search"
QUERY = "television"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.flipkart.com/"
}
# ---------------------------------------


def get_soup(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    return BeautifulSoup(response.text, "html.parser")


def clean_price(price_text):
    digits = re.sub(r"[^\d]", "", price_text)
    return int(digits) if digits else None


def extract_inches(text):
    match = re.search(r'(\d{2})\s*(inch|")', text.lower())
    return match.group(1) if match else "N/A"


def extract_panel_type(text):
    text = text.lower()
    if "qled" in text:
        return "QLED"
    elif "oled" in text:
        return "OLED"
    elif "mini led" in text or "miniled" in text:
        return "Mini LED"
    elif "led" in text:
        return "LED"
    return "Unknown"


def extract_os(text):
    text = text.lower()
    if "google tv" in text:
        return "Google TV"
    elif "android" in text:
        return "Android TV"
    elif "webos" in text:
        return "WebOS"
    elif "tizen" in text:
        return "Tizen"
    elif "vidaa" in text:
        return "VIDAA"
    return "Other"


def scrape_one_page(soup, data):
    grid = soup.find("div", class_="QSCKDh dLgFEE")
    if not grid:
        return 0

    names = grid.find_all("div", class_="RG5Slk")
    prices = grid.find_all("div", class_="hZ3P6w DeU9vF")
    ratings = grid.find_all("div", class_="MKiFS6")

    total_items = max(len(names), len(prices), len(ratings))
    count = 0

    for i in range(total_items):

        if i < len(names):
            full_name = names[i].text.strip()

            if full_name:
                parts = full_name.split()
                brand = parts[0]
                model = full_name.replace(brand, "").strip()

                inches = extract_inches(full_name)
                panel_type = extract_panel_type(full_name)
                operating_system = extract_os(full_name)
                smart_tv = "Yes" if "smart" in full_name.lower() else "No"

                year_match = re.search(r'(20[1-2][0-9])', full_name)
                launch_year = year_match.group(1) if year_match else "N/A"
            else:
                brand = model = inches = panel_type = operating_system = smart_tv = launch_year = "N/A"
        else:
            brand = model = inches = panel_type = operating_system = smart_tv = launch_year = "N/A"

        price = clean_price(prices[i].text) if i < len(prices) else None
        rating = ratings[i].text.strip() if i < len(ratings) else "0"

        data.append({
            "brand": brand,
            "model": model,
            "inches": inches,
            "panel_type": panel_type,
            "smart_tv": smart_tv,
            "operating_system": operating_system,
            "launch_year": launch_year,
            "price": price,
            "rating": rating
        })

        count += 1

    return count


def scrape_flipkart_tvs():
    data = []
    page = 1

    while True:
        print(f"Scraping page {page}")
        url = f"{BASE_URL}?q={QUERY}&page={page}"
        soup = get_soup(url)

        count = scrape_one_page(soup, data)
        if count == 0:
            break

        page += 1
        time.sleep(1.5)

    return pd.DataFrame(data)


# ---------------- RUN ----------------
df = scrape_flipkart_tvs()

df.drop_duplicates(subset=["brand", "model", "price"], inplace=True)

print(df.head())
print("Total TVs scraped:", len(df))

# MySQL connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="Sudheer@16159",
    database="flipkart_ref"
)

cursor = conn.cursor()

insert_query = """
INSERT IGNORE INTO flipkart_televisions
(brand, model, inches, panel_type, smart_tv,
 operating_system, launch_year, price, rating)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

for _, row in df.iterrows():
    cursor.execute(insert_query, (
        row["brand"],
        row["model"],
        row["inches"] if row["inches"] != "N/A" else None,
        row["panel_type"],
        row["smart_tv"],
        row["operating_system"],
        row["launch_year"] if row["launch_year"] != "N/A" else None,
        row["price"],
        row["rating"]
    ))

conn.commit()
conn.close()

print("Data inserted successfully into MySQL")