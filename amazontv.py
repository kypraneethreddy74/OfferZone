# Used to send HTTP requests to Amazon
import requests

# Used to parse and read HTML content                
from bs4 import BeautifulSoup

# Used to add delay between requests
import time

# Used to randomly select headers
import random

# Used for pattern matching (brand, model, price)
import re 

# Used to save data into CSV file
import csv                        


# STEP 1: HIGH-SECURITY HEADERS
# These headers make our script behave like a real browser
# Using multiple headers helps reduce Amazon blocking
header_list = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-GB,en;q=0.8",
        "Referer": "https://www.amazon.in/"
    }
]


# STEP 2: BRAND CLEANING FUNCTION 
# This function extracts a clean and correct brand name
# It avoids wrong brands like INCH, CM, HD, etc.
def get_clean_brand( full_name ):

    # List of known TV brands
    known_brands = [
        "SAMSUNG", "LG", "SONY", "XIAOMI", "MI", "REDMI", "ONEPLUS",
        "TCL", "ACER", "HISENSE", "VU", "IFFALCON", "KODAK",
        "SANSUI", "PANASONIC", "AMAZON BASICS", "TOSHIBA",
        "PHILIPS", "VW", "BPL", "LLOYD", "BLAUPUNKT"
    ]

    # Convert full product name to uppercase for easy matching
    name_up = " " + full_name.upper() + " "

    # First try to find exact brand name using word boundary
    # This avoids errors like MI inside PREMIUM
    for b in known_brands:
        if re.search( r'\b' + re.escape(b) + r'\b', name_up ):
            return b

    # If brand not found above, fallback logic
    # Pick first valid word that is not a size or number
    for word in full_name.split():
        clean_w = word.upper().strip(".,-")

        # Ignore words containing digits and size related words
        if not any( char.isdigit() for char in clean_w ) and clean_w not in [
            "INCH", "CM", "INCHES", "FULL", "HD"
        ]:
            if len (clean_w ) > 1:
                return clean_w

    # If nothing works, return UNKNOWN
    return "UNKNOWN"


#  STEP 3: MODEL ID EXTRACTION 
# This function extracts model ID from product title
# If not found, it falls back to Amazon ASIN
def get_clean_model( name, url ):

    # Remove brackets to simplify product name
    clean_name = re.sub( r'[()\[\]]', ' ', name )
    words = clean_name.split()

    # Words to exclude from model detection
    exclude = [
        "4K", "ULTRA", "WATTS", "DDR3", "DDR4",
        "INCH", "INCHES", "NITS", "HZ",
        "WOOD", "UNIT", "WARRANTY", "PROTECTOR"
    ]

    # Scan words from right side (model usually appears at end)
    for word in reversed( words ):
        w = word.upper().strip(".,-")

        # Model must contain both letters and numbers
        if any(c.isdigit() for c in w) and any( c.isalpha() for c in w ):

            # Skip size formats like 55-INCH
            if not re.search( r'\d+(INCH|CM|INCHES)', w ) and len(w) >= 5:
                if w not in exclude:
                    return w

    # If model not found in name, extract ASIN from URL
    match = re.search( r'/dp/([A-Z0-9]{10})', url )
    return match.group(1) if match else "Not Found"


#  STEP 4: PRICE CLEANING 
# Converts price like "15,990.00" into integer 15990
def parse_price( price_text ):
    clean = price_text.replace(',', '').split('.')[0]
    return int(re.sub( r'\D', '', clean ))


