import pandas as pd

df = pd.read_csv( "customers.csv" )

print( df.info )

def normalize_date(x):
    try:
        return pd.to_datetime(x, errors="raise")
    except:
        return pd.NaT

# Create new column without modifying original
df["creation_date_fixed"] = df["created_at"].apply(normalize_date)

print(df)

print(df.loc[16, "creation_date_fixed"])