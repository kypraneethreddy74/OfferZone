import pandas as pd
from sqlalchemy import create_engine

# Connect to the database
engine = create_engine(
    "mysql+pymysql://root:Kpkr%40153@localhost:3306/offerzone_project"
)

# Read latest platform level TV data
# This table already contains only latest prices

latest_tvs = pd.read_sql( "select * from tv_platform_latest_master", engine )

# Create brand presence summary
# This shows how string each brand is in the store

brand_master = (
    latest_tvs
    .groupby( "brand" )
    .agg(
        # Number of unique TV models
        total_models = ( "model_id", "nunique" ),

        # Total listings across platforms
        total_listings = ( "model_id", "count" ),

        in_stock_count = ( "stock_status", lambda x: ( x == "In Stock" ).sum() )

    )
    .reset_index()
)

# Save brand master table

brand_master.to_sql(
    "tv_brand_master",
    engine,
    if_exists = "replace",
    index = False

)

# Simple confirmation message
print( "tv_brand_master table created successfully" )
print( "Total brands:", len( brand_master ))