# --- STEP 5: MAIN SCRAPER FUNCTION ---
def scrape_amazon_total_cleanup():

    # Creates a new session with random headers
    def get_new_session():
        s = requests.Session()
        s.headers.update(random.choice( header_list ))
        return s

    session = get_new_session()

    # Broad search keywords to cover all TV categories
    broad_searches = [
        "google tv", "android tv", "smart tv",
        "4k tv", "oled tv", "qled tv",
        "32 inch tv", "43 inch tv", "55 inch tv",
        "sony bravia"
    ]

    # Shuffle keywords to look more human-like
    random.shuffle( broad_searches )

    total_extracted_rows = 0

    # Create CSV file and write header row
    with open( 'amazon_tvs_final_perfected1.csv', mode='w', newline='', encoding='utf-8' ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "No", "Product ID", "Brand", "Model ID", "Full Name",
            "Sale Price", "Original Cost", "Discount",
            "Rating", "Product URL", "Image URL"
        ])

        # Loop through each search keyword
        for search_term in broad_searches:
            current_url = f"https://www.amazon.in/s?k={search_term.replace(' ', '+')}"
            print(f"\n>>> CATEGORY: {search_term.upper()}")

            # Limit pages to avoid infinite pagination
            for page_number in range( 1, 15 ):
                try:
                    # Delay to avoid getting blocked
                    time.sleep(random.uniform(5, 8))

                    response = session.get( current_url, timeout=30 )

                    # Detect Amazon anti-bot page
                    if "To discuss automated access" in response.text:
                        print("!!! BLOCKED. Refreshing session...")
                        session = get_new_session()
                        time.sleep(45)
                        continue

                    soup = BeautifulSoup( response.text, "html.parser" )

                    # Each container represents one product
                    products = soup.find_all(
                        "div", {"data-component-type": "s-search-result"}
                    )

                    # If no products found, stop pagination
                    if not products:
                        break

                    for item in products:

                        # Skip sponsored ads
                        if item.find("span", string=re.compile( "Sponsored|Ad", re.I )):
                            continue

                        # Get product title
                        name_tag = item.find( "h2" )
                        if not name_tag:
                            continue

                        full_name = name_tag.get_text( strip=True )
                        ln = full_name.lower()

                        # Remove accessories and non-TV items
                        bad_words = [
                            "protector", "anti glare", "matte filter", "film",
                            "unit", "cabinet", "table", "rack", "shelf",
                            "drawer", "furniture", "remote", "mount",
                            "stabilizer", "cable", "stand", "wood",
                            "warranty", "delivery", "service"
                        ]

                        if any( w in ln for w in bad_words ):
                            continue

                        # Ensure item is actually a TV
                        if "tv" not in ln:
                            continue

                        # Extract sale price
                        price_tag = item.find( "span", class_="a-price-whole" )
                        if not price_tag:
                            continue

                        sale_price = parse_price(price_tag.get_text( strip=True ))

                        # Filter cheap non-TV products
                        if sale_price < 7000:
                            continue

                        # Extract product URL and ASIN
                        product_link = item.find( "a", class_="a-link-normal s-no-outline" )
                        product_url = "https://www.amazon.in" + product_link[ 'href' ].split("?")[0]
                        asin = re.search(r'/dp/([A-Z0-9]{10})', product_url).group(1) if "/dp/" in product_url else "N/A"

                        # Extract brand and model
                        brand = get_clean_brand( full_name )
                        model_id = get_clean_model( full_name, product_url )

                        # Extract original price if available
                        cost_span = item.find( "span", class_="a-price a-text-price" )
                        original_cost = sale_price

                        if cost_span:
                            cost_val = parse_price(
                                cost_span.find( "span", class_="a-offscreen" ).get_text( strip=True )
                            )
                            if cost_val < ( sale_price * 6 ):
                                original_cost = cost_val

                        # Extract discount percentage
                        discount_tag = item.find( "span", string=re.compile(r'% off') )
                        discount = re.sub(r'\D', '', discount_tag.get_text( strip=True )) if discount_tag else "0"

                        # Extract rating
                        rating = (
                            item.find( "span", class_="a-icon-alt" )
                            .get_text( strip=True )
                            .split(" ")[0]
                            if item.find( "span", class_="a-icon-alt" )
                            else "N/A"
                        )

                        # Extract image URL
                        image_url = item.find( "img", class_="s-image" ).get("src")

                        total_extracted_rows += 1

                        # Print extracted data for verification
                        print( f"ROW NUMBER    : {total_extracted_rows}" )
                        print( f"PRODUCT ID    : {asin}" )
                        print( f"BRAND         : {brand}" )
                        print( f"MODEL ID      : {model_id}" )
                        print( f"FULL NAME     : {full_name}" )
                        print( f"SALE PRICE    : {sale_price}" )
                        print( f"ORIGINAL COST : {original_cost}" )
                        print( f"DISCOUNT      : {discount}" )
                        print( f"RATING        : {rating}" )
                        print( f"PRODUCT URL   : {product_url}" )
                        print( f"IMAGE URL     : {image_url}" )
                        print( "-" * 50)

                        # Save row into CSV
                        writer.writerow([
                            total_extracted_rows, asin, brand, model_id,
                            full_name, sale_price, original_cost,
                            discount, rating, product_url, image_url
                        ])

                        # Ensure data is written immediately
                        file.flush()

                    # Go to next page if available
                    next_link = soup.find( "a", class_="s-pagination-next" )
                    if next_link:
                        current_url = "https://www.amazon.in" + next_link['href']
                    else:
                        break

                except Exception:
                    continue

    # Final success message
    print( f"SUCCESS! Total Clean TVs: {total_extracted_rows}" )


# Entry point of the script
if __name__ == "__main__":
    scrape_amazon_total_cleanup()
