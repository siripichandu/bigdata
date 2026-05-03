"""
data_cleaning.py
Standalone Silver Layer cleaning pipeline.
Can be run independently or imported by the notebook.
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime


# ── Helpers ────────────────────────────────────────────────────────────────────

def age_to_months(age_str):
    """Convert age string like '2 years', '4 weeks' to float months."""
    if pd.isna(age_str):
        return np.nan
    age_str = str(age_str).lower().strip()
    match = re.match(r"(\d+)\s*(year|month|week|day)", age_str)
    if not match:
        return np.nan
    val, unit = int(match.group(1)), match.group(2)
    return val * {"year": 12, "month": 1, "week": 0.25, "day": 1 / 30}[unit]


def report_quality(df, name):
    """Print a data quality summary."""
    print(f"\n{'='*55}")
    print(f"  DATA QUALITY REPORT — {name.upper()}")
    print(f"{'='*55}")
    print(f"  Rows      : {len(df):,}")
    print(f"  Columns   : {df.shape[1]}")
    print(f"  Duplicates: {df.duplicated().sum():,}")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing):
        print(f"\n  Missing values:")
        for col, cnt in missing.items():
            pct = cnt / len(df) * 100
            print(f"    {col:<35} {cnt:>6,}  ({pct:.1f}%)")
    else:
        print("  No missing values ✅")


# ── Intake Cleaning ────────────────────────────────────────────────────────────

def clean_intakes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    before = len(df)

    # 1. Remove duplicates
    df.drop_duplicates(inplace=True)
    print(f"  Duplicates removed : {before - len(df):,}")

    # 2. Parse dates
    df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
    df.dropna(subset=["DateTime"], inplace=True)
    df["Year"]      = df["DateTime"].dt.year
    df["Month"]     = df["DateTime"].dt.month
    df["Hour"]      = df["DateTime"].dt.hour
    df["DayOfWeek"] = df["DateTime"].dt.day_name()
    df["Quarter"]   = df["DateTime"].dt.quarter

    # 3. Standardize text
    text_cols = ["Intake Type", "Intake Condition", "Animal Type",
                 "Sex upon Intake", "Breed", "Color"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].str.strip().str.title().fillna("Unknown")

    # 4. Names
    df["Name"] = (df["Name"].fillna("Unknown")
                             .str.strip()
                             .replace("", "Unknown")
                             .str.lstrip("*"))

    # 5. Age engineering
    df["Age_Months"] = df["Age upon Intake"].apply(age_to_months)
    df["Age_Group"]  = pd.cut(
        df["Age_Months"],
        bins=[0, 1, 6, 12, 36, 84, 9999],
        labels=["Neonatal", "Juvenile", "Young", "Adult", "Senior", "Geriatric"],
        right=False
    )

    # 6. Sex / neuter breakdown
    df["Neutered"] = df["Sex upon Intake"].str.contains(
        "Neutered|Spayed", case=False, na=False)
    df["Sex"] = df["Sex upon Intake"].str.extract(r"(Male|Female)", expand=False)

    # 7. Mixed breed flag
    df["Mixed_Breed"] = df["Breed"].str.contains("Mix|/", case=False, na=False)

    print(f"  Final clean rows   : {len(df):,}")
    return df


# ── Outcome Cleaning ───────────────────────────────────────────────────────────

def clean_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    before = len(df)

    df.drop_duplicates(inplace=True)
    print(f"  Duplicates removed : {before - len(df):,}")

    df["DateTime"]      = pd.to_datetime(df["DateTime"], errors="coerce")
    df["Date of Birth"] = pd.to_datetime(df["Date of Birth"], errors="coerce")
    df.dropna(subset=["DateTime", "Outcome Type"], inplace=True)

    df["Year"]    = df["DateTime"].dt.year
    df["Month"]   = df["DateTime"].dt.month
    df["Hour"]    = df["DateTime"].dt.hour
    df["Quarter"] = df["DateTime"].dt.quarter

    text_cols = ["Outcome Type", "Outcome Subtype", "Animal Type",
                 "Sex upon Outcome", "Breed", "Color"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].str.strip().str.title().fillna("Unknown")

    df["Name"] = (df["Name"].fillna("Unknown")
                             .str.strip()
                             .replace("", "Unknown")
                             .str.lstrip("*"))

    df["Age_Months"] = df["Age upon Outcome"].apply(age_to_months)

    # Target variable: positive outcome
    positive_outcomes = {"Adoption", "Return To Owner", "Rto-Adopt"}
    df["Positive_Outcome"] = df["Outcome Type"].isin(positive_outcomes).astype(int)

    # Outcome category grouping
    def group_outcome(o):
        if o in {"Adoption", "Rto-Adopt"}:         return "Adopted"
        if o == "Return To Owner":                  return "Returned"
        if o == "Transfer":                         return "Transferred"
        if o == "Euthanasia":                       return "Euthanized"
        return "Other"

    df["Outcome_Group"] = df["Outcome Type"].apply(group_outcome)

    df["Neutered"] = df["Sex upon Outcome"].str.contains(
        "Neutered|Spayed", case=False, na=False)
    df["Sex"] = df["Sex upon Outcome"].str.extract(r"(Male|Female)", expand=False)

    print(f"  Final clean rows   : {len(df):,}")
    return df


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    DATA_PATH = sys.argv[1] if len(sys.argv) > 1 else "../data/"

    print("Loading raw CSVs...")
    df_i = pd.read_csv(DATA_PATH + "Austin_Animal_Center_Intakes.csv")
    df_o = pd.read_csv(DATA_PATH + "Austin_Animal_Center_Outcomes.csv")

    report_quality(df_i, "intakes")
    report_quality(df_o, "outcomes")

    print("\n🧹 Cleaning Intakes...")
    df_i_clean = clean_intakes(df_i)

    print("\n🧹 Cleaning Outcomes...")
    df_o_clean = clean_outcomes(df_o)

    # Save silver CSVs (optional backup)
    df_i_clean.to_csv(DATA_PATH + "silver_intakes.csv", index=False)
    df_o_clean.to_csv(DATA_PATH + "silver_outcomes.csv", index=False)
    print("\n✅ Silver CSVs saved to data/")
