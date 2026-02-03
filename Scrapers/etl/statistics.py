import pandas as pd
from sqlalchemy import create_engine

# Connect to the database
engine = create_engine(
    "mysql+pymysql://root:Kpkr%40153@localhost:3306/offerzone_project"
)

# Load all masters tables 
tv_prices = pd.read_sql( "select * from tv_platform_latest_master", engine )

tv_products = pd.read_sql( "select * from tv_product_master", engine )

tv_brand = pd.read_sql( "select * from tv_brand_master", engine )

tv_platform = pd.read_sql( "select * from tv_platform_master", engine )

print( "All master tables loaded successfully" )

# Check numeric columns for all master tables

print( "------------------price table----------------------" )
print( tv_prices.select_dtypes( include = "number" ).columns )
print( "---------------------------------------------------" )

print( "------------------product table----------------------" )
print( tv_products.select_dtypes( include = "number" ).columns )
print( "-----------------------------------------------------" )

print( "-----------------brand table----------------------" )
print( tv_brand.select_dtypes( include = "number" ).columns )
print( "--------------------------------------------------" )

print( "----------------platform table-----------------------")
print( tv_platform.select_dtypes(include = "number" ).columns )
print( "----------------------------------------------------" )

# Mean data

# Mean of sale price

print( "----------mean of sale price -----------------------" )
print( tv_prices[ "sale_price" ].mean() )
print( "--------------------------------------------" )

# Mean of original cost

print( "-------------original cost-----------------" )
print( tv_prices[ "original_cost" ].mean() )
print( "-------------------------------------" )

# Mean of dicount

print( "------------------discount-----------------" )
print( tv_prices[ "discount" ].mean() )
print( "-------------------------------------" )

# Mean of rating

print("---------------Rating--------------" )
print( tv_prices[ "rating" ].mean() )
print( "----------------------------------" )

# Mean of total models

print( "---------------total_models------------" )
print( tv_brand[ "total_models" ].mean() )
print( "----------------------------------------" )

# Mean of total listings

print( "--------------total listings----------------" )
print(tv_brand[ "total_listings" ].mean() )
print( "--------------------------------------" )

# Mean of unique models

print( "-----------unique models-----------------" )
print(tv_platform[ "unique_models" ].mean() )
print( "-----------------------------------" )


# Median Data

# Median of sale price

print( "-----------median of sale price------------" )
print( tv_prices[ "sale_price" ].median() ) 
print( "---------------------------------------------" )

# Median of original cost

print( "-------------median of original cost------------------" )
print( tv_prices[ "original_cost" ].median() )
print( "------------------------------------------------------" )

# Median of discount

print( "-------------median of discount-----------------" )
print( tv_prices[ "discount" ].median() )
print( "-------------------------------------------------" )

# Median of rating

print( "-------------------median of rating---------------------" )
print( tv_prices[ "rating" ].median() )
print( "----------------------------------------------" )

# Median of total models

print( "--------------median of total models-------------" )
print( tv_brand[ "total_models" ].median() )
print( "--------------------------------------------" )

# Median of total listings

print( "-------------toatl listings------------------" )
print( tv_brand[ "total_listings" ].median() )
print( "--------------------------------------" )

# Median of unique models

print( "----------------unique models---------------------" )
print( tv_platform[ "unique_models" ].median() )
print( "---------------------------------------" )

# Mode Data

# Mode of sale price
print( "---------------mode of sale price--------------" )
print( tv_prices[ "sale_price" ].mode() )
print( "-------------------------------------------" )

# Mode of original cost

print( "-----------------mode of original cost--------------" )
print( tv_prices[ "original_cost" ].mode() )
print( "----------------------------------------------" )

# Mode of discount

print( "------------------mode of discount------------------" )
print( tv_prices[ "discount" ]. mode() )
print( "--------------------------------------------" )

# Mode of rating

print( "------------------mode of rating-----------------" )
print( tv_prices[ "rating" ].mode() )
print( "-----------------------------------------" )

# Mode of total models

