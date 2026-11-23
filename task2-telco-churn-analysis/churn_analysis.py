# =====================================================
# Customer Churn & Retention Analysis: Telco Dataset
# Data Analytics Project for Datheon
# Run:  python churn_analysis.py
# Needs: telco_customer_churn.csv in the same folder
# =====================================================
import pandas as pd              # tables (DataFrames)
import numpy as np               # numbers / arrays
import matplotlib.pyplot as plt  # charts
import seaborn as sns            # nicer charts + heatmaps

# -----------------------------------------------------
# STEP 1: Load and clean the data
# -----------------------------------------------------
df = pd.read_csv("telco_customer_churn.csv")
print("Shape:", df.shape)

# TotalCharges is text because 11 cells are blank -> convert to numbers.
# Those 11 customers have tenure = 0 (new, not billed yet), so we fill with 0.
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)

# Numeric churn flag: Yes = 1, No = 0 (average of this column = churn rate)
df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)
print("Missing values left:", df.isna().sum().sum())


# Helper: churn table for one column (count, churned, churn rate %)
# We use this function many times, so we write it only once.
def churn_table(data, column):
    t = data.groupby(column, observed=True)["ChurnFlag"].agg(["count", "sum", "mean"])
    t["mean"] = (t["mean"] * 100).round(2)
    t.columns = ["Customers", "Churned", "ChurnRate%"]
    return t


# -----------------------------------------------------
# STEP 2: Baseline churn rate
# -----------------------------------------------------
total_customers = len(df)
churned_customers = df["ChurnFlag"].sum()
churn_rate = churned_customers / total_customers * 100
print(f"\nTotal customers  : {total_customers}")
print(f"Churned customers: {churned_customers}")
print(f"Baseline churn rate: {churn_rate:.2f}%")

# -----------------------------------------------------
# STEP 3: Tenure cohorts and contract type
# -----------------------------------------------------
bins = [-1, 12, 24, 36, 48, 60, 72]          # -1 so that tenure = 0 is included
labels = ["0-12", "13-24", "25-36", "37-48", "49-60", "61-72"]
df["TenureCohort"] = pd.cut(df["tenure"], bins=bins, labels=labels)

cohort = churn_table(df, "TenureCohort")
contract = churn_table(df, "Contract")
print("\nChurn by tenure cohort:\n", cohort)
print("\nChurn by contract type:\n", contract)

cross = df.pivot_table(index="TenureCohort", columns="Contract",
                       values="ChurnFlag", aggfunc="mean", observed=True) * 100
print("\nChurn % by cohort and contract:\n", cross.round(2))

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sns.barplot(x=cohort.index, y=cohort["ChurnRate%"], ax=axes[0], color="steelblue")
axes[0].set_title("Churn Rate by Tenure Cohort")
axes[0].set_xlabel("Tenure (months)")
axes[0].set_ylabel("Churn rate (%)")
sns.barplot(x=contract.index, y=contract["ChurnRate%"], ax=axes[1], color="indianred")
axes[1].set_title("Churn Rate by Contract Type")
axes[1].set_xlabel("Contract")
axes[1].set_ylabel("Churn rate (%)")
plt.tight_layout()
plt.savefig("churn_by_cohort_contract.png", dpi=150)
plt.show()

# -----------------------------------------------------
# STEP 4: Payment method and monthly charges
# -----------------------------------------------------
pay = churn_table(df, "PaymentMethod").sort_values("ChurnRate%", ascending=False)
print("\nChurn by payment method:\n", pay)

charge_bins = [0, 30, 60, 90, 120]
charge_labels = ["$0-30", "$30-60", "$60-90", "$90-120"]
df["ChargeBand"] = pd.cut(df["MonthlyCharges"], bins=charge_bins, labels=charge_labels)
chg = churn_table(df, "ChargeBand")
print("\nChurn by monthly charges:\n", chg)


# -----------------------------------------------------
# STEP 5: Retention curves (Kaplan-Meier method)
# -----------------------------------------------------
# For each month t: look at customers still active at t ("at risk"),
# see what fraction left exactly at t, and multiply the survival fractions.
def retention_curve(data):
    months = np.arange(1, 73)
    survival = []
    s = 1.0                                   # start with 100% retained
    for t in months:
        at_risk = (data["tenure"] >= t).sum()
        churned_now = ((data["tenure"] == t) & (data["ChurnFlag"] == 1)).sum()
        if at_risk > 0:
            s = s * (1 - churned_now / at_risk)
        survival.append(s)
    return months, np.array(survival)


