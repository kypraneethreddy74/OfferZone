import time
import re
import pymysql
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# ---------------- DB CONFIG ----------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Kpkr@153",
    "database": "colabcloud"
}



scraped_time = datetime.now().replace(second=0, microsecond=0)

# ---------------- DRIVER -------------------
def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

# ---------------- COLLECTION -----------------
def collect_listings():
    driver = get_driver()
    driver.get("https://www.croma.com/televisions-accessories/televisions/c/997")
    wait = WebDriverWait(driver, 15)

    print(f"Starting Scrape at: {SCRAPE_TIME_STR}")
    print("Collecting product listings...")
    
    for _ in range(30): 
        try:
            driver.execute_script("window.scrollBy(0, 1200);")
            time.sleep(1.5)
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'View More')]")))
            driver.execute_script("arguments[0].click();", btn)
        except:
            break

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    items = soup.find_all("li", class_="product-item")
    print("-" * 30)
    print(f"TOTAL PRODUCTS EXTRACTED: {len(items)}")
    print("-" * 30)
    return items

def extract_screen_resolution(text):
    if not text:
        return "Unknown"

    t = text.upper()

    if re.search(r"\b8K\b", t):
        return "8K"
    if re.search(r"ULTRA\s*HD|\b4K\b", t):
        return "4K"
    if re.search(r"FULL\s*HD", t):
        return "Full HD"
    if re.search(r"HD\s*READY|\bHD\b", t):
        return "HD"

    return "Unknown"


def extract_panel_type(text):
    if not text:
        return "Unknown"

    t = text.upper()

    if re.search(r"MINI\s*LED", t):
        return "Mini LED"
    if re.search(r"QNED", t):
        return "QNED"
    if re.search(r"QLED", t):
        return "QLED"
    if re.search(r"OLED", t):
        return "OLED"
    if re.search(r"NANOCELL", t):
        return "NanoCell"
    if re.search(r"\bLED\b", t):
        return "LED"

    return "Unknown"



# ---------------- PROCESSING -----------------
def stage_products(items):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    driver = get_driver()


    insert_sql = """
    INSERT INTO croma_stg 
    (product_id, platform, brand, model_number, full_name, display_type, 
     sale_price, original_cost, discount, rating, stock_status, 
     product_url, image_url, scraped_at, panel_type) 
    VALUES (%s, 'Croma', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for idx, item in enumerate(items, start=1):
        try:
            link = item.find("a", href=True)
            if not link: continue
            
            product_url = "https://www.croma.com" + link["href"]
            product_id = re.search(r"/p/(\d+)", product_url).group(1)

            full_name = item.find("h3").text.strip()
            brand = full_name.split()[0]

            sale_el = item.select_one("span.amount, .sale-price, .cp-product-price")
            sale_price = sale_el.text.strip() if sale_el else "0"

            mrp_el = item.select_one("span.old-price, .mrp, .cp-product-mrp")
            original_cost = mrp_el.text.strip() if mrp_el else sale_price

            disc_el = item.select_one("span.discount-newsearch-plp, .cp-productDiscount")
            discount = disc_el.text.strip() if disc_el else "0"

            rating_el = item.select_one(".cp-product-rating, .cp-rating")
            rating = rating_el.text.strip() if rating_el else "0"

            img = item.find("img")
            image_url = img.get("data-src") or img.get("src") if img else "N/A"

            # DEEP SCRAPE for Model Number
            driver.get(product_url)
            time.sleep(1)
            psoup = BeautifulSoup(driver.page_source, "html.parser")

            model_number = "N/A"
            lbl = psoup.find("h4", string=re.compile("Model Number", re.I))
            if lbl:
                val = lbl.find_parent("li").find_next_sibling("li")
                model_number = val.text.strip() if val else "N/A"

            stock_status = "Out of Stock" if "Out of Stock" in driver.page_source else "In Stock"
            
            screen_type = extract_screen_resolution(full_name)
            panel_type = extract_panel_type(full_name)


            # Execute INSERT using the GLOBAL constant SCRAPE_TIME_STR
            cursor.execute(insert_sql, (
                product_id, brand, model_number, full_name, screen_type,
                sale_price, original_cost, discount, rating, stock_status,
                product_url, image_url, scraped_time, panel_type
            ))
                
            conn.commit() 
            

        except Exception as e:
            print(f"Error at item {idx}: {e}")
            continue

    driver.quit()
    conn.close()

def main():
    items = collect_listings()
    # Batch processing for stability
    batch_size = 30
    for i in range(0, len(items), batch_size):
        stage_products(items[i:i + batch_size])

if __name__ == "__main__":
    main()