print( "-------------mode of total models----------------" )
print( tv_brand[ "total_models" ].mode() )
print( "-----------------------------------------------" )

# Mode of total listings

print( "-------------total listings-------------------" )
print( tv_brand[ "total_listings" ].mode() )
print( "-----------------------------------------" )

# Mode of unique models

print( "-------------mode of unique models---------" )
print( tv_platform[ "unique_models" ].mode() )
print( "-----------------------------------------" )


print( "------------------price table----------------------" )
print( tv_prices.select_dtypes( include = "object" ).columns )
print( "---------------------------------------------------" )

print( "------------------product table----------------------" )
print( tv_products.select_dtypes( include = "object" ).columns )
print( "-----------------------------------------------------" )

print( "-----------------brand table----------------------" )
print( tv_brand.select_dtypes( include = "object" ).columns )
print( "--------------------------------------------------" )

print( "----------------platform table-----------------------")
print( tv_platform.select_dtypes(include = "object" ).columns )
print( "----------------------------------------------------" )

# Mode of brand

print( "-------------mode of brand------------------" )
print( tv_prices[ "brand" ].mode() )
print( "----------------------------------------------" )

# Mode of model id

print( "----------mode of model id------------" )
print( tv_prices[ "model_id" ].mode() )
print( "----------------------------------" )

# Mode of full name

print( "-----------mode of full name----------------" )
print( tv_prices[ "full_name" ].mode() )
print( "-------------------------------------------" )

# Mode of platform

print( "---------mode of platform----------------" )
print( tv_prices[ "platform" ].mode() )
print( "----------------------------------------" )

# Mode of stock status

print( "---------mode of stock status--------------" )
print( tv_prices[ "stock_status" ].mode() )
print( "------------------------------------" )

# Mode of product URL

print( "------------mode of product URL---------------" )
print( tv_prices[ "product_url" ].mode() )
print( "------------------------------------------" )

# Mode of display type

print( "------------mode of display type-----------------" )
print( tv_prices[ "display_type" ].mode() )
print( "-------------------------------------------" )

# Standard deviation

# Sale Price

print( "----------std sale price------------" )
print( tv_prices[ "sale_price" ].std() )
print( "------------------------------------" )

# original cost

print( "---------std original cost---------------" )
print( tv_prices[ "original_cost" ].std() )
print( "-----------------------------------" )

# Discount

print( "----------std discount---------------" )
print( tv_prices[ "discount" ].std() )
print( "--------------------------------------" )

# Rating

print( "-----------std rating----------------" )
print( tv_prices[ "rating" ].std() )
print( "-----------------------------------" )

# Interquartile range(IQR)

# Sale price

print( "------------------q1 of sale price-----------------" )
q1 = tv_prices[ "sale_price" ].quantile( 0.25 )
print( q1 )
print( "-------------------------------------" )

print( "--------------------q2 of sale price------------------" )
q2 = tv_prices[ "sale_price" ].quantile( 0.50 )
print( q2 )
print( "---------------------------------------" )

print( "----------------------q3 of sale price----------------------" )
q3 = tv_prices[ "sale_price" ].quantile( 0.75 )
print( q3 )
print( "-----------------------------------------" )

# print IQR
print( "----------------------IQR of sale price------------" )
IQR = q3 - q1
print( IQR )
print( "------------------------------------" )

# Here check outliers

print( "---------------check outliers---------------" )
lower =  max( 0, q1 - 1.5 * IQR )
print( lower )
upper_sale_price = q3 + 1.5 * IQR 
print( upper_sale_price )

print( "-----------------------------------------------" )

# Original cost

print( "------------------q1 of original cost-----------------" )
q1 = tv_prices[ "original_cost" ].quantile( 0.25 )
print( q1 )
print( "-------------------------------------" )

print( "--------------------q2 of original cost------------------" )
q2 = tv_prices[ "original_cost" ].quantile( 0.50 )
print( q2 )
print( "---------------------------------------" )

