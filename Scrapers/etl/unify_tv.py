import pandas as pd
from sqlalchemy import create_engine

# Database connection
engine = create_engine(
    "mysql+pymysql://root:Kpkr%40153@localhost:3306/offerzone_project"
)

# Read standardized tables
amazon = pd.read_sql( "select * from amazon_tv_standardized", engine )
flipkart = pd.read_sql( "select * from flipkart_tv_standardized", engine )
croma = pd.read_sql( "select * from croma_tv_standardized", engine )

# Verify schemas
print( amazon.columns )
print( flipkart.columns )
print( croma.columns )

# Unify tables
tvs_unified = pd.concat(
    [ amazon, flipkart, croma ],
    ignore_index = True
)

# Validate unified data
print( "Total unified rows:", len( tvs_unified ))
print( tvs_unified[ "platform" ].value_counts() )

# Save unified table back to DB
tvs_unified.to_sql(
    "tvs_unified",
    engine,
    if_exists = "replace",
    index = False
)

print( "Unification completed successfully" )