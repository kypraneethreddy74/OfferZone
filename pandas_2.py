import pandas as pd

df = pd.read_csv( "customers.csv" )

print( df.loc[:7] )

print( df[[ "full_name", "age", "city" ]] )

print( df.sample(3) )

print( df.loc[10] )

print( df.iloc[5:13] )

print( df.loc[3:7, ["full_name", "phone" ]] )

print( df[df[ "age" ] > 50 ] )

print( df[df[ "city" ].isin( ["Chennai", "Hyderabad"] ) ] )

print( df[df[ "age" ].between( 25, 35 ) ] )

print( df[ "age" ].isnull.sum() )