print( "----------------------q3 of original cost----------------------" )
q3 = tv_prices[ "original_cost" ].quantile( 0.75 )
print( q3 )
print( "-----------------------------------------" )

# print IQR
print( "----------------------IQR of original cost------------" )
IQR = q3 - q1
print( IQR )
print( "------------------------------------" )

# Here check outliers

print( "---------------check outliers---------------" )
lower = max( 0, q1 - 1.5 * IQR )
print( lower )
upper_original_cost = q3 + 1.5 * IQR 
print( upper_original_cost )

print( "-----------------------------------------------" )

# Discount

print( "------------------q1 of discount-----------------" )
q1 = tv_prices[ "discount" ].quantile( 0.25 )
print( q1 )
print( "-------------------------------------" )

print( "--------------------q2 of discount------------------" )
q2 = tv_prices[ "discount" ].quantile( 0.50 )
print( q2 )
print( "---------------------------------------" )

print( "----------------------q3 of discount----------------------" )
q3 = tv_prices[ "sale_price" ].quantile( 0.75 )
print( q3 )
print( "-----------------------------------------" )

# print IQR
print( "----------------------IQR of discount------------" )
IQR = q3 - q1
print( IQR )
print( "------------------------------------" )

# Here check outliers

print( "---------------check outliers---------------" )
lower =  max( 0, q1 - 1.5 * IQR )
print( lower )
upper_discount = q3 + 1.5 * IQR 
print( upper_discount )

print( "-----------------------------------------------" )

# Rating

print( "------------------q1 of rating-----------------" )
q1 = tv_prices[ "rating" ].quantile( 0.25 )
print( q1 )
print( "-------------------------------------" )

print( "--------------------q2 of rating------------------" )
q2 = tv_prices[ "rating" ].quantile( 0.50 )
print( q2 )
print( "---------------------------------------" )

print( "----------------------q3 of rating----------------------" )
q3 = tv_prices[ "rating" ].quantile( 0.75 )
print( q3 )
print( "-----------------------------------------" )

# print IQR
print( "----------------------IQR of rating------------" )
IQR = q3 - q1
print( IQR )
print( "------------------------------------" )

# Here check outliers

print( "---------------check outliers---------------" )
lower =  max( 0, q1 - 1.5 * IQR )
print( lower )
upper_rating = q3 + 1.5 * IQR 
print( upper_rating )

print( "-----------------------------------------------" )


# Total models
print( "------------------q1 of total models-----------------" )
q1 = tv_brand[ "total_models" ].quantile( 0.25 )
print( q1 )
print( "-------------------------------------" )

print( "--------------------q2 of total models------------------" )
q2 = tv_brand[ "total_models" ].quantile( 0.50 )
print( q2 )
print( "---------------------------------------" )

print( "----------------------q3 of total models----------------------" )
q3 = tv_brand[ "total_models" ].quantile( 0.75 )
print( q3 )
print( "-----------------------------------------" )

# print IQR
print( "----------------------IQR of total models------------" )
IQR = q3 - q1
print( IQR )
print( "------------------------------------" )

# Here check outliers

print( "---------------check outliers---------------" )
lower =  max( 0, q1 - 1.5 * IQR ) 
print( lower )
upper_total_models = q3 + 1.5 * IQR 
print( upper_total_models )

print( "-----------------------------------------------" )

# Total listings
print( "------------------q1 of total listings-----------------" )
q1 = tv_brand[ "total_listings" ].quantile( 0.25 )
print( q1 )
print( "-------------------------------------" )

print( "--------------------q2 of total listings------------------" )
q2 = tv_brand[ "total_listings" ].quantile( 0.50 )
print( q2 )
print( "---------------------------------------" )

print( "----------------------q3 of total listings----------------------" )
q3 = tv_brand[ "total_listings" ].quantile( 0.75 )
print( q3 )
print( "-----------------------------------------" )

# print IQR
print( "----------------------IQR of total listings------------" )
IQR = q3 - q1
print( IQR )
print( "------------------------------------" )

# Here check outliers

