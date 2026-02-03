'''
1. Take an product categery from flipkart
2. Identify How to scrap the data without knowing that our scraper is a bot.
3. To confuse Flipkart Bot Catcher, Take a link - That link should be like price range and sorting link, to behave not like bot
4. Take Some price ranges
5. use request.Session() to save cookies 
6. Take 1st price range - containing link
7. Use span tag to find how many products( total_products) are there in that price range - for loop
8. Then use math.ceil to find how many pages are there in that price cetagery using total_products / 24
9. And Every page for all cetogeries has 24 constant products expect last page
10. To get all the products for every page use a if condition like - The products of the current page is != 24 
11. Try to fetch the page until product count of the current page == 24, using some delay for every time untill 5
12. Connect to Db and  Then Extract all the required data and append the data to db
Note: Using price ranges and some sort by technique is manditory because our scraper 
    will be blocked if we take a single link and we can extract all the products.

'''


from bs4 import BeautifulSoup as bs
import requests, time, re, random, math
from datetime import datetime
import mysql.connector

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kpkr@153",
        database="colabcloud",
        autocommit=True
    )

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Windows NT 10.0; rv:122.0) Gecko/20100101 Firefox/122.0",
]

def get_headers():
    return {
        "User-Agent": random.choice( user_agents ),
        "Accept-Language": "en-US,en;q=0.9",
    }

price_ranges = [
    ( "0-14999", 0, 14999 ),
    ( "15000-22999", 15000, 22999 ),
    ( "23000-29999", 23000, 29999 ),
    ( "30000-39999", 30000, 39999 ),
    ( "40000-49999", 40000, 49999 ),
    ( "50000-59999", 50000, 59999 ),
    ( "60000+", 60000, "Max" ),
]

def get_url( min_p, max_p, page ):
    
    base_url = (
        "https://www.flipkart.com/search?q=tv"
        "&otracker=search&otracker1=search"
        "&marketplace=FLIPKART&as-show=on&as=off"
        "&sort=price_asc"
    )
    base_url += f"&p%5B%5D=facets.price_range.from%3D{ min_p }"
    base_url += f"&p%5B%5D=facets.price_range.to%3D{ max_p }"
    base_url += f"&page={ page }"
    return base_url
 
def fetch_page( session, url, retries = 5 ):
    for i in range( retries ):
        try:
            r = session.get( url, headers = get_headers(), timeout = 30 )
            if r.status_code == 200:
                return r
            if r.status_code == 429:
                time.sleep(( 2 ** i ) * 3)
        except:
            time.sleep(( 2 ** i ) * 2)
    return None  

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
   
def smart_delay( base = 2, end = 2 ):
    time.sleep( base + random.uniform( 0, end ))
    
def scrap_page_until_last_product( session, url, expected_products_count, retry_page = 6 ):
    for _ in range( retry_page ):
        r = fetch_page( session, url )
        # if r is none skip page
        if not r:
            continue
        soup = bs( r.text, "lxml" )
        cards = soup.find_all( "div", class_ = "nZIRY7" )
        if len( cards ) == expected_products_count:
            return soup, cards
        # if len of cards != expected_products_count - then retry the page with 3 - 5 delay untill len of cards == 24
        smart_delay( 3, 2 )
    return soup, cards  

def extract_product_details( tv ):
    
    title = tv.find( "div", class_ = "RG5Slk" )
    
    name = title.get_text( strip = True ) if title else None
  
    brand = name.split()[0] if name and name.split() else None
    
    i = re.search( r'(\d{2,3})\s*[-"]?\s*(inch|inches|")', name.lower() ) if name else None
    size_of_screen = int( i.group(1) ) if i else None
    
    return title, name, brand, size_of_screen

def extract_pid( url ):
    m = re.search( r'pid=([A-Z0-9]+)', url )
    return m.group(1) if m else None
    
def extract_product_url( tv ):
    link = tv.find( "a", class_ = "k7wcnx" )
    product_url = "https://www.flipkart.com" + link["href"] if link else None
    return product_url
    
def extract_image_url( tv ):
    img = tv.find( "img", class_ = "UCc1lI" )
    image_url = img["src"] if img else None
    return image_url

def extract_ul_list_details(tv):
    model = year = screen_resolution = panel_technology = sound = warranty = None

    specs = tv.find("div", class_="CMXw7N")
    if not specs:
        return model, year, screen_resolution, panel_technology, sound, warranty

    for li in specs.find_all("li"):
        txt = li.get_text(strip=True)

        # Model ID
        m = re.search(r"Model\s*ID[:\s]*(.+)", txt, re.I)
        if m:
            model = m.group(1)
            continue

        # Launch Year
        y = re.search(r"\b(19|20)\d{2}\b", txt)
        if "Launch Year" in txt and y:
            year = y.group(0)
            continue

        # Screen Resolution (REGEX ONLY)
        if re.search(r"HD\s*Ready", txt, re.I):
            screen_resolution = "HD"
        elif re.search(r"Full\s*HD", txt, re.I):
            screen_resolution = "Full HD"
        elif re.search(r"Ultra\s*HD|\b4K\b", txt, re.I):
            screen_resolution = "4K"
        elif re.search(r"\b8K\b", txt, re.I):
            screen_resolution = "8K"

        # Panel Technology (REGEX ONLY)
        if re.search(r"Mini\s*LED", txt, re.I):
            panel_technology = "Mini LED"
        elif re.search(r"Neo\s*QLED", txt, re.I):
            panel_technology = "Neo QLED"
        elif re.search(r"\bQLED\b", txt, re.I):
            panel_technology = "QLED"
        elif re.search(r"\bOLED\b", txt, re.I):
            panel_technology = "OLED"
        elif re.search(r"Nano\s*Cell", txt, re.I):
            panel_technology = "NanoCell"
        elif re.search(r"\bLED\b", txt, re.I):
            panel_technology = "LED"

        # Sound
        s = re.search(r"Total\s*Sound\s*Output[:\s]*(.+)", txt, re.I)
        if s:
            sound = s.group(1)
            continue

        # Warranty
        if re.search(r"Warranty", txt, re.I):
            warranty = txt

    return model, year, screen_resolution, panel_technology, sound, warranty

 
