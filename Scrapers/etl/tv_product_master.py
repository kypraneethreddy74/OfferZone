import pandas as pd
from sqlalchemy import create_engine

# Connect to the database
engine = create_engine(
    "mysql+pymysql://root:Kpkr%40153@localhost:3306/offerzone_project"
)

# Read unified TV data
# This table contains all TV records from all platforms

tvs = pd.read_sql( "select * from tvs_unified", engine )

# Select only product-related columns
# These columns describe the TV itself
tv_product_master = tvs[
    [
        "brand",
        "model_id",
        "full_name",
        "display_type"
    ]
]

# Remove duplicate products
# One row per brand + model id

tv_product_master = tv_product_master.drop_duplicates( subset= [ "brand", "model_id" ] )

# Save product master table to database

tv_product_master.to_sql(
    "tv_product_master",
    engine,
    if_exists="replace",
    index=False
)

# Simple confirmation message
print( "tv_product_master table created successfully" )
print( "Total unique products:", len( tv_product_master ))