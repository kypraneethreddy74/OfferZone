import requests
import pandas as pd
from bs4 import BeautifulSoup
import re


def get_soup(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    return BeautifulSoup(response.text, "html.parser")

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
    else:
        return "Unknown"
    
def scrape_one_page(soup, data):
    box = soup.find("div", class_="QSCKDh dLgFEE")
    if box is None:
        return 0

    names = box.find_all("div", class_="RG5Slk")
    prices = box.find_all("div", class_="hZ3P6w DeU9vF")
    ratings = box.find_all("div", class_="MKiFS6")

    max_len = max(len(names), len(prices), len(ratings))

    for i in range(max_len):
        if i < len(names):
            full_name = names[i].text.strip()
            lower_name = full_name.lower()

            # BRAND
            brand = full_name.split()[0]

            # INCHES
            inch_match = re.search(r'(\d{2})\s*(inch|")', lower_name)
            inches = inch_match.group(1) if inch_match else "N/A"

            #  PANEL TYPE
            panel_type = extract_panel_type(lower_name)

            #  LAUNCH YEAR
            year_match = re.search(r'(20[1-2][0-9])', full_name)
            launch_year = year_match.group(1) if year_match else "N/A"

            #  MODEL
            model = full_name
            model = model.replace(brand, "")
            if inch_match:
                model = model.replace(inch_match.group(0), "")
            if year_match:
                model = model.replace(launch_year, "")
            model = model.replace(panel_type, "").strip()

        else:
            brand = model = inches = panel_type = launch_year = "N/A"

        data.append({
            "brand": brand,
            "model": model,
            "inches": inches,
            "panel_type": panel_type,
            "launch_year": launch_year,
            "price": prices[i].text.strip() if i < len(prices) else "N/A",
            "rating": ratings[i].text.strip() if i < len(ratings) else "0"
        })

    return max_len

def scrape_flipkart_all_pages():
    data = []
    page = 1

    while True:
        print(f"Scraping page {page}")
        url = f"https://www.flipkart.com/search?q=television&page={page}"
        soup = get_soup(url)

        count = scrape_one_page(soup, data)
        if count == 0:
            break

        page += 1

    return pd.DataFrame(data)

df = scrape_flipkart_all_pages()

print(df.head())
print("Total products scraped:", len(df))

df.to_csv("C:/sudheerpy/flipkart_televisions_clean.csv", index=False)
print("CSV file saved successfully")    