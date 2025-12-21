import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("shopping.csv")

data = df.groupby("Gender")["Purchase Amount (USD)"].mean()

plt.bar(data.index, data.values)
plt.xlabel("Gender")
plt.ylabel("Average Purchase Amount")
plt.title("Average Purchase Amount by Gender")
plt.show()

plt.hist(df["Purchase Amount (USD)"], bins=10)
plt.xlabel("Purchase Amount")
plt.ylabel("Frequency")
plt.title("Purchase Amount Distribution")
plt.show()

plt.scatter(df["Age"], df["Purchase Amount (USD)"])
plt.xlabel("Age")
plt.ylabel("Purchase Amount")
plt.title("Age vs Purchase Amount")
plt.show()

payment_counts = df["Payment Method"].value_counts()

plt.pie(payment_counts.values, labels=payment_counts.index, autopct="%1.1f%%")
plt.title("Payment Method Distribution")
plt.show()
