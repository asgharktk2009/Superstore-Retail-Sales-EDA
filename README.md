# Superstore Retail Sales EDA

Exploratory data analysis of retail sales data (2015-2018) using Python, Pandas and Seaborn.

## What I did
- Cleaned the data: found 806 extra rows from other Excel sheets, fixed 11 missing postal codes
- Analysed customer purchases, monthly seasonality, category revenue and discount impact

## Key findings
1. Discounts above 20% cause most of the losses (88.7% of all losses)
2. Furniture is 32% of sales but only 6% of profit
3. November and December are the biggest months (29.5% of yearly sales)
4. Sales grew 20-30% a year in 2017-2018, but profit margin stayed near 13%
5. The top 20% of customers give 48% of sales

## Files
- `eda_analysis.py` : the analysis code
- `superstore_sales.csv` : original data
- `superstore_clean.csv` : cleaned data

## How to run
    pip install pandas numpy matplotlib seaborn
    python eda_analysis.py
