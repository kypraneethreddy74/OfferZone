import pandas as pd
from db_connection import get_connection
from sqlalchemy import create_engine

# Connect to mysql
conn = get_connection()

# Read raw croma table
data = pd.read_sql( "select * from croma_tvsss", conn )

# View first few rows
print( data.head() )

# Check column names
print( data.columns.tolist() )

# Rename model number to model id for consistency
data = data.rename( columns = {
    "model_number" : "model_id"
})

# Verify column names after renaming
print( data.columns.tolist() )

# Check null values in each column
print( data.isna().sum() )

# Standardize brand and model_id
data[ "brand" ] = data[ "brand" ].str.upper().str.strip()
data[ "model_id" ] = data[ "model_id" ].str.upper().str.strip()

# Standardize stock_status
data[ "stock_status" ] = (
    data[ "stock_status" ]
    .str.lower()
    .str.replace( " ", "_" )
    .str.strip()
)

# Standardize display_type
data[ "display_type" ] = data[ "display_type" ].str.upper().str.strip()

# Convert numeric columns safely
# convert invalid values to null instead of crashing

data[ "sale_price" ] = pd.to_numeric( data[ "sale_price" ], errors = "coerce" )
data[ "original_cost" ] = pd.to_numeric( data[ "original_cost" ], errors = "coerce" )
data[ "discount" ] = pd.to_numeric( data[ "discount" ], errors = "coerce" )
data[ "rating" ] = pd.to_numeric(data[ "rating" ], errors = "coerce" )

# Check datatypes after conversion
print( data.dtypes )

# Check if any nulls appeared after conversion
print( data[[ "sale_price", "original_cost", "discount", "rating" ]].isna().sum() )

# force everything to string
data[ "scraped_at" ] = data[ "scraped_at" ].astype( str ).str.strip()

# Convert safely
data[ "scraped_at" ] = pd.to_datetime(
    data[ "scraped_at" ],
    errors = "coerce"
)

# verify
print( data[ "scraped_at" ].dtype )
print( data[ "scraped_at"].isna().sum() )

# Convert sale_price to numeric
data[ "sale_price" ] = pd.to_numeric( data [ "sale_price" ], errors="coerce" )

# Treat zero or negative prices as invalid
data[ "sale_price" ] = data[ "sale_price" ].fillna( 0 )

data["screen_resolution" ] = (data["screen_resolution" ].fillna( "UNKNOWN" ) )

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


data = (
    data.sort_values( "scraped_at", ascending=False )
      .drop_duplicates(
          subset=[ "product_id", "scraped_at" ],
          keep="first"
      )
)




# Select only standardized columns
croma_standardized = data[
    [
        "platform",
        "product_id",
        "brand",
        "model_id",
        "full_name",
        "display_type",
        "sale_price",
        "original_cost",
        "discount",
        "rating",
        "stock_status",
        "scraped_at",
        "product_url",
        "image_url"
    ]
]

engine = create_engine(
    "mysql+pymysql://root:Kpkr%40153@localhost:3306/offerzone_project"
)

croma_standardized.to_sql(
    name="croma_tv_standardized",
    con=engine,
    if_exists="replace",
    index=False
)

print( "Croma standardized data stored successfully" )