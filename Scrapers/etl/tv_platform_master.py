import pandas as pd
from sqlalchemy import create_engine

# Connect to the database
engine = create_engine(
    "mysql+pymysql://root:Kpkr%40153@localhost:3306/offerzone_project"
)

# Read latest platform level TV data
# This table contains only latest records

latest_tvs = pd.read_sql( "select * from tv_platform_latest_master", engine )

# Create platform Summary
# One row per platform

platform_master = (
    latest_tvs
    .groupby( "platform" )
    .agg(

        # Total TVs listed
        total_listings = ( "model_id", "count" ),

        # Unique TV models
        unique_models = ( "model_id", "nunique" ),

        in_stock_count=(
    "stock_status",
    lambda x: (
        x.fillna("")
         .astype(str)
         .str.strip()
         .str.lower()
         .eq("in_stock")
         .sum()
    )
)
    )
    .reset_index()
)

# Save platform summary master table
platform_master.to_sql(
    "tv_platform_master",
    engine,
    if_exists = "replace",
    index = False
)

# Simple confirmation message
print( "platform_master table created successfully" )
print( "Total platforms:", len( platform_master ))
