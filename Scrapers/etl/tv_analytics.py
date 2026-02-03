import pandas as pd
from sqlalchemy import create_engine

# Connect to the database
engine = create_engine(
    "mysql+pymysql://root:Kpkr%40153@localhost:3306/offerzone_project"
)

# Load all masters tables 
tv_prices = pd.read_sql( "select * from tv_platform_latest_master", engine )

tv_products = pd.read_sql( "select * from tv_product_master", engine )

tv_brand = pd.read_sql( "select * from tv_brand_master", engine )

tv_platform = pd.read_sql( "select * from tv_platform_master", engine )

print( "All master tables loaded successfully" )

# ensure sale_price is numeric
tv_prices[ "sale_price" ] = pd.to_numeric( tv_prices[ "sale_price" ], errors = "coerce" )

# Remove rows with nan prices
tv_prices_clean = tv_prices.dropna( subset = ["sale_price" ])

# 1. Price comparision
# which platform is cheapest for each TV

cheapest_platform_per_tv = (
    tv_prices_clean
    .loc[
        tv_prices_clean.groupby([ "brand", "model_id" ])[ "sale_price" ].idxmin()
    ]
    [[ "brand", "model_id", "platform", "sale_price" ]]
)

print( "\n cheapest platform for each tv:" )
print( cheapest_platform_per_tv.head() )

# 2. Get list of available brands from product catlog

available_brands = (
    tv_products[ "brand" ]
    .dropna()
    .unique()
)

print( "\n ---------------------" )
print( "Available brands" )
print( "-----------------------" )

for brand in sorted( available_brands ):
    print( brand )

print( "---------------------" )


# 3. Product details

# Select product- related columns

available_products = tv_products[
    [ "brand", "model_id", "full_name", "display_type" ]
]

print( "\n ---------------------" )
print( "Available TV products" )
print( "----------------------" )
print( available_products.head( 10 ) )
print( "-----------------------" )

# 4. What are the prices of TV available

# Select TV price details

tv_price_list = tv_prices[
    [ "brand", "model_id", "platform", "sale_price" ]
]

print( "\n------------------" )
print( "prices of tvs" )
print( tv_price_list.head( 10 ) )
print( "-------------------" )

# 5. Maximum & Minimum price TV

# Remove rows where price is missing
tv_prices_clean = tv_prices[
    ( tv_prices[ "sale_price"].notna()) &
    ( tv_prices[ "sale_price" ] > 0 )
]

# Find maximum priced TV
max_price_tv = tv_prices_clean.loc[
    tv_prices_clean[ "sale_price" ].idxmax()
]

# Find minimum priced TV
min_price_tv = tv_prices_clean.loc[
    tv_prices_clean[ "sale_price" ].idxmin()
]

print( "\n--------------------------" )
print( "maximum & minimum price TV" )
print( "-----------------------------" )

print( "\n most expensive TV:" )
print( max_price_tv[[ "brand", "model_id", "platform", "sale_price" ]])

print( "\n cheapest TV:" )
print( min_price_tv[[ "brand", "model_id", "platform", "sale_price" ]])
print( "-------------------------------------" )

tv_prices_clean.sort_values( "sale_price" ).head(10)


# 6. what discounts are available on TVS

# Convert discount to numeric
tv_prices[ "discount" ] = pd.to_numeric( tv_prices[ "discount" ], errors = "coerce" )

# keep rows where discount is present and > 0
tv_discounted = tv_prices[
    ( tv_prices[ "discount" ].notna() )  &
    ( tv_prices[ "discount" ] > 0 )
]

# Sort by hightest discount
tv_discounted_sorted = tv_discounted.sort_values(
    by = "discount",
    ascending = False
)

print( "\n ---------------------------" )
print( " TV Discounts" )
print( "------------------------" )

print(
    tv_discounted_sorted[
        [ "brand", "model_id", "platform", "discount", "sale_price" ]
    ].head( 10 )
)

print( "-----------------------------" )

# 7. Which TVs are currently in stock

# Make stock_status consistent

