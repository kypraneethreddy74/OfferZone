import pandas as pd
from db_connection import get_connection
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# --------------------------------------------------
# Database connection
# --------------------------------------------------
conn = get_connection()

# --------------------------------------------------
# VALID TV BRANDS
# --------------------------------------------------
VALID_TV_BRANDS = {
    "ACER", "ACERPURE", "AISEN", "AIWA", "AMAZONBASICS", "BLAUPUNKT", "BPL",
    "BUSH", "COOCAA", "COMPAQ", "CORNEA", "CROMA", "DAIWA", "DYANORA",
    "ELISTA", "GEEPAS", "HAIER", "HAIKAWA", "HISENSE", "HUIDI", "HYEON",
    "HYUNDAI", "IBELL", "IFFALCON", "IMPEX", "INFINIX", "INTEX", "ITEL",
    "JVC", "KARBONN", "KODAK", "LG", "LIMEBERRY", "LLOYD", "LUGOSI",
    "LUMIO", "MADURA", "MARQ", "MASHIVA", "METZ", "MI", "MICROMAX",
    "MITASHI", "MOTOROLA", "MTC", "NACSON", "NEXAVISION", "NIKASHI", "NU",
    "ONEPLUS", "ONIDA", "PANASONIC", "PHILIPS", "REALME", "REINTECH",
    "RELIANCE", "SAMSUNG", "SANSUI", "SANYO", "SEVISION", "SHARP", "SHINCO",
    "SKYWALL", "SKYLIVE", "SONY", "STARSHINE", "STUDYNLEARN", "TCL",
    "TG", "THOMSON", "TIVORA", "TOSHIBA", "TRUSENSE", "UNIMAX", "UNIBOOM",
    "UREN", "VASAP", "VIDEOCON", "VISTEK", "VU", "VW", "VZY", "WESTINGHOUSE",
    "WESTON", "WOBBLE", "WYBOR", "XIAOMI", "ZEBRONICS"
}

# --------------------------------------------------
# BRAND ALIASES (for normalization)
# --------------------------------------------------
BRAND_ALIASES = {
    
    "AISEN®": "AISEN",
    "acer": "ACER",
    "AISENÂ®": "AISEN",
    "BLACK & DECKER": "BLACK+DECKER",
    "BLACK+DECKER": "BLACK+DECKER",
}

# --------------------------------------------------
# Brand Normalization Function
# --------------------------------------------------
def normalize_brand(brand):
    """
    Normalize brand name:
    - Check aliases first
    - Then check if in valid brands
    - Otherwise return UNKNOWN
    """
    if pd.isna(brand) or brand is None:
        return "UNKNOWN"
    
    brand = str(brand).upper().strip()
    
    # Remove special characters
    brand = brand.replace("®", "").replace("Â", "").replace("™", "").strip()
    
    # Check aliases first
    if brand in BRAND_ALIASES:
        return BRAND_ALIASES[brand]
    
    # Check if valid brand
    if brand in VALID_TV_BRANDS:
        return brand
    
    return "UNKNOWN"

# --------------------------------------------------
# Read data from database
# --------------------------------------------------
data = pd.read_sql("SELECT * FROM amazon_tv", conn)

print(data.head())
print("\nNull values before cleaning:\n")
print(data.isna().sum())

# --------------------------------------------------
# NUMERIC CLEANING
# --------------------------------------------------

# Rating
data["rating"] = (
    pd.to_numeric(data["rating"], errors="coerce")
    .fillna(0)
)

# Rating count
data["rating_count"] = (
    pd.to_numeric(data["rating_count"], errors="coerce")
    .fillna(0)
)

# Sale price
data["sale_price"] = (
    pd.to_numeric(data["sale_price"], errors="coerce")
    .fillna(0)
    .astype(int)
)

# Original cost
data["original_cost"] = (
    pd.to_numeric(data["original_cost"], errors="coerce")
    .fillna(data["sale_price"])
    .astype(int)
)

# Discount
data["discount"] = (
    pd.to_numeric(data["discount"], errors="coerce")
    .fillna(0)
    .astype(int)
)

# --------------------------------------------------
# BRAND NORMALIZATION (NEW)
# --------------------------------------------------

# Store original brand for logging
data["brand_original"] = data["brand"]

# Normalize brand
data["brand"] = data["brand"].apply(normalize_brand)

# Log unknown brands for review
unknown_brands = data[data["brand"] == "UNKNOWN"]["brand_original"].unique()
print("\n⚠️ Unknown brands found:")
print(unknown_brands)
print(f"Total unknown brand records: {(data['brand'] == 'UNKNOWN').sum()}")

# Drop the temp column
data = data.drop(columns=["brand_original"])

# --------------------------------------------------
# TEXT CLEANING
# --------------------------------------------------

# Model ID
data["model_id"] = (
    data["model_id"]
    .fillna("UNKNOWN")
    .str.upper()
    .str.strip()
)

# Stock status normalization
data["stock_status"] = (
    data["stock_status"]
    .astype(str)
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

# Platform
data["platform"] = (
    data["platform"]
    .astype(str)
    .str.lower()
    .str.strip()
)

# --------------------------------------------------
# DATETIME CLEANING
# --------------------------------------------------

data["scraped_at"] = pd.to_datetime(
    data["scraped_at"],
    errors="coerce"
)

# --------------------------------------------------
# COLUMN NAME STANDARDIZATION
# --------------------------------------------------

data.columns = (
    data.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# --------------------------------------------------
# DUPLICATE CHECK
# --------------------------------------------------

duplicate_count = data.duplicated(subset=["product_id"]).sum()
print("\nDuplicate product_id count:", duplicate_count)

# Keep latest record per product per scrape time
data = (
    data.sort_values("scraped_at", ascending=False)
    .drop_duplicates(
        subset=["product_id", "scraped_at"],
        keep="first"
    )
)

# --------------------------------------------------
# FINAL CHECK
# --------------------------------------------------

print("\nNull values after cleaning:\n")
print(data.isna().sum())

print("\nData types:\n")
print(data.dtypes)

print("\n✅ Brand distribution after normalization:")
print(data["brand"].value_counts().head(20))

# --------------------------------------------------
# SELECT FINAL COLUMNS
# --------------------------------------------------

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

# --------------------------------------------------
# SAVE TO DATABASE
# --------------------------------------------------

engine = create_engine(
    "mysql+pymysql://root:Kpkr%40153@localhost:3306/offerzone_project"
)

data.to_sql(
    name="amazon_tv_standardized",
    con=engine,
    if_exists="replace",
    index=False
)

print("\n✅ Successfully standardized and saved to MySQL")