import pandas as pd
from sqlalchemy import create_engine

# Connect to the database
engine = create_engine(
    "mysql+pymysql://root:Kpkr%40153@localhost:3306/offerzone_project"
)

# Read unified TV data
# This table contains data from all platforms and all scrape times

tvs = pd.read_sql( "select * from tvs_unified", engine )

# Sort data by scraped time
# This help us identify the latest price

tvs = tvs.sort_values( "scraped_at" )

# Keep only the latest record for each TV on each platform

tv_platform_latest_master = (
    tvs.groupby([ "brand", "model_id", "platform" ]).tail(1)
)

# Select only required columns for master table
tv_platform_latest_master = tv_platform_latest_master[
    [
        "brand",
        "model_id",
        "product_id",
        "full_name",
        "platform",
        "sale_price",
        "original_cost",
        "discount",
        "stock_status",
        "scraped_at",
        "product_url",
        "rating",
        "display_type",
        "image_url",
        "screen_resolution"
    ]
]

# Save the master table back to database
# This table will always contain latest prices

tv_platform_latest_master.to_sql(
    "tv_platform_latest_master",
    engine,
    if_exists = "replace",
    index = False
)

# Simple confirmation message

print("tv_platform_latest_master table created successfully" )
print( "Total rows:", len( tv_platform_latest_master ))