print( "---------------check outliers---------------" )
lower =  max( 0, q1 - 1.5 * IQR ) 
print( lower )
upper_total_listings = q3 + 1.5 * IQR 
print( upper_total_listings )

print( "-----------------------------------------------" )

# Unique models

print( "------------------q1 of unique models-----------------" )
q1 = tv_platform[ "unique_models" ].quantile( 0.25 )
print( q1 )
print( "-------------------------------------" )

print( "--------------------q2 of unique models------------------" )
q2 = tv_platform[ "unique_models" ].quantile( 0.50 )
print( q2 )
print( "---------------------------------------" )

print( "----------------------q3 of unique models----------------------" )
q3 = tv_platform[ "unique_models" ].quantile( 0.75 )
print( q3 )
print( "-----------------------------------------" )

# print IQR
print( "----------------------IQR of unique models------------" )
IQR = q3 - q1
print( IQR )
print( "------------------------------------" )

print( "-------------check outliers----------------" )
lower =  max(0, q1 - 1.5 * IQR )
print( lower )
upper_unique_models = q3 + 1.5 * IQR 
print( upper_unique_models )
print( "---------------------------------------" )


# here we copy the data
tv_prices_clean = tv_prices.copy() 
print( tv_prices_clean )

# sale price

tv_prices_clean = tv_prices_clean[
    ( tv_prices_clean[ "sale_price" ] >= 0 ) &
    ( tv_prices_clean[ "sale_price" ] <= upper_sale_price )
]

# Original cost

tv_prices_clean = tv_prices_clean[
    ( tv_prices_clean[ "original_cost" ] >= 0 ) &
    ( tv_prices_clean[ "original_cost" ] <= upper_original_cost )
]

# Discount

tv_prices_clean = tv_prices_clean[
    ( tv_prices_clean[ "discount" ] >= 0 ) &
    ( tv_prices_clean[ "discount" ] <= 100 )
]

# Rating

tv_prices_clean = tv_prices_clean[
    ( tv_prices_clean[ "rating" ] >=0 ) &
    ( tv_prices_clean[ "rating" ] <= 5 )
]

# Here we copy the data
tv_platform_clean = tv_platform.copy()
print( tv_platform_clean )

# Unique models

tv_platform_clean = tv_platform_clean[
     tv_platform_clean[ "unique_models" ] >= 0 
    
]

# Total listings

tv_platform_clean = tv_platform_clean[
     tv_platform_clean[ "total_listings" ] >= 0 
    
]

# In stock count

tv_platform_clean = tv_platform_clean[
    tv_platform_clean[ "in_stock_count" ] >= 0
]



# Here we copy the data

tv_brand_clean = tv_brand.copy()
print( tv_brand_clean )

# Total Models

tv_brand_clean = tv_brand_clean[
    ( tv_brand_clean[ "total_models" ] >= 0 ) &
    ( tv_brand_clean[ "total_models" ] <= upper_total_models )
]


print( "---------------------------------------------------" )
print( "Before cleaning:", tv_prices.shape )
print( "After cleaning:", tv_prices_clean.shape )

print( "Platform before:", tv_platform.shape )
print( "Platform after:", tv_platform_clean.shape )

print( "Brand before:", tv_brand.shape )
print( "Brand after:", tv_brand_clean.shape )

print( "-------------------------------------------------------------" )


# Subsets

# 1. High Discount TVS

print( "------------High Discount--------------------" )
high_discount_tvs = tv_prices_clean[
    tv_prices_clean[ "discount" ] >= 20
]

print( high_discount_tvs.shape )
print( "----------------------------------------------" )

# 2. Highly Rated TVs

print( "----------High Rating---------------------" )
high_rating_tvs = tv_prices_clean[
    tv_prices_clean[ "rating" ] >= 4
]

print( high_rating_tvs.shape )
print( "-------------------------------------------" )

# 3. Budget TVs

print( "------------------Budget TVs--------------------" )
median_price = tv_prices_clean[ "sale_price" ].median()

