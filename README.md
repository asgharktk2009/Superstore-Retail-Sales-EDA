# Superstore Retail Sales: Exploratory Data Analysis (EDA)

> **Internship project at Datheon.**
> This analysis was completed as part of my Data Analytics Internship at **Datheon**.

## 1. Project Overview

This project studies four years of retail sales data (January 2015 to December 2018) from a US superstore. The goal is to clean the data, understand how sales are spread, and find what helps or hurts profit.

**Business questions I answered**
1. How do customers buy, and who brings the most sales?
2. Which months are strong and which are weak (seasonality)?
3. Which product categories bring the most revenue and profit?
4. How do discounts change profit?

## 2. Dataset

| Item | Detail |
|---|---|
| Source | Superstore sample sales dataset (public) |
| Period | 3 Jan 2015 to 30 Dec 2018 |
| Order lines | 9,994 |
| Orders | 5,009 |
| Customers | 793 |
| Products | 1,862 |
| Columns | 21 (order, customer, location, product, sales, quantity, discount, profit) |

**Headline numbers:** Sales $2.30M, Profit $286K, Profit margin 12.5%.

## 3. Data Wrangling and Missing-Value Check

| Problem found | What I did |
|---|---|
| The file had 10,800 rows, but only 9,994 were real orders. The other **806 rows came from two extra Excel sheets** (a Returns list and a Managers list) pasted below the orders. They made it look like 6.8% of the data was missing. | Split them into separate tables and kept only the orders |
| **11 missing postal codes** (all in Burlington, Vermont) | Filled with the correct code, 05401 |
| Dates were stored as text | Converted to real dates |
| Postal codes were stored as decimals | Converted to 5-digit text |
| Checked for duplicates, negative sales, and ship dates before order dates | None found, apart from one repeated line in a single order (kept) |

After cleaning there are **0 missing values**.

## 4. Key Findings

### Discounts
- Orders with **0% discount earn a 29.5% margin**. Orders with 11-20% discount still earn 11.6%.
- **Every discount above 20% loses money:** 21-30% = -10.0%, 31-50% = -24.8%, above 50% = -119.2%.
- Discounts above 20% are only **15.8% of sales** but cause **88.7% of all losses** (-$135K).
- Bigger discounts did **not** make customers buy more. The average quantity per order stays about the same at every discount level.

### Product categories
| Category | Share of sales | Share of profit | Margin |
|---|---|---|---|
| Technology | 36.4% | 50.8% | 17.4% |
| Office Supplies | 31.3% | 42.8% | 17.0% |
| Furniture | 32.3% | 6.4% | 2.5% |

- **Tables** (-$17.7K) and **Bookcases** (-$3.5K) lose money overall.
- **Copiers** make the most profit ($55.6K). **Paper, Labels and Envelopes** have the best margins (42-44%).

### Seasonality
- **November, December and September** are the strongest months. **January and February** are the weakest.
- November and December alone are **29.5% of yearly sales**. The busiest month is about 6 times stronger than the weakest.
- November has a lower margin (10.1%) than October (15.9%). Busy months are not always the most profitable.

### Growth
- Sales: 2015 $484K, 2016 $471K (-2.8%), 2017 $609K (+29.5%), 2018 $733K (+20.4%).
- Profit margin rose from 10.2% in 2015 to about 13% in 2016-2018, then stayed flat.

### Customers
- Almost every customer buys again (98.5%). The middle customer placed 6 orders.
- The **top 20% of customers give 48.1% of sales.**
- Some of the biggest customers lose money: the top customer by sales ($25K) has a net loss of $2K. In total, 155 of 793 customers are unprofitable.

### Regions
- West has the best margin (14.9%). Central has the lowest (7.9%).
- Texas, Ohio, Pennsylvania and Illinois are all loss-making states.

## 5. Recommendations

1. **Limit discounts to 20%**, or ask for manager approval above it. This would remove most of the losses.
2. **Review prices for Tables and Bookcases**, which lose money even before discounts are
   
