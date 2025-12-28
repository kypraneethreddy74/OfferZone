import time
import re
import pandas as pd
import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Sudheer@16159", 
    "database": "croma_db"
}

def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_croma():
    driver = get_driver()
    url = "https://www.croma.com/televisions-accessories/televisions/c/997"
    driver.get(url)
    wait = WebDriverWait(driver, 15)

    print("Loading all products...")
    while True:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            # Find the View More button
            view_more = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'View More')]")))
            driver.execute_script("arguments[0].click();", view_more)
            print("Clicked 'View More'...")
            time.sleep(3)
        except Exception:
            print("Reached the end of the list or button not found.")
            break

    # Final scroll to ensure all lazy-loaded elements (ratings/images) are triggered
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    data = []
    seen_urls = set()
    items = soup.find_all("li", class_="product-item")
    print(f"Parsing {len(items)} products...")

    for item in items:
        try:
            # 1. Product Name & Brand
            name_tag = item.find("h3")
            if not name_tag: continue
            name = name_tag.text.strip()
            
            # 2. Product URL
            link_tag = item.find("a")
            if not link_tag: continue
            p_url = "https://www.croma.com" + link_tag['href']
            
            if p_url in seen_urls: continue
            seen_urls.add(p_url)

            # 3. Rating Extraction (Improved)
            rating_val = 0.0
            # Croma usually uses 'cp-rating' or 'pdp-rating-count'
            rating_container = item.find("div", class_="cp-rating") or \
                               item.find("span", class_="pdp-rating-count") or \
                               item.find("span", class_="rating")

            if rating_container:
                rating_text = rating_container.text.strip()
                # Use regex to find number like 4.2 or 4
                match = re.search(r"(\d+\.\d+|\d+)", rating_text)
                if match:
                    rating_val = float(match.group(1))

            # 4. Prices
            s_tag = item.find("span", class_="amount")
            selling_price = int(''.join(filter(str.isdigit, s_tag.text))) if s_tag else None
            
            m_tag = item.find("span", class_="old-price")
            mrp_val = int(''.join(filter(str.isdigit, m_tag.text))) if m_tag else selling_price
            
            # 5. Image URL
            img_tag = item.find("img")
            img_url = img_tag.get('data-src') or img_tag.get('src') if img_tag else None

            data.append({
                "brand": name.split()[0],
                "model_name": name,
                "selling_price": selling_price,
                "mrp": mrp_val,
                "rating": rating_val,
                "image_url": img_url,
                "product_url": p_url
            })
        except Exception as e:
            print(f"Error parsing item: {e}")
            continue

    return pd.DataFrame(data)

def save_to_db(df):
    if df.empty:
        print("No data to save.")
        return

    df = df.where(pd.notnull(df), None)
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # SQL query including rating
    insert_sql = """
    INSERT INTO products (brand, model_name, selling_price, mrp, rating, image_url, product_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        selling_price = VALUES(selling_price),
        mrp = VALUES(mrp),
        rating = VALUES(rating),
        scraped_at = CURRENT_TIMESTAMP;
    """

    success_count = 0
    for _, row in df.iterrows():
        try:
            cursor.execute(insert_sql, (
                row["brand"], row["model_name"], row["selling_price"], 
                row["mrp"], row["rating"], row["image_url"], row["product_url"]
            ))
            success_count += 1
        except Exception as e:
            print(f"Database error: {e}")
    
    conn.commit()
    conn.close()
    print(f"Success: {success_count} records synced to MySQL.")

# --- RUN ---
df_final = scrape_croma()
df_final.to_csv("croma_tvs.csv", index=False, encoding='utf-8-sig')
save_to_db(df_final)