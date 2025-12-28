import requests
import mysql.connector
from bs4 import BeautifulSoup as bs
import time, re, random, math
from datetime import datetime

# MYSQL CONNECTION

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kpkr@153",
        database="offerzone",
        autocommit=True
    )

# USER AGENTS

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Windows NT 10.0; rv:122.0) Gecko/20100101 Firefox/122.0",
]

def get_headers():
    return {
        "User-Agent": random.choice( USER_AGENTS ),
        "Accept-Language": "en-US,en;q=0.9",
    }

# PRICE RANGES TO CONFUSE FLIPKART BOT SYSTEM 

PRICE_RANGES = [
    ( "0-14999", 0, 14999 ),
    ( "15000-22999", 15000, 22999 ),
    ( "23000-29999", 23000, 29999 ),
    ( "30000-39999", 30000, 39999 ),
    ( "40000-49999", 40000, 49999 ),
    ( "50000-59999", 50000, 59999 ),
    ( "60000+", 60000, "Max" ),
]

# HELPERS TO GET URL FOR EVERY PRICE RANGES AND PAGES FOR THAT PRICE RANGE

def build_url( min_p, max_p, page ):

    base = (
        "https://www.flipkart.com/search?q=tv"
        "&otracker=search&otracker1=search"
        "&marketplace=FLIPKART&as-show=on&as=off"
        "&sort=price_asc"
    )
    base += f"&p%5B%5D=facets.price_range.from%3D{ min_p }"
    base += f"&p%5B%5D=facets.price_range.to%3D{ max_p }"
    base += f"&page={ page }"
    return base
    
# SMART DELAY TO BEHAVE LIKE NORMAL HUMAN

def smart_delay( base = 2, end = 2 ):
    time.sleep( base + random.uniform( 0, end ) )

# FETCH PAGE 

def fetch_page( session, url, retries=5 ):
    for i in range( retries ):
        try:
            r = session.get( url, headers = get_headers(), timeout=30 )
            if r.status_code == 200:
                return r
            if r.status_code == 429:
                time.sleep( (2 ** i) * 3)
        except:
            time.sleep( (2 ** i) * 2)
    return None

# TO GET TOTAL NO OF PRODUCTS AND NO OF PAGES

def get_total_products_and_pages( soup, per_page = 24 ):
    span = soup.find( "span", class_ = "_Omnvo" )
    if not span:
        return None, None
    text = span.get_text( " ", strip = True )
    m = re.search( r"of\s+([\d,]+)\s+results", text )
    if not m:
        return None, None
    total_products = int( m.group(1).replace( ",", "" ) )
    total_pages = math.ceil( total_products / per_page )
    return total_products, total_pages


def scrape_page_until_valid( session, url, expected_count, max_retry=6 ):
    for _ in range( max_retry ):
        r = fetch_page( session, url )
        if not r:
            continue
        soup = bs( r.text, "lxml" )
        cards = soup.find_all( "div", class_="nZIRY7" )
        if len(cards) == expected_count:
            return soup, cards
        smart_delay( 3, 2 )
    return soup, cards

# GETTING PID USING URL

def extract_pid( url ):
    m = re.search( r'pid=([A-Z0-9]+)', url )
    return m.group(1) if m else None

# SCRAPER

session = requests.Session()
session.get( "https://www.flipkart.com", headers=get_headers() )
smart_delay( 2, 1 )

conn = get_mysql_connection()
cursor = conn.cursor()

insert_sql = """
INSERT INTO flipkart_products (
    platform, platform_product_id,
    brand, product_name, model_id, launch_year, screen_type, sound, 
    warranty, selling_price, original_price, discount_percent, flipkart_assured_product,
    rating_value, rating_count,
    product_url, image_url,product_is_unavailable, scraped_at
) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

# SCRAPING THE PAGE USING PRICE RANGES

for label, min_p, max_p in PRICE_RANGES:

    print( f"\nScraping ₹{label}" )

    first_url = build_url( min_p, max_p, 1 )
    r = fetch_page( session, first_url )
    if not r:
        continue

    soup = bs( r.text, "lxml" )
    total_products, total_pages = get_total_products_and_pages( soup )
    if not total_pages:
        continue

    print( f"Pages : {total_pages}" )

    for page in range( 1, total_pages + 1 ):

        url = build_url( min_p, max_p, page )

        if page < total_pages:
            soup, cards = scrape_page_until_valid( session, url, 24 )
        else:
            r = fetch_page( session, url )
            soup = bs( r.text, "lxml" )
            cards = soup.find_all( "div", class_ = "nZIRY7" )

        print(f"Page {page}: {len(cards)} products")

        for card in cards:

            title = card.find( "div", class_="RG5Slk" )
            name = title.get_text( strip = True ) if title else None
            brand = name.split()[0] if name and name.split() else None

            link = card.find( "a", class_ = "k7wcnx" )
            product_url = "https://www.flipkart.com" + link["href"] if link else None
            pid = extract_pid( product_url )

            img = card.find( "img", class_ = "UCc1lI" )
            image_url = img["src"] if img else None

            model, year, screen, sound, warranty = None, None, None, None, None
            specs = card.find( "div", class_ = "CMXw7N" )
            if specs:
                for li in specs.find_all( "li" ):
                    txt = li.get_text( strip = True )

                    if "Model ID" in txt:
                        m = re.search( r"Model\s*ID[:\s]*(.+)", txt )
                        if m: model = m.group(1)
                    elif "Launch Year" in txt:
                        y = re.search( r"(\d{4})", txt )
                        if y: year = y.group(1)
                    elif "HD" in txt:
                        screen = txt 
                    elif "Total Sound Output" in txt:
                        s = re.search( r"Total\s*Sound\s*Output[:\s]*(.+)", txt )
                        if s: sound = s.group(1)
                    elif (
                        "Warranty" in txt
                        or "warranty" in txt
                        or "Year" in txt
                        or "year" in txt
                        or "1" in txt
                        or "2" in txt
                    ):
                        warranty = txt


            sp = card.find( "div", class_ = "hZ3P6w" )
            selling_price = int( sp.get_text( strip = True ).replace( "₹","" ).replace( ",","" )) if sp else None

            op = card.find( "div", class_ = "kRYCnD" )
            original_price = int( op.get_text( strip = True ).replace( "₹","" ).replace( ",","" )) if op else None

            dp = card.find( "div", class_ = "HQe8jr" )
            discount = int( re.sub(r"\D", "", dp.get_text())) if dp else None
            
            assured = "Yes" if card.find("div", class_="qYp2rh") else "No"
            
            unavailable = "Yes" if card.find("div", class_="bgFu62") else "No"

            rv = card.find( "div", class_ = "MKiFS6" )
            rating_value = float( rv.get_text() ) if rv else None

            rc = card.find( "div", class_ = "a7saXW" )
            rating_count = int(re.sub( r"\D", "", rc.get_text())) if rc else None

            cursor.execute(
                insert_sql,
                (
                    "flipkart", pid,
                    brand, name, model, year, screen, sound, warranty,
                    selling_price, original_price, discount, assured,
                    rating_value, rating_count,
                    product_url, image_url, unavailable,
                    datetime.now()
                )
            )
        # DELAY FOR EVERY PAGE FOR 2 - 3 SECONDS 
        smart_delay( 2, 1 )
        
    # DELAY FOR EVERY CATEGORY FOR 5 - 8 SECONDS
    smart_delay( 5, 3 )

cursor.close()
conn.close()

print( "\nSCRAPING COMPLETED" )