tv_prices[ "stock_status" ] = (
    tv_prices[ "stock_status" ]
    .str.lower()
    .str.strip()
)

# Keep only TVs that are currently in stock
tv_in_stock = tv_prices[
    tv_prices[ "stock_status" ] == "in_stock"
]

# Select columns relevant for stock view

latest_stock = tv_in_stock[
    [ "brand", "model_id", "platform", "sale_price", "scraped_at" ]
]

# Sort by most recently scraped TVs

latest_stock_sorted = latest_stock.sort_values(
    by = "scraped_at",
    ascending = False
)

print( "\n-----------------------" )
print( "Latest TVs currently in stock" )
print( "----------------------------" )
print( latest_stock_sorted.head( 10 ))

# 8. For these TV, which website has lowest price

# Samsung products that actually have prices
available_samsung_products = tv_products.merge(
    tv_prices[[ "model_id" ]],
    on= "model_id",
    how= "inner"
)[[ "brand", "model_id", "full_name", "display_type" ]].drop_duplicates()

print( "\nSamsung TVs currently available for price comparison:" )
print( available_samsung_products.head(10) )

selected_model_id = available_samsung_products.iloc[0]["model_id"]

price_comparison = tv_prices[
    tv_prices[ "model_id"] == selected_model_id
][[ "platform", "sale_price" ]]

print( "\nPrice comparison for selected TV:" )
print( price_comparison )

# 9. Budget friendly TVs

# define budget price
budget_price_limit = 30000

# Select TVS whose price is less than or equal to 30000
budget_tvs = tv_prices_clean[
    tv_prices_clean["sale_price"] <= budget_price_limit
]

# Count how many budget TVs are available on each platform
budget_tv_count_by_platform = (
    budget_tvs
    .groupby( "platform" )
    .size()
    .sort_values( ascending = False )
)

print( "\n platform with more budget TVs" )
print( budget_tv_count_by_platform )

# 10. Which platform has hightest rating

# Convert rating column to numeric (string → number)
tv_prices_clean[ "rating" ] = pd.to_numeric(
    tv_prices_clean[ "rating" ], errors="coerce"
)

# Remove rows where rating is missing
tv_prices_clean = tv_prices_clean[
    tv_prices_clean[ "rating" ].notna()
]

# Calculate average rating for each platform
platform_avg_rating = (
    tv_prices_clean
    .groupby( "platform" )[ "rating" ]   
    .mean()                           
    .sort_values(ascending=False)    
)

# Display platform with highest ratings
print( "\nPlatform with higher average rating" )
print( platform_avg_rating )
print("---------------------------" )

# 11. Which platform has more discount and best rating

# Convert discount to numeric
tv_prices_clean[ "discount" ] = pd.to_numeric(
    tv_prices_clean[ "discount" ], errors="coerce"
)

# Convert rating to numeric
tv_prices_clean[ "rating" ] = pd.to_numeric(
    tv_prices_clean[ "rating" ], errors="coerce"
)

# Keep only valid discount values
tv_prices_clean = tv_prices_clean[
    tv_prices_clean[ "discount" ].notna()
]

# Keep only realistic ratings (1 to 5)
tv_prices_clean = tv_prices_clean[
    (tv_prices_clean[ "rating" ] >= 1) &
    (tv_prices_clean[ "rating" ] <= 5)
]

# Calculate average discount and average rating for each platform
platform_discount_rating = (
    tv_prices_clean
    .groupby( "platform" )
    .agg(
        avg_discount=( "discount", "mean" ),   
        avg_rating=( "rating", "mean" )        
    )
)

# Sort by higher discount first, then higher rating
platform_discount_rating_sorted = (
    platform_discount_rating
    .sort_values(
        by=[ "avg_discount", "avg_rating" ],
        ascending=False
    )
)

print( "\n Platform with high discount and good rating" )
print( platform_discount_rating_sorted )
print( "----------------------------------" )

# 12. Screen type VS price

# Convert sale_price to numeric
tv_prices_clean[ "sale_price" ] = pd.to_numeric(
    tv_prices_clean[ "sale_price" ], errors="coerce"
)