budget_tvs = tv_prices_clean[
    tv_prices_clean[ "sale_price" ] < median_price
]

print( budget_tvs.shape )
print( "---------------------------------------" )

# Premimum TVs

print( "-------------Premimum TVS-----------------------" )

premimum_tvs = tv_prices_clean[
    tv_prices_clean[ "sale_price" ] > 50000
]

print( premimum_tvs.shape )
print( "----------------------------------" )

# Best value TVs( High discount + high rating )

print( "-----------Best Value TVs-------------------" )

best_value_tvs = tv_prices_clean[
    ( tv_prices_clean[ "discount" ] >= 20 ) &
    ( tv_prices_clean[ "rating" ] >= 4 )
]

print( best_value_tvs.shape )
print( "-------------------------------------------" )

# Platform with high stock

print( "------------platform with stock-----------------" )

high_stock_platforms = tv_platform_clean[
    tv_platform_clean[ "in_stock_count" ] > 200
]

print( high_stock_platforms )

# Brands with many models

print( "----------Brands with many models--------------" )

top_brands = tv_brand_clean[
    tv_brand_clean[ "total_models" ] >=20
]

print( top_brands.shape )
print( "----------------------------------" )

print( "High discount TVS: ", high_discount_tvs.shape )
print( "High rating TVs: ", high_rating_tvs.shape )
print( "Best value TVs: ", best_value_tvs.shape )


# Group By

# 1. Brand wise total TVs and average rating

print( "---------------------------------------" )
brand_price_analysis = (
    tv_prices_clean
    .groupby( "brand" )
    .agg(
        total_tvs = ( "brand", "count" ),
        avg_reviews = ( "rating", "mean" )
    )
    .reset_index()
)
print( brand_price_analysis.head() )
print( "-------------------------------------" )

# 2. Brand wise price analysis

print( "-----------------brand price analysis-----------------------------" )

brand_price_analysis = (
    tv_prices_clean
    .groupby( "brand" )
    .agg(
        avag_sale_price = ( "sale_price", "mean" ),
        median_sale_price = ( "sale_price", "median" )
    )
    .reset_index()
)
print( brand_price_analysis.head() )   
print( "----------------------------------------------" )

# 3. Platform wise analysis

print( "---------------market wise analysis--------------" )

platform_analysis = (
    tv_platform_clean
    .groupby( "platform" )
    .agg(
        total_models = ( "unique_models", "sum" ),
        total_listings = ( "total_listings", "sum" ),
        total_in_stock = ( "in_stock_count", "sum" )
    )
    .reset_index()
)

print( platform_analysis )
print( "-------------------------------------------" )

# Discount based grouping

print( "--------------Discount based-----------------" )

discount_analysis = (
    tv_prices_clean
    .groupby( "brand" )
    .agg(
        avg_discount = ( "discount", "mean" )
    )
    .reset_index()
    
)
print( discount_analysis.head() )
print( "----------------------------------" )

# 5. Best values TVs

print( "--------------best value TVs-------------------" )

best_value_tvs = tv_prices_clean[
    ( tv_prices_clean[ "discount" ] >= 20 ) &
    ( tv_prices_clean[ "rating" ] >= 4 )
]

best_value_brand_analysis = (
    best_value_tvs
    .groupby( "brand" )
    .agg(
        total_tvs = ( "brand", "count" ),
        avg_rating = ( "rating", "mean" )

    )
    .reset_index()
)

print( best_value_brand_analysis.head() )
print( "-----------------------------------------" )


# select numeric columns

numeric_cols = [
    "sale_price",
    "original_cost",
    "discount",
    "rating"
]

# calculate covariance matrix

price_covariance = tv_prices_clean[ numeric_cols].cov()

print( "-------- covariance matrix---------" )
print( price_covariance )
print( "----------------------------------------" )

# calculate correlation matrix

price_correlation = tv_prices_clean[ numeric_cols ].corr()

print( "----- correlation matrix-------" )
print( price_correlation )
print( "----------------------------------------" )

# sale price vs original cost

