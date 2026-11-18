  #Exploratory Data Analysis (EDA)
#Task 1: Exploratory data Analysis (EDA) on Superstore Retails

#(1): Import Liabraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="whitegrid")

#(2):Now we load the CSV File 
raw=pd.read_csv("superstore_sales.csv",dtype=str)
print(raw.shape)
print(raw.head())

#dtype=str: reads every thing as text first. This is safer because the file is messy.

raw.isna().sum()
print(raw)

#(3): Find The Problem and split the file
is_order = raw["Row ID"].str.fullmatch(r"\d+")
orders = raw[is_order].copy()
returns = raw[raw["Row ID"] == "Yes"]
returned_ids = set(returns["Order ID"])
print(len(orders), len(returned_ids))
orders.isna().sum()[lambda s: s > 0]
print(raw)

#(4):Fix data types and the missing postal code
df = orders.copy()
for c in ["Sales", "Discount", "Profit"]:
    df[c] = pd.to_numeric(df[c])
df["Quantity"] = pd.to_numeric(df["Quantity"]).astype(int)
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")

# the 11 missing postal codes are all Burlington, Vermont
df["Postal Code"] = df["Postal Code"].fillna("05401")
df["Postal Code"] = df["Postal Code"].str.replace(r"\.0$", "", regex=True)

print(df.isna().sum().sum())   # should be 0

# (5):Add helpful columns
df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.month
df["Margin"] = df["Profit"] / df["Sales"]
df["Loss"] = df["Profit"] < 0
bins = [-0.001, 0, 0.10, 0.20, 0.30, 0.50, 1.0]
labels = ["0%", "1-10%", "11-20%", "21-30%", "31-50%", ">50%"]
df["Discount Band"] = pd.cut(df["Discount"], bins=bins, labels=labels)

print("Sales:", df["Sales"].sum().round())
print("Profit:", df["Profit"].sum().round())
print("Margin %:", (df["Profit"].sum() / df["Sales"].sum() * 100).round(1))

#(6):Customer purchase volume
cust = df.groupby("Customer Name").agg(
    Orders=("Order ID", "nunique"),
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum"),
).sort_values("Sales", ascending=False)

top20 = cust.head(int(len(cust) * 0.2))["Sales"].sum() / cust["Sales"].sum()
print("Top 20% customers give", round(top20 * 100, 1), "% of sales")
print("Customers losing money:", (cust["Profit"] < 0).sum())

sns.histplot(cust["Orders"], discrete=True)
plt.title("Orders per customer")
plt.show()
cust.head(10)

#(7):Monthly seasonality
monthly = df.groupby(df["Order Date"].dt.to_period("M"))["Sales"].sum()
monthly.plot(figsize=(10, 4), marker="o", title="Monthly sales")
plt.show()

# month x year table
table = df.groupby(["Month", "Year"])["Sales"].sum().unstack()
sns.heatmap(table / 1000, annot=True, fmt=".0f", cmap="YlOrRd")
plt.title("Sales by month and year ($k)")
plt.show()

# seasonal index: 1.0 = average month
index = (table / table.mean()).mean(axis=1)
print(index.round(2))

#(8):Category revenue
cat = df.groupby("Category")[["Sales", "Profit"]].sum()
cat["Margin %"] = cat["Profit"] / cat["Sales"] * 100
cat["Share of sales %"] = cat["Sales"] / cat["Sales"].sum() * 100
cat["Share of profit %"] = cat["Profit"] / cat["Profit"].sum() * 100
print(cat.round(1))

cat[["Sales", "Profit"]].plot(kind="bar", figsize=(7, 4))
plt.show()

sub = df.groupby("Sub-Category")[["Sales", "Profit"]].sum().sort_values("Profit")
sub["Profit"].plot(kind="barh", figsize=(7, 6), title="Profit by sub-category")
plt.show()

#(9):Discount sensitivity (the most important part)
d = df.groupby("Discount Band", observed=True).agg(
    Lines=("Row ID", "count"),
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum"),
    Loss_share=("Loss", "mean"),
)
d["Margin %"] = d["Profit"] / d["Sales"] * 100
print(d.round(1))

sns.barplot(x=d.index.astype(str), y=d["Margin %"])
plt.title("Profit margin by discount band")
plt.axhline(0, color="black")
plt.show()

print("Discount vs margin correlation:", df["Discount"].corr(df["Margin"]).round(2))
print("Discount vs quantity correlation:", df["Discount"].corr(df["Quantity"]).round(2))

#(10):Save your clean data
df.to_csv("superstore_clean.csv", index=False)