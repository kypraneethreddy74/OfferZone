import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time

# 1. Initialize Lists
brand_list, title_list, model_list, year_list = [], [], [], []
selling_list, original_list, discount_list = [], [], []
rating_val_list, rating_count_list, review_count_list, url_list = [], [], [], []

# Set how many pages you want to scrape (e.g., 1 to 10)
# To get ALL pages, look at the bottom of Flipkart; usually it's around 40-50.
total_pages = 2

print(f"Starting scraper for {total_pages} pages...")

for page in range(1, total_pages + 1):
    print(f"Scraping Page: {page}...")
    
    # Update URL dynamically with the page number
    url = f"https://www.flipkart.com/search?q=tv&page={page}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        r = requests.get(url, headers=headers)
        soup = bs(r.text, "lxml")

        # 2. Find all product card containers
        product_cards = soup.find_all("div", class_="nZIRY7")

        # If no cards are found, we might have hit the end or been blocked
        if not product_cards:
            print("No more products found or blocked. Stopping.")
            break

        for card in product_cards:
            # --- PRODUCT TITLE & BRAND ---
            title_tag = card.find("div", class_="RG5Slk")
            name = title_tag.get_text(strip=True) if title_tag else "N/A"
            title_list.append(name)
            brand_list.append(name.split()[0] if name != "N/A" else "N/A")

            # --- URL ---
            link_tag = card.find("a", class_="k7wcnx")
            if link_tag and link_tag.get('href'):
                url_list.append("https://www.flipkart.com" + link_tag['href'])
            else:
                url_list.append("N/A")

            # --- MODEL ID & LAUNCH YEAR ---
            m_id, l_year = "N/A", "N/A"
            ul_tag = card.find("ul", class_="HwRTzP")
            if ul_tag:
                li_tags = ul_tag.find_all("li", class_="DTBslk")
                for li in li_tags:
                    text = li.get_text(strip=True)
                    if "Model ID" in text:
                        m_id = text.replace("Model ID:", "").strip()
                    if "Launch Year" in text:
                        l_year = text.replace("Launch Year:", "").strip()
            model_list.append(m_id)
            year_list.append(l_year)

            # --- PRICES & DISCOUNT ---
            sp = card.find("div", class_="hZ3P6w")
            op = card.find("div", class_="kRYCnD")
            dp = card.find("div", class_="HQe8jr")
            
            selling_list.append(sp.get_text(strip=True).replace("₹", "").replace(",", "") if sp else "0")
            original_list.append(op.get_text(strip=True).replace("₹", "").replace(",", "") if op else "0")
            discount_list.append(dp.get_text(strip=True).replace("off", "").strip() if dp else "0%")

            # --- RATINGS & REVIEWS ---
            rv = card.find("div", class_="MKiFS6")
            rating_val_list.append(rv.get_text(strip=True) if rv else "0")

            rb = card.find("span", class_="PvbNMB")
            if rb:
                clean_text = rb.get_text(strip=True).replace(",", "")
                parts = clean_text.split('&')
                r_count = parts[0].strip().split()[0] if len(parts) > 0 else "0"
                rev_count = parts[1].strip().split()[0] if len(parts) > 1 else "0"
                rating_count_list.append(r_count)
                review_count_list.append(rev_count)
            else:
                rating_count_list.append("0")
                review_count_list.append("0")
        
        # 3. Wait a second before next page to be polite to the server
        time.sleep(1)

    except Exception as e:
        print(f"An error occurred on page {page}: {e}")
        break

# 4. Create DataFrame
df = pd.DataFrame({
    "brand": brand_list,
    "product_name": title_list,
    "model_id": model_list,
    "launch_year": year_list,
    "selling_price": selling_list,
    "original_price": original_list,
    "discount_percent": discount_list,
    "rating_value": rating_val_list,
    "rating_count": rating_count_list,
    "review_count": review_count_list,
    "product_url": url_list
})

# 5. Export to CSV
df.to_csv("flipkart_all_tvs.csv", index=False)

print("-" * 30)
print(f"Scraping Complete!")
print(f"Total products saved: {len(df)}")
print("-" * 30)