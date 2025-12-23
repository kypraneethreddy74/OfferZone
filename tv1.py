# STEP 1: Import required libraries
# BeautifulSoup -> used to read and extract data from HTML
# re -> used to extract model numbers using pattern matching

from bs4 import BeautifulSoup
import re



# STEP 2: List of saved Amazon TV HTML pages
# These pages were saved manually from the browser
# We use multiple pages to demonstrate pagination

pages = [
    "amazon_tv.html",        # Amazon TV page 1
    "amazon_tv_page2.html"   # Amazon TV page 2
]



# STEP 3: Create data containers
# page_summaries -> stores summary info for each page
# all_products   -> stores only valid TV product blocks

page_summaries = []
all_products = []


# STEP 4: First pass
# Purpose:
# - Read each page
# - Count total containers
# - Identify real TVs vs ads
# - Store page-wise summary
# - Collect valid TV products for later printing

for page_file in pages:

    # Open saved HTML page

    with open( page_file, "r", encoding="utf-8" ) as file:
        html_content = file.read()

    # Parse HTML content into searchable structure

    soup = BeautifulSoup( html_content, "html.parser" )

    # Find all product containers on the page
    # Each container may be a TV, ad, or empty block

    products = soup.find_all("div", class_="s-result-item")

    # Total number of containers on this page

    total_containers = len(products)

    # Counter to track real TVs on this page

    real_tv_count = 0


    
    # Loop through containers to identify valid TV products
    # A valid TV must have:
    # - TV name
    # - Price
    
    for product in products:

        name_tag = product.find( "h2" )
        price_tag = product.select_one( "span.a-offscreen" )

        # If both name and price exist, it is a real TV

        if name_tag and price_tag:
            real_tv_count += 1

            # Store product for later detailed printing
            all_products.append( product )

    # Ads / invalid items = total containers - real TVs
    
    ads_count = total_containers - real_tv_count

    # Store page summary in dictionary format

    page_summaries.append({
        "page": page_file,
        "total": total_containers,
        "real": real_tv_count,
        "ads": ads_count
    })



# STEP 5: Print summary of all pages
# This gives an overview before showing TV details

print( "\n---------------- PAGE SUMMARY -----------------" )

for summary in page_summaries:
    print( f"\nPage               : {summary['page']}" )
    print( f"Total containers     : {summary['total']}" )
    print( f"Real TVs extracted   : {summary['real']}" )
    print( f"Ads / invalid items  : {summary['ads']}" )

print( "\n---------------------------------\n" )



# STEP 6: PRINT all TV details
# Now we loop through only valid TV products

tv_count = 0

for product in all_products:

    
    # Extract TV Name
    
    name_tag = product.find( "h2" )
    tv_name = name_tag.get_text( strip=True )

    
    # Extract Price
    
    price_tag = product.select_one( "span.a-offscreen" )
    tv_price = price_tag.get_text( strip=True )

    
    # Extract Brand
    # Brand is usually the first word in TV name
    
    tv_brand = tv_name.split()[ 0 ]

    
    # Extract Model Number using regex
    # Model numbers contain uppercase letters and digits
    
    model_match = re.findall( r"[A-Z0-9]{4,}", tv_name )
    tv_model = model_match[ -1 ] if model_match else "Model not found"

    
    # Extract Rating 
    # Some TVs may not have ratings
    
    rating_tag = product.find( "span", class_ = "a-icon-alt" )
    tv_rating = rating_tag.get_text( strip=True ) if rating_tag else "No rating"

    
    # Extract Image URL 
    
    image_tag = product.find( "img", class_="s-image" )
    tv_image = image_tag[ "src" ] if image_tag else "No image"

    # Increase overall TV counter
    tv_count += 1

    
    # Print TV details
    
    print( f"------------------------ TV {tv_count} -----------------" )
    print( "TV Name     :", tv_name )
    print( "Brand       :", tv_brand )
    print( "Model       :", tv_model ) 
    print( "Price       :", tv_price )
    print( "Rating      :", tv_rating )
    print( "Image URL   :", tv_image )
    print( "-------------------------------------------------------" )



# STEP 7: Final over all total

print( "\n TOTAL TVs extracted from all pages:", tv_count )