def plot_retention(column, title, filename):
    fig, ax = plt.subplots(figsize=(9, 5))
    for name, grp in df.groupby(column):
        m, s = retention_curve(grp)
        ax.plot(m, s * 100, label=name)
    ax.set_title(title)
    ax.set_xlabel("Tenure (months)")
    ax.set_ylabel("Customers retained (%)")
    ax.legend()
    plt.savefig(filename, dpi=150)
    plt.show()


plot_retention("Contract", "Retention Curve by Contract Type", "retention_curves.png")
plot_retention("PaymentMethod", "Retention Curve by Payment Method", "retention_by_payment.png")

# -----------------------------------------------------
# STEP 6: High-risk segments
# -----------------------------------------------------
# 6a: Fiber optic users WITHOUT tech support  (& means AND)
seg = df[(df["InternetService"] == "Fiber optic") & (df["TechSupport"] == "No")]
seg_rate = seg["ChurnFlag"].mean() * 100
rest_rate = df.drop(seg.index)["ChurnFlag"].mean() * 100
print(f"\nFiber optic + No TechSupport: {len(seg)} customers, churn {seg_rate:.2f}%")
print(f"All other customers churn: {rest_rate:.2f}%")

# 6b: find the riskiest combinations automatically
cols = ["Contract", "InternetService", "TechSupport", "PaymentMethod"]
risk = df.groupby(cols)["ChurnFlag"].agg(["count", "sum", "mean"]).reset_index()
risk.columns = cols + ["Customers", "Churned", "ChurnRate%"]
risk["ChurnRate%"] = (risk["ChurnRate%"] * 100).round(2)
risk = risk[risk["Customers"] >= 50]          # ignore tiny segments
risk = risk.sort_values("ChurnRate%", ascending=False)
print("\nTop 8 high-risk segments:")
print(risk.head(8).to_string(index=False))
risk.to_csv("high_risk_segments.csv", index=False)   # open in Excel / Power BI

# -----------------------------------------------------
# STEP 7: Churn heatmaps
# -----------------------------------------------------
heat1 = df.pivot_table(index="InternetService", columns="Contract",
                       values="ChurnFlag", aggfunc="mean") * 100
internet_users = df[df["InternetService"] != "No"]
heat2 = internet_users.pivot_table(index="TechSupport", columns="InternetService",
                                   values="ChurnFlag", aggfunc="mean") * 100

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.heatmap(heat1, annot=True, fmt=".1f", cmap="Reds", ax=axes[0],
            cbar_kws={"label": "Churn rate (%)"})
axes[0].set_title("Churn % by Internet Service and Contract")
sns.heatmap(heat2, annot=True, fmt=".1f", cmap="Reds", ax=axes[1],
            cbar_kws={"label": "Churn rate (%)"})
axes[1].set_title("Churn % by Tech Support and Internet Service")
plt.tight_layout()
plt.savefig("churn_heatmap.png", dpi=150)
plt.show()

# -----------------------------------------------------
# STEP 8: Final summary (printed from the real numbers)
# -----------------------------------------------------
# The single riskiest segment from step 6b is the first row of "risk"
top = risk.iloc[0]
share_of_all_churn = top["Churned"] / churned_customers * 100

print("\n" + "=" * 50)
print("FINAL SUMMARY")
print("=" * 50)
print(f"1. Overall churn rate: {churn_rate:.1f}% ({churned_customers} of {total_customers})")
print(f"2. First-year customers churn at {cohort.loc['0-12', 'ChurnRate%']}%, "
      f"customers beyond 5 years at {cohort.loc['61-72', 'ChurnRate%']}%")
print(f"3. Month-to-month churn {contract.loc['Month-to-month', 'ChurnRate%']}% "
      f"vs two-year {contract.loc['Two year', 'ChurnRate%']}%")
print(f"4. Electronic check churn {pay.loc['Electronic check', 'ChurnRate%']}% "
      f"vs credit card (automatic) {pay.loc['Credit card (automatic)', 'ChurnRate%']}%")
print(f"5. Riskiest segment: {top['Contract']} + {top['InternetService']} + "
      f"TechSupport={top['TechSupport']} + {top['PaymentMethod']}")
print(f"   {int(top['Customers'])} customers, churn {top['ChurnRate%']}%, "
      f"= {share_of_all_churn:.1f}% of ALL churn")
