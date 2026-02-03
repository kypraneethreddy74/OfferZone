import subprocess
import sys

files = [
    "db_connection.py",

    "croma_std.py",
    "flipkart_std.py",
    "amazon_std.py",
    "unify_tv.py",

    "tv_brand_master.py",
    "tv_platform_master.py",
    "tv_product_master.py",
    "tv_price_master.py",

    
    "tv_analytics.py"

    
]

for f in files:
    print(f"\n Running {f}")
    result = subprocess.run([sys.executable, f])

    if result.returncode != 0:
        print(f" Failed at {f}. Stopping pipeline.")
        break
    else:
        print(f" {f} completed")

print("\n ETL Pipeline Finished")