print( "-----correlation sale price vs original cost------" )
print( tv_prices_clean[ "sale_price" ].corr( tv_prices_clean[ "original_cost" ]))
print( "----------------------------------------------------" )

# sale price vs discount

print( "------correlation sale price vs discount--------------" )
print( tv_prices_clean[ "sale_price" ].corr( tv_prices_clean[ "discount" ]))
print( "------------------------------------" )

# Sale price vs rating

print( "------correlation of sale price vs rating----------" )
print( tv_prices_clean[ "sale_price" ].corr( tv_prices_clean[ "rating" ]))
print( "-------------------------------------------" )

# original cost vs discount

print( "--------correlation of original cost vs discount---------")
print( tv_prices_clean[ "original_cost" ].corr( tv_prices_clean[ "discount" ]))
print( "-----------------------------------------" )

# original cost vs rating

print( "-----------correlation of original cost vs rating-------------" )
print( tv_prices_clean["original_cost" ].corr( tv_prices_clean[ "rating" ]))
print( "-------------------------------------------" )

# discount vs rating

print( "----------correlation of discount vs rating----------------" )
print( tv_prices_clean[ "discount" ].corr( tv_prices_clean[ "rating" ]))
print( "--------------------------------------------------" )

# Covariance graph

import matplotlib.pyplot as plt
import numpy as np


cov_matrix = tv_prices_clean[ numeric_cols].cov()

plt.figure(figsize = (6, 5))
plt.imshow( cov_matrix )
plt.title( "covariance matrix" )
plt.xticks( range( len( numeric_cols )), numeric_cols, rotation = 45 )
plt.yticks( range( len( numeric_cols )), numeric_cols )
plt.colorbar()

# Display values
for i in range( len( numeric_cols )):
    for j in range( len( numeric_cols)):
        plt.text( j, i, f"{ cov_matrix.iloc[ i, j ]:.1e}",
                 ha = "center", va = "center", color = "black" )
                 
plt.tight_layout()
plt.show()

# Correlation graph

corr_matrix = tv_prices[ numeric_cols ].corr()

plt.figure( figsize = ( 6, 5 ))
plt.imshow( corr_matrix )
plt.title( "correlation matrix")
plt.xticks( range( len( numeric_cols)), numeric_cols, rotation = 45 )
plt.yticks( range( len( numeric_cols)), numeric_cols )
plt.colorbar()

# Display values inside cells
for i in range( len( numeric_cols )):
    for j in range( len( numeric_cols)):
        plt.text( j, i, f"{ corr_matrix.iloc[ i, j]:.2f}",
                 ha = "center", va = "center", color = "black" )
plt.tight_layout()
plt.show()

# Skewness

skew_values = tv_prices_clean[ numeric_cols].skew()
print( "skewness values: " )
print( skew_values )

# Visualize skewness

# Sale price

plt.figure(figsize = ( 8, 5))
plt.hist( tv_prices_clean[ "sale_price" ], bins = 50, edgecolor = "black" )
plt.title( "Distribution of sale price" )
plt.xlabel( "sale price" )
plt.ylabel( "count of TVs" )
plt.show()

# original cost

plt.figure( figsize = ( 8, 5 ))
plt.hist( tv_prices_clean[ "original_cost" ], bins = 50, edgecolor = "black" )
plt.title( "Distribution of original cost" )
plt.xlabel( "original cost" )
plt.ylabel( "count of TVs" )
plt.show()

# Discount 

plt.figure( figsize = ( 8, 5 ))
plt.hist( tv_prices_clean[ "discount" ], bins = 30, edgecolor = "black" )
plt.title( "Distribution of discount" )
plt.xlabel( "discount" )
plt.ylabel( "count of TVs" )
plt.show()

# rating

plt.figure( figsize = ( 8, 5 ))
plt.hist( tv_prices_clean[ "rating" ], bins = 10, edgecolor = "black" )
plt.title( "Distribution of rating" )
plt.xlabel( "rating" )
plt.ylabel( "count of TVs" )
plt.show()


