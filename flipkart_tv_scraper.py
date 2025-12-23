import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time
import re

brand_list, title_list, model_list, year_list = [], [], [], []
selling_list, original_list, discount_list = [], [], []
rating_val_list, rating_count_list, review_count_list, url_list = [], [], [], []
price_range_list = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# PRICE RANGES 

price_ranges = [
    ("0-14999", 0, 14999),
    ("15000-39999", 15000, 39999),
    ("40000-59999", 40000, 59999),
    ("60000+", 60000, "Max")  # "Max" is a string, not a variable!
]


def build_url(min_p, max_p, page):
    """Build Flipkart search URL with price filters"""
    base = (
        "https://www.flipkart.com/search?q=tv"
        "&otracker=search&otracker1=search"
        "&marketplace=FLIPKART&as-show=on&as=off"
        "&sort=price_asc"
    )
    
    # Add price range filters
    base += f"&p%5B%5D=facets.price_range.from%3D{min_p}"
    base += f"&p%5B%5D=facets.price_range.to%3D{max_p}"
    
    # Add page number
    base += f"&page={page}"
    
    return base


# SCRAPING

MAX_PAGES = 50
session = requests.Session()

for label, min_p, max_p in price_ranges:
    print(f"\n{'='*50}")
    print(f"Scraping price range: ₹{label}")
    print("="*50)
    
    page = 1
    consecutive_empty = 0
    seen_urls = set()
    
    while page <= MAX_PAGES:
        url = build_url(min_p, max_p, page)
        
        try:
            r = session.get(url, headers=headers, timeout=20)
            r.raise_for_status()
        except Exception as e:
            print(f" Error on page {page}: {e}")
            consecutive_empty += 1
            if consecutive_empty >= 3:
                break
            time.sleep(3)
            continue
        
        soup = bs(r.text, "lxml")
        
        # Find product cards
        product_cards = soup.find_all("div", class_="nZIRY7")
        
        if not product_cards:
            consecutive_empty += 1
            print(f"  No cards found on page {page} (attempt {consecutive_empty})")
            if consecutive_empty >= 2:
                break
            page += 1
            time.sleep(2)
            continue
        
        consecutive_empty = 0
        new_count = 0
        
        for card in product_cards:
            
            # TITLE
            title_tag = card.find("div", class_="RG5Slk")
            if title_tag:
                name = title_tag.get_text(strip=True)
            else:
                name = "N/A"
            
            # URL
            link_tag = card.find("a", class_="k7wcnx")
            if link_tag and link_tag.get("href"):
                href = link_tag["href"]
                full_url = "https://www.flipkart.com" + href
            else:
                full_url = "N/A"
            
            # Skip duplicates
            if full_url != "N/A" and full_url in seen_urls:
                continue
            if full_url != "N/A":
                seen_urls.add(full_url)
            
            # Add to lists
            title_list.append(name)
            url_list.append(full_url)
            price_range_list.append(label)
            
            # BRAND (first word of title)
            if name and name != "N/A":
                brand_list.append(name.split()[0])
            else:
                brand_list.append("N/A")
            
            # MODEL ID & LAUNCH YEAR
            m_id = "N/A"
            l_year = "N/A"
            
            specs_div = card.find("div", class_="CMXw7N")
            if specs_div:
                specs_text = specs_div.get_text(strip=True)
                
                # Extract Model ID
                model_match = re.search(r'Model\s*ID[:\s]*([A-Za-z0-9\-_]+)', specs_text)
                if model_match:
                    m_id = model_match.group(1)
                
                # Extract Launch Year
                year_match = re.search(r'Launch\s*Year[:\s]*(\d{4})', specs_text)
                if year_match:
                    l_year = year_match.group(1)
            
            model_list.append(m_id)
            year_list.append(l_year)
            
            # SELLING PRICE
            sp = card.find("div", class_="hZ3P6w")
            if sp:
                price_text = sp.get_text(strip=True)
                price_clean = price_text.replace("₹", "").replace(",", "")
                selling_list.append(price_clean)
            else:
                selling_list.append("0")
            
            # ORIGINAL PRICE
            op = card.find("div", class_="kRYCnD")
            if op:
                orig_text = op.get_text(strip=True)
                orig_clean = orig_text.replace("₹", "").replace(",", "")
                original_list.append(orig_clean)
            else:
                original_list.append("0")
            
            # DISCOUNT
            dp = card.find("div", class_="HQe8jr")
            if dp:
                disc_text = dp.get_text(strip=True)
                discount_list.append(disc_text)
            else:
                discount_list.append("0%")
            
            # RATING VALUE
            rv = card.find("div", class_="MKiFS6")
            if rv:
                rating_val_list.append(rv.get_text(strip=True))
            else:
                rating_val_list.append("0")
            
            # RATING COUNT & REVIEW COUNT
            rating_div = card.find("div", class_="a7saXW")
            if rating_div:
                rating_text = rating_div.get_text(strip=True)
                
                # Extract rating count
                rc_match = re.search(r'([\d,]+)\s*Ratings?', rating_text)
                if rc_match:
                    rating_count_list.append(rc_match.group(1).replace(",", ""))
                else:
                    rating_count_list.append("0")
                
                # Extract review count
                rev_match = re.search(r'([\d,]+)\s*Reviews?', rating_text)
                if rev_match:
                    review_count_list.append(rev_match.group(1).replace(",", ""))
                else:
                    review_count_list.append("0")
            else:
                rating_count_list.append("0")
                review_count_list.append("0")
            
            new_count += 1
        
        print(f"  Page {page}: {new_count} products scraped (Total: {len(title_list)})")
        
        # Check for next page
        if new_count < 20:
            next_link = soup.find("a", href=lambda x: x and f"page={page+1}" in str(x))
            if not next_link:
                print(f"  ℹ️ No more pages")
                break
        
        page += 1
        time.sleep(1.5)
    
    range_count = len([x for x in price_range_list if x == label])
    print(f"Total for ₹{label}: {range_count} products")


# SAVE TO CSV

df = pd.DataFrame({
    "price_range": price_range_list,
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

initial_count = len(df)
df.drop_duplicates(subset="product_url", inplace=True)
df.to_csv("flipkart_all_tvs.csv", index=False)

print("\n" + "="*50)
print("SCRAPING COMPLETE!")
print("="*50)
print(f"Total scraped: {initial_count}")
print("Saved to: flipkart_all_tvs.csv")
print("="*50)

# Show sample
print("\nFirst 5 products:")
print(df[["brand", "product_name", "selling_price", "rating_value"]].head().to_string())