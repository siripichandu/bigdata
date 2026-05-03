"""
visualizations.py
All 9 charts for the Austin Animal Shelter Big Data project.
Can run standalone (reads cleaned CSVs) or be imported from notebook.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os, warnings
warnings.filterwarnings("ignore")

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 130
plt.rcParams["font.family"] = "DejaVu Sans"

CHARTS_DIR = "../charts/"
os.makedirs(CHARTS_DIR, exist_ok=True)

COLORS = {"Dog": "#4472C4", "Cat": "#ED7D31", "Bird": "#70AD47",
          "Other": "#FFC000", "Livestock": "#FF4040"}


# ── Chart 1 — Intake Trends & Donut ───────────────────────────────────────────

def chart_intake_trends(df_intakes, agg_trends):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    trend_pivot = (agg_trends[agg_trends["animal_type"].isin(["Dog", "Cat", "Other"])]
                   .pivot_table(index="year", columns="animal_type",
                                values="total_intakes", aggfunc="sum"))

    for col in trend_pivot.columns:
        c = COLORS.get(col, "#888888")
        axes[0].plot(trend_pivot.index, trend_pivot[col], marker="o",
                     linewidth=2.5, label=col, color=c)
        axes[0].fill_between(trend_pivot.index, trend_pivot[col], alpha=0.1, color=c)

    axes[0].set_title("Annual Intake Trends by Animal Type", fontsize=14, fontweight="bold")
    axes[0].set_xlabel("Year"); axes[0].set_ylabel("Intakes")
    axes[0].legend(); axes[0].grid(alpha=0.3)

    totals = df_intakes["Animal Type"].value_counts().head(5)
    axes[1].pie(totals.values, labels=totals.index, autopct="%1.1f%%",
                startangle=90, wedgeprops={"linewidth": 2, "edgecolor": "white"},
                colors=list(COLORS.values())[:len(totals)])
    axes[1].set_title("Overall Intake Distribution", fontsize=14, fontweight="bold")

    plt.suptitle("Austin Animal Center — Intake Overview",
                 fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    _save("01_intake_trends.png")


# ── Chart 2 — Outcome Dashboard ───────────────────────────────────────────────

def chart_outcomes(df_outcomes):
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    outcome_pivot = (df_outcomes.groupby(["Animal Type", "Outcome Type"])
                                .size().unstack(fill_value=0))
    top_outcomes  = df_outcomes["Outcome Type"].value_counts().head(6).index
    subset = outcome_pivot.loc[
        outcome_pivot.index.isin(["Dog", "Cat"]),
        outcome_pivot.columns.isin(top_outcomes)
    ]
    subset.plot(kind="bar", ax=axes[0], stacked=True, colormap="tab10",
                edgecolor="white", linewidth=0.5)
    axes[0].set_title("Outcome Types: Dogs vs Cats", fontsize=14, fontweight="bold")
    axes[0].set_xlabel(""); axes[0].set_ylabel("Count")
    axes[0].tick_params(axis="x", rotation=0)
    axes[0].legend(loc="upper right", fontsize=8)

    counts = df_outcomes["Outcome Type"].value_counts().head(8)
    grad   = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(counts)))
    bars   = axes[1].barh(counts.index[::-1], counts.values[::-1], color=grad[::-1])
    for bar, val in zip(bars, counts.values[::-1]):
        axes[1].text(bar.get_width() + 100, bar.get_y() + bar.get_height() / 2,
                     f"{val:,}", va="center", fontsize=9)
    axes[1].set_title("Overall Outcome Distribution", fontsize=14, fontweight="bold")
    axes[1].set_xlabel("Count"); axes[1].grid(axis="x", alpha=0.3)

    plt.suptitle("Austin Animal Center — Outcome Analysis",
                 fontsize=16, fontweight="bold")
    plt.tight_layout()
    _save("02_outcome_analysis.png")


# ── Chart 3 — Temporal Heatmap ────────────────────────────────────────────────

def chart_heatmap(df_intakes):
    df = df_intakes.copy()
    df["DayNum"] = pd.to_datetime(df["DateTime"]).dt.dayofweek
    heat = df.groupby(["DayNum", "Hour"]).size().unstack(fill_value=0)
    heat.index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    fig, ax = plt.subplots(figsize=(16, 5))
    sns.heatmap(heat, ax=ax, cmap="YlOrRd", linewidths=0.3,
                cbar_kws={"label": "Intakes"},
                annot=True, fmt="d", annot_kws={"size": 7})
    ax.set_title("Intake Heatmap: Day of Week × Hour of Day",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Hour (24h)"); ax.set_ylabel("Day of Week")
    plt.tight_layout()
    _save("03_temporal_heatmap.png")


# ── Chart 4 — Age Distribution ────────────────────────────────────────────────

def chart_age_dist(df_intakes):
    fig, ax = plt.subplots(figsize=(14, 6))
    for animal, color in [("Dog", "#4472C4"), ("Cat", "#ED7D31"), ("Bird", "#70AD47")]:
        sub = df_intakes[
            (df_intakes["Animal Type"] == animal) &
            (df_intakes["Age_Months"].between(0, 120))
        ]["Age_Months"]
        if len(sub) < 10:
            continue
        ax.hist(sub, bins=40, alpha=0.5, label=f"{animal} (n={len(sub):,})",
                color=color, edgecolor="white")
        ax.axvline(sub.median(), color=color, linestyle="--",
                   alpha=0.85, linewidth=1.8,
                   label=f"{animal} median={sub.median():.0f}mo")

    ax.set_title("Age at Intake Distribution by Animal Type",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Age (Months)"); ax.set_ylabel("Count")
    ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    _save("04_age_distribution.png")


# ── Chart 5 — Intake Type × Condition Cross-Tab ───────────────────────────────

def chart_crosstab(df_intakes):
    ct = pd.crosstab(df_intakes["Intake Type"], df_intakes["Intake Condition"])
    ct_top = ct.loc[ct.sum(axis=1).nlargest(6).index,
                    ct.sum().nlargest(6).index]

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.heatmap(ct_top, ax=ax, cmap="Blues", annot=True, fmt=",d",
                linewidths=0.5, linecolor="white",
                cbar_kws={"label": "Count"})
    ax.set_title("Intake Type × Intake Condition Cross-Analysis",
                 fontsize=14, fontweight="bold")
    ax.set_ylabel("Intake Type"); ax.set_xlabel("Intake Condition")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    _save("05_intake_crosstab.png")


# ── Chart 6 — Monthly Seasonality ────────────────────────────────────────────

def chart_seasonality(df_intakes):
    month_names = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    monthly = (df_intakes.groupby(["Month", "Animal Type"])
                         .size().unstack(fill_value=0))

    fig, ax = plt.subplots(figsize=(14, 5))
    x = np.arange(12); w = 0.35
    for i, (animal, color) in enumerate([("Dog", "#4472C4"), ("Cat", "#ED7D31")]):
        if animal in monthly.columns:
            offset = (i - 0.5) * w
            ax.bar(x + offset, monthly[animal], w, label=animal,
                   color=color, alpha=0.85, edgecolor="white")

    ax.set_xticks(x); ax.set_xticklabels(month_names)
    ax.set_title("Monthly Intake Seasonality: Dogs vs Cats",
                 fontsize=14, fontweight="bold")
    ax.set_ylabel("Intakes"); ax.set_xlabel("Month")
    ax.legend(); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    _save("06_monthly_seasonality.png")


# ── Chart 8 — Sankey Flow (Plotly) ────────────────────────────────────────────

def chart_sankey(df_merged):
    data = (df_merged.groupby(["Intake Type", "Animal Type", "Outcome Type"])
                     .size().reset_index(name="count"))
    data = data[data["count"] > 50]  # filter noise

    intake_types  = sorted(data["Intake Type"].unique())
    animal_types  = sorted(data["Animal Type"].unique())
    outcome_types = sorted(data["Outcome Type"].unique())
    all_nodes     = intake_types + animal_types + outcome_types
    idx           = {n: i for i, n in enumerate(all_nodes)}

    sources, targets, values = [], [], []
    for _, row in data.iterrows():
        sources.append(idx[row["Intake Type"]])
        targets.append(idx[row["Animal Type"]])
        values.append(row["count"])
        sources.append(idx[row["Animal Type"]])
        targets.append(idx[row["Outcome Type"]])
        values.append(row["count"])

    fig = go.Figure(go.Sankey(
        node=dict(label=all_nodes, pad=15, thickness=20,
                  color="rgba(68,114,196,0.75)"),
        link=dict(source=sources, target=targets, value=values,
                  color="rgba(68,114,196,0.18)")
    ))
    fig.update_layout(
        title_text="Animal Flow: Intake Type → Species → Outcome",
        font_size=11, height=620
    )
    path = CHARTS_DIR + "08_sankey_flow.html"
    fig.write_html(path)
    print(f"✅ Sankey saved → {path}")


# ── Chart 9 — Adoption Rate by Age Group (Bar) ────────────────────────────────

def chart_adoption_by_age(df_outcomes):
    df = df_outcomes[df_outcomes["Age_Months"].between(0, 200)].copy()
    df["Age_Bucket"] = pd.cut(
        df["Age_Months"],
        bins=[0, 1, 3, 6, 12, 24, 48, 84, 200],
        labels=["<1mo","1-3mo","3-6mo","6-12mo","1-2yr","2-4yr","4-7yr","7+yr"],
        right=False
    )
    rate = (df.groupby("Age_Bucket")["Positive_Outcome"]
              .agg(["mean", "count"])
              .reset_index())
    rate.columns = ["Age_Bucket", "Adoption_Rate", "Count"]

    fig, ax1 = plt.subplots(figsize=(13, 6))
    ax2 = ax1.twinx()

    colors_b = plt.cm.RdYlGn(rate["Adoption_Rate"].values)
    bars = ax1.bar(range(len(rate)), rate["Adoption_Rate"] * 100,
                   color=colors_b, edgecolor="white", alpha=0.85)
    ax2.plot(range(len(rate)), rate["Count"], "o--", color="#4472C4",
             linewidth=1.8, markersize=6, label="# Animals")

    for bar, val in zip(bars, rate["Adoption_Rate"] * 100):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 f"{val:.0f}%", ha="center", fontsize=9, fontweight="bold")

    ax1.set_xticks(range(len(rate))); ax1.set_xticklabels(rate["Age_Bucket"])
    ax1.set_ylabel("Positive Outcome Rate (%)", color="black")
    ax2.set_ylabel("# Animals in Bucket", color="#4472C4")
    ax2.tick_params(axis="y", colors="#4472C4")
    ax2.legend(loc="upper right")
    ax1.set_title("Positive Outcome Rate by Age at Intake",
                  fontsize=14, fontweight="bold")
    ax1.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    _save("09_adoption_by_age.png")


# ── Helper ─────────────────────────────────────────────────────────────────────

def _save(filename):
    path = CHARTS_DIR + filename
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"✅ Saved → {path}")


# ── Run All ────────────────────────────────────────────────────────────────────

def run_all_charts(df_intakes, df_outcomes, agg_trends, df_merged=None):
    print("\n📊 Generating all charts...\n")
    chart_intake_trends(df_intakes, agg_trends)
    chart_outcomes(df_outcomes)
    chart_heatmap(df_intakes)
    chart_age_dist(df_intakes)
    chart_crosstab(df_intakes)
    chart_seasonality(df_intakes)
    if df_merged is not None:
        chart_sankey(df_merged)
    chart_adoption_by_age(df_outcomes)
    print("\n✅ All charts generated!")


if __name__ == "__main__":
    from data_cleaning import clean_intakes, clean_outcomes
    import sys
    DATA_PATH = sys.argv[1] if len(sys.argv) > 1 else "../data/"

    df_i = pd.read_csv(DATA_PATH + "Austin_Animal_Center_Intakes.csv")
    df_o = pd.read_csv(DATA_PATH + "Austin_Animal_Center_Outcomes.csv")

    df_i_clean = clean_intakes(df_i)
    df_o_clean = clean_outcomes(df_o)

    # Fake trend aggregation from cleaned data
    agg_trends = (df_i_clean.groupby(["Year", "Animal Type"])
                             .size().reset_index(name="total_intakes")
                             .rename(columns={"Year": "year", "Animal Type": "animal_type"}))

    df_merged = pd.merge(
        df_i_clean[["Animal ID", "Intake Type", "Animal Type"]],
        df_o_clean[["Animal ID", "Outcome Type"]],
        on="Animal ID"
    )

    run_all_charts(df_i_clean, df_o_clean, agg_trends, df_merged)
