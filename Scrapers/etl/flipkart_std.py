import pandas as pd
from db_connection import get_connection
from sqlalchemy import create_engine

# Create database connection
conn = get_connection()

# Read raw flipkart table into pandas dataframe
data = pd.read_sql( "select * from flipkart_products_new", conn )

# Display first few rows
print( data.head())

# Check how many null values are present in each column
print( data.isna().sum() )

# Converts string "NULL" into real missing values
data = data.replace( "NULL", pd.NA )

# Check how many null values are present in each column
print( data.isna().sum())

# Standardize column names
# Remove extra spaces
# Convert to lowercase
# replace spaces with underscore
data.columns = (
    data.columns
        .str.strip()
        .str.lower()
        .str.replace( " ", "_" )
)

# Rename flipkart-specific columns to common names
data = data.rename( columns = {
    "product_name"        : "full_name",
    "selling_price"       : "sale_price",
    "original_price"      : "original_cost",
    "discount_percent"    : "discount",
    "rating_value"        : "rating",
    "platform_product_id" : "product_id",
    "screen_type"         : "display_type",
    "panel_type"           : "screen_resolution"
})

# Convert price and discount columns to numeric values
data[ "sale_price" ] = pd.to_numeric( data[ "sale_price" ], errors = "coerce" )
data[ "original_cost" ] = pd.to_numeric( data[ "original_cost" ], errors = "coerce" )
data[ "discount" ] = pd.to_numeric( data[ "discount"], errors = "coerce" )

# If original price is missing, assume no discount
# So original_cost = sale_price
data[ "original_cost" ] = data[ "original_cost" ].fillna( data[ "sale_price" ] )
data[ "sale_price" ] = data[ "sale_price" ].fillna( data[ "original_cost" ])

# If discount is missing, assume 0%
data[ "discount" ] = data[ "discount" ].fillna( 0 )

# Convert rating column to numeric
# If rating is not a number, convert it to null
data[ "rating" ] = pd.to_numeric( data[ "rating" ], errors = "coerce" )

# Fill missing brand and model_id
data[ "brand" ] = data[ "brand" ].fillna( "UNKNOWN" )
data[ "model_id" ] = data[ "model_id" ].fillna( "UNKNOWN" )

# Normalize text values
data[ "brand" ] = data[ "brand" ].str.upper().str.strip()
data[ "model_id" ] = data[ "model_id" ].str.upper().str.strip()

# Clean product availability text
data[ "product_is_unavailable" ] = (
    data[ "product_is_unavailable" ]
        .str.lower()
        .str.strip()
)

# Create a unified stock_status column
data[ "stock_status" ] = data[ "product_is_unavailable" ].map({
    "yes" : "out_of_stock",
    "no" : "in_stock"
})

# Normalize platform values
data[ "platform" ] = (
    data[ "platform" ]
    .str.lower()
    .str.strip()
)

# Convert scraped_at column to datetime
# errors = "coerce" means invalid dates become null
data[ "scraped_at" ] = pd.to_datetime( data[ "scraped_at" ], errors = "coerce" )

# Convert sale_price to numeric
data[ "sale_price" ] = pd.to_numeric( data [ "sale_price" ], errors="coerce" )

# Treat zero or negative prices as invalid
data[ "sale_price" ] = data[ "sale_price" ].fillna( 0 )
data[ "original_cost" ] = data[ "original_cost" ].fillna( 0) 



data[ "rating" ] = data[ "rating" ].fillna( 0 )

print( data.isna().sum() )

data = (
    data.sort_values( "scraped_at", ascending=False )
      .drop_duplicates(
          subset=[ "product_id", "scraped_at" ],
          keep="first"
      )
)


# Select only standardized columns
data = data[
    [
        "platform",
        "product_id",
        "brand",
        "model_id",
        "full_name",
        "sale_price",
        "original_cost",
        "discount",
        "rating",
        "stock_status",
        "scraped_at",
        "product_url",
        "image_url",
        "display_type",
        "screen_resolution"
    ]
]

# Create sqlalchemy engine to write data to mysql
engine = create_engine(
    "mysql+pymysql://root:Kpkr%40153@localhost:3306/offerzone_project"

)

data.to_sql(
    name = "flipkart_tv_standardized",
    con = engine,
    if_exists = "replace",
    index = False
)

print( "Flipkart standardized data stored successfully" )