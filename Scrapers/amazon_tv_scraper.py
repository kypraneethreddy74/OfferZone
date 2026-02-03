import requests, re, random, time
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os


# =========================
# HEADERS
# =========================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Windows NT 10.0; rv:122.0) Gecko/20100101 Firefox/122.0",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
        "Referer": "https://www.amazon.in/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

# =========================
# BRANDS (CAMEL CASE)
# =========================
KNOWN_BRANDS = sorted({
    "Motorola","Acer","Sony","Onida","Lg","Lemorele","Philips","Samsung","Vw",
    "Redmi","Sansui","Trusense","Panasonic","Lloyd","Xiaomi","Tcl","Oneplus",
    "Hisense","Hyundai","Earthonic","Bpl","Nokia","Kodak","Vu","Toshiba",
    "Blaupunkt","Apple","Foxsky","Fire","Rokid","Electron","Nvidia","Haier",
    "Black+Decker","Black & Decker","Samtonic","Thomson","Realme","Infinix",
    "Iffalcon","Mitashi","Aiwa","Reliance","Marq","Beston","Voir","Coocaa",
    "Imee","Vone","Iair","Daiwa","Limeberry","Nvy","Xelectron","Acerpure","Nu",
    "Skylive","Innoq","Reintech","Uniboom","Invater","Nacson","Compaq","Huidi",
    "Bush","Wybor","Starshine","Metz","Vzy","Zebronics","Admiral","Kenstar",
    "Mi","Rgl","Elista","Dor","Sharp","Qthin","Micromax","Jvc","Weston","Plus",
    "Sens","Doodle","Phx","Croma","Amazon","Logitech","Westinghouse","Sonos",
    "Saregama"
}, key=len, reverse=True)

# =========================
# EXTRACTION HELPERS
# =========================
def extract_brand(title):
    text = " " + title.lower() + " "
    for b in KNOWN_BRANDS:
        if re.search(rf"\b{re.escape(b.lower())}\b", text):
            return b
    return title.split()[0].title() if title else None

def extract_screen_size(title):
    if not title:
        return None
    m = re.search(r"(\d{2,3})\s*(inch|inches|\")", title.lower())
    if m:
        return int(m.group(1))
    m = re.search(r"(\d{2,3})\s*cm", title.lower())
    if m:
        return round(int(m.group(1)) / 2.54)
    return None

# =========================
# EXTRACTION HELPERS (UPDATED)
# =========================

def extract_panel_technology(title):
    if not title:
        return None
    t = title.upper()

    if "MINI LED" in t: return "Mini LED"
    if "QLED" in t: return "QLED"
    if "OLED" in t: return "OLED"
    if "NANOCELL" in t: return "NanoCell"
    if "ULED" in t: return "ULED"
    if "CRYSTAL" in t: return "Crystal LED"
    if "LED" in t: return "LED"

    return None


def extract_screen_resolution(title):
    if not title:
        return None
    t = title.lower()

    if "8k" in t or "4320p" in t or "7680" in t:
        return "8K"
    if "4k" in t or "ultra hd" in t or "uhd" in t or "2160p" in t or "3840" in t:
        return "4K"
    if "full hd" in t or "fhd" in t or "1080p" in t:
        return "Full HD"
    if re.search(r"\bhd\b", t) or "720p" in t:
        return "HD"

    return None



def extract_model_id(title):
    if not title:
        return None
    tokens = re.sub(r"[()\[\],]", " ", title.upper()).split()
    for t in tokens[::-1]:
        if any(c.isalpha() for c in t) and any(c.isdigit() for c in t):
            return t
    return None

def extract_asin(url):
    if not url:
        return None
    m = re.search(r"/dp/([A-Z0-9]{10})", url)
    return m.group(1) if m else None

def parse_price(txt):
    try:
        return int(re.sub(r"\D", "", txt))
    except:
        return None

scraped_time = datetime.now().replace(second=0, microsecond=0)
# =========================
# AMAZON URL (UNCHANGED)
# =========================
def get_url(min_p, max_p, page):
    base_url = "https://www.amazon.in/s?k=television&rh=p_36%"
    base_url += f"3A{min_p}00-{max_p}00%"
    base_url += (
        "2Cp_n_feature_browse-bin%3A13466811031%257C1485061031%257C1485062031%257C15430914031"
        f"&s=price-asc-rank&dc&page={page}&"
        "crid=1JWXHA5SEW0O9&qid=1768018360&rnid=14076159031"
        "&sprefix=television%2Caps%2C488&xpid=vbfiKRpdOq7b0"
        f"&ref=sr_pg_{page}"
    )
    return base_url

# =========================
# MAIN SCRAPER (NO FILTERS)
# =========================
def scrape_amazon_tv_full():

    session = requests.Session()
    session.get("https://www.amazon.in", headers=get_headers(), timeout=30)
    time.sleep(2)

    row_no = 0
    if os.path.exists("amazon_tvs_final_fixed21.csv"):
        with open("amazon_tvs_final_fixed21.csv", "r", encoding="utf-8") as f:
            row_no = max(0, sum(1 for _ in f) - 1)

    file = open("amazon_tvs_final_fixed21.csv", "a", newline="", encoding="utf-8")
    writer = csv.writer(file)

    # write header only once (optional safeguard)
    if file.tell() == 0:
        writer.writerow([
            "No","Platform","Product ID","Brand","Model ID","Full Name",
            "Display Type","screen_resolution",
            "Sale Price","Original Cost","Discount",
            "Rating","rating_count","Stock Status",
            "Scraped At","Product URL","Image URL"
        ])



    PRICE_RANGES = [
        ("5000-24999", 5000, 24999),
        ("25000-49999", 25000, 49999),
        ("50000-59999", 50000, 59999),
        ("60000-69999", 60000, 69999),
        ("70000-79999", 70000, 79999),
        ("80000-89999", 80000, 89999),
        ("90000-99999", 90000, 99999),
        ("100000-149999", 100000, 149999),
        ("150000-199999", 150000, 199999),
        ("200000+", 200000, 999999),
    ]

    grand_total = 0

    for label, min_p, max_p in PRICE_RANGES:

        print(f"\nPRICE RANGE: {label}")
        range_total = 0

        r = session.get(get_url(min_p, max_p, 1), headers=get_headers(), timeout=30)
        soup = BeautifulSoup(r.text, "lxml")

        pages = max(
            [int(s.text) for s in soup.find_all("span", class_="s-pagination-item s-pagination-disabled") if s.text.isdigit()],
            default=1
        )

        print(f"   Total Pages: {pages}")

        for page in range(1, pages + 1):

            r = session.get(get_url(min_p, max_p, page), headers=get_headers(), timeout=30)
            soup = BeautifulSoup(r.text, "lxml")

            cards = soup.find_all("div", {"data-component-type": "s-search-result"})
            print(f"   Page {page}: {len(cards)} products found")

            page_count = 0

            for c in cards:
                title = c.find("h2").get_text(strip=True) if c.find("h2") else None
                a = c.find("a", href=True)
                product_url = "https://www.amazon.in" + a["href"].split("?")[0] if a else None

                sp = c.find("span", class_="a-price-whole")
                op = c.find("span", class_="a-offscreen")
                disc = c.find("span", string=re.compile("% off"))
                rating_val = c.find("span", class_="a-size-small")
                rating_cnt = c.find("span", class_="s-underline-text")
                img = c.find("img", class_="s-image")

                rv = None
                if rating_val:
                    m = re.search(r"\d+(\.\d+)?", rating_val.text)
                    if m:
                        rv = float(m.group())

                rc = None
                if rating_cnt:
                    m = re.search(r"\d+", rating_cnt.text)
                    if m:
                        rc = int(m.group())
                
                stock_status = "In Stock"

                unavailable = c.find("span", class_="a-size-small", string=re.compile("unavailable", re.I))
                if unavailable:
                    stock_status = "Out of Stock"


                row_no += 1
                
                writer.writerow([
                    row_no,
                    "Amazon",
                    extract_asin(product_url),                 # Product ID
                    extract_brand(title),                      # Brand
                    extract_model_id(title),                   # Model ID
                    title,                                     # Full Name
                    extract_panel_technology(title),           # Display Type
                    extract_screen_resolution(title),
                    parse_price(sp.text) if sp else None,      # Sale Price
                    parse_price(op.text) if op else None,      # Original Cost
                    int(re.sub(r"\D","",disc.text)) if disc else None,
                    rv,                                        # Rating
                    rc,                                        # rating_count
                    stock_status,
                    scraped_time,
                    product_url,
                    img["src"] if img else None
                ])
                file.flush()

                

                page_count += 1

            print(f"      Inserted: {page_count}")
            range_total += page_count
            time.sleep(1)

        print(f"   TOTAL FOR RANGE {label}: {range_total}")
        grand_total += range_total
    file.close()

    

    print("\n==============================")
    print(f"GRAND TOTAL SCRAPED: {grand_total}")
    print("==============================")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    scrape_amazon_tv_full()