# Keep only valid prices
tv_prices_clean = tv_prices_clean[
    tv_prices_clean[ "sale_price" ] > 0
]

# Calculate average price for each screen type
screen_type_price = (
    tv_prices_clean
    .groupby( "display_type" )[ "sale_price" ]   
    .mean()                                  
    .sort_values()                        
)

print( "\n Screen type vs average price" )
print( screen_type_price )
print( "------------------------" )


# 13. Top rating with less price

# Define budget price limit
budget_price_limit = 30000

# Define top rating threshold
top_rating_limit = 4.5

# Select TVs with high rating and low price
best_value_tvs = tv_prices_clean[
    ( tv_prices_clean[ "sale_price" ] <= budget_price_limit ) &
    ( tv_prices_clean[ "rating" ] >= top_rating_limit )
]

# Select useful columns for display
best_value_tvs = best_value_tvs[
    [ "brand", "model_id", "platform", "sale_price", "rating" ]
]

# Sort by highest rating first, then lowest price
best_value_tvs_sorted = (
    best_value_tvs
    .sort_values(
        by=[ "rating", "sale_price" ],
        ascending= [False, True ]
    )
)

print( "\n Top rating TVs with less price" )
print( best_value_tvs_sorted.head(10) )
print( "------------------------------" )

# 13. Brand wise cheapest platform

# Get index of minimum price for each brand
idx = (
    tv_prices_clean
    .groupby( "brand" )[ "sale_price" ]
    .idxmin()
)

# Select rows with cheapest price per brand
brand_cheapest_platform = tv_prices_clean.loc[
    idx,
    [ "brand", "platform", "sale_price" ]
].sort_values( "brand" )

print( "\n Brand-wise cheapest platform" )
print( brand_cheapest_platform )
print( "-------------------------------" )

# 14. Brand availability across platforms

# Normalize brand and platform text
tv_prices_clean[ "brand" ] = tv_prices_clean[ "brand" ].str.strip().str.upper()
tv_prices_clean[ "platform" ] = tv_prices_clean[ "platform" ].str.strip().str.upper()

# Count how many unique platforms each brand is available on
brand_platform_count = (
    tv_prices_clean
    .groupby( "brand" )[ "platform" ]
    .nunique()
)

# Get total number of platforms
total_platforms = tv_prices_clean[ "platform" ].nunique()

# Brands available on all platforms
brands_all_platforms = brand_platform_count[
    brand_platform_count == total_platforms
]

# Brands available only on one platform
brands_single_platform = brand_platform_count[
    brand_platform_count == 1
]

print( "\n Brands available on ALL platforms" )
print( brands_all_platforms )

print( "\n Brands available on ONLY ONE platform" )
print( brands_single_platform )
print( "------------------------" )

# 14. platform wise discount dependency

# Calculate average discount for each platform
platform_avg_discount = (
    tv_prices_clean 
    .groupby( "platform" )[ "discount" ]   
    .mean()                             
    .sort_values( ascending=False )       
)

# Count number of TVs having discount (>0) per platform
platform_discounted_count = (
    tv_prices_clean[
        tv_prices_clean[ "discount" ] > 0
    ]
    .groupby( "platform" )
    .size()
    .sort_values( ascending=False )
)

print( "\n Platform-wise average discount" )
print( platform_avg_discount )

print( "\n Platform-wise count of discounted TVs" )
print( platform_discounted_count )
print( "-----------------------------" )

# 15. Price range distribution per platform

# Define price range labels and bins
price_bins = [ 0, 30000, 60000, float("inf") ]
price_labels = [ "Budget (<=30k)", "Mid (30k-60k)", "Premium (>60k)" ]

# Create a new column for price range
tv_prices_clean[ "price_range" ] = pd.cut(
    tv_prices_clean[ "sale_price" ],
    bins=price_bins,
    labels=price_labels
)

# Count number of TVs in each price range per platform
platform_price_distribution = (
    tv_prices_clean
    .groupby([ "platform", "price_range" ])
    .size()
)

print( "\n Price range distribution per platform" )
print( platform_price_distribution )
print( "-----------------------------" )