def extract_prices( tv ):
    sp = tv.find( "div", class_="hZ3P6w" )
    selling_price = int(sp.get_text(strip=True).replace("₹", "").replace(",", "")) if sp else None

    op = tv.find( "div", class_="kRYCnD" )
    original_price = int(op.get_text(strip=True).replace("₹", "").replace(",", "")) if op else None

    dp = tv.find( "div", class_="HQe8jr" )
    discount = int(re.sub(r"\D", "", dp.get_text())) if dp else None
    return selling_price, original_price, discount

def extract_assured_product( tv ):
    assured = "Yes" if tv.find( "div", class_="qYp2rh") else "No"
    return assured
    
def extract_unavailable_product( tv ):
    unavailable = "Yes" if tv.find( "div", class_="bgFu62" ) else "No"
    return unavailable

def extract_ratings( tv ):
    rv = tv.find( "div", class_="MKiFS6" )
    rating_value = float(rv.get_text()) if rv else None

    rc = tv.find( "div", class_="a7saXW" )
    rating_count = int(re.sub(r"\D", "", rc.get_text())) if rc else None
    return rating_value, rating_count

scraped_time = datetime.now().replace(second=0, microsecond=0)
    
session = requests.Session()
session.get( "https://www.flipkart.com", headers = get_headers() )
smart_delay( 2, 1 )

conn = get_mysql_connection()
cursor = conn.cursor()

insert_sql = """
INSERT INTO flipkart_products_new (
    platform, platform_product_id,
    brand, product_name,screen_size, model_id, launch_year, screen_type, panel_type, sound, 
    warranty, selling_price, original_price, discount_percent, flipkart_assured_product,
    rating_value, rating_count,
    product_url, image_url,product_is_unavailable, scraped_at
) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

total_products_scraped = 0 

# Getting min and max price form price_ranges 
for lable, min_p, max_p in price_ranges:
    
    print( f"\nScraping {lable}" )
    
    # Making the complete url
    price_range_url = get_url( min_p, max_p, 1 )
    
    # Fetching the page 
    r = fetch_page( session, price_range_url )
    # if all retries failed to load the page, we will skip that page / url & go to nxt 
    if not r:
        continue
    
    soup = bs( r.text, "lxml" )
    
    total_products, total_pages = get_total_products_and_pages( soup )
    if not total_pages:
        continue
    print( f"Contains {total_pages} Pages with {total_products} Products" )
    p = 0
    
    for page in range( 1, total_pages + 1 ):
        url = get_url( min_p, max_p, page )
        
        if page < total_pages:
            soup, cards = scrap_page_until_last_product( session, url, 24 )
        else:
            r = fetch_page( session, url )
            soup = bs( r.text, "lxml" )
            cards = soup.find_all( "div", class_ = "nZIRY7" )
        print( f"Page {page}: {len(cards)} Products" )
        
        for tv in cards:

            title, name, brand, size_of_screen = extract_product_details( tv )

            product_url = extract_product_url( tv )
            
            pid = extract_pid( product_url )

            image_url = extract_image_url( tv )

            model, year, screen_resolution, panel_technology, sound, warranty = extract_ul_list_details( tv )

            selling_price, original_price, discount = extract_prices( tv )

            assured = extract_assured_product( tv )
            
            unavailable = extract_unavailable_product( tv )

            rating_value, rating_count = extract_ratings( tv )
            
            cursor.execute(
                insert_sql,
                (
                    "flipkart", pid,
                    brand, name, size_of_screen, model, year, screen_resolution, panel_technology, sound, warranty,
                    selling_price, original_price, discount, assured,
                    rating_value, rating_count,
                    product_url, image_url, unavailable,
                    scraped_time
                )
            )
        p += len(cards)
             
        # DELAY FOR EVERY PAGE FOR 2 - 3 SECONDS 
        smart_delay( 2, 1 )
        
    # Total Products Scraped for the following price range
    print(f"Total Products Scraped in {lable}: {p}")
    total_products_scraped += p   
    
    # DELAY FOR EVERY Price range FOR 5 - 8 SECONDS
    smart_delay( 5, 3 )
    
cursor.close()
conn.close()

print( f"\nScraping Completed & Total Products Scraped are : {total_products_scraped}" )  