"""
aggregations.py
Gold Layer — All MongoDB Aggregation Pipelines
Run after ingestion and cleaning (Silver layer must exist).
"""

import pandas as pd
from pymongo import MongoClient
import os, json
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://<USERNAME>:<PASSWORD>@<CLUSTER>.mongodb.net/")


def get_db():
    client = MongoClient(MONGO_URI)
    return client["austin_animal_shelter"]


# ── Pipeline Definitions ───────────────────────────────────────────────────────

def agg_intake_trends(db) -> pd.DataFrame:
    """Annual intake volume by animal type with avg age."""
    pipeline = [
        {"$match": {"Year": {"$gte": 2013, "$lte": 2021}}},
        {"$group": {
            "_id": {"year": "$Year", "animal_type": "$Animal Type"},
            "total_intakes": {"$sum": 1},
            "avg_age_months": {"$avg": "$Age_Months"},
            "neutered_count": {"$sum": {"$cond": ["$Neutered", 1, 0]}}
        }},
        {"$sort": {"_id.year": 1, "total_intakes": -1}},
        {"$project": {
            "_id": 0,
            "year": "$_id.year",
            "animal_type": "$_id.animal_type",
            "total_intakes": 1,
            "avg_age_months": {"$round": ["$avg_age_months", 1]},
            "neutered_pct": {"$round": [
                {"$multiply": [{"$divide": ["$neutered_count", "$total_intakes"]}, 100]}, 1]}
        }}
    ]
    return pd.DataFrame(list(db["silver_intakes"].aggregate(pipeline)))


def agg_outcome_dist(db) -> pd.DataFrame:
    """Outcome type × animal type breakdown with positive rate."""
    pipeline = [
        {"$group": {
            "_id": {"outcome": "$Outcome Type", "animal": "$Animal Type"},
            "count": {"$sum": 1},
            "positive_rate": {"$avg": "$Positive_Outcome"}
        }},
        {"$sort": {"count": -1}},
        {"$project": {
            "_id": 0,
            "outcome_type": "$_id.outcome",
            "animal_type": "$_id.animal",
            "count": 1,
            "positive_rate_pct": {"$round": [{"$multiply": ["$positive_rate", 100]}, 1]}
        }}
    ]
    return pd.DataFrame(list(db["silver_outcomes"].aggregate(pipeline)))


def agg_intake_by_condition(db) -> pd.DataFrame:
    """Intake condition distribution with animal type breakdown."""
    pipeline = [
        {"$match": {"Intake Condition": {"$nin": [None, "Unknown"]}}},
        {"$group": {
            "_id": {"condition": "$Intake Condition", "animal": "$Animal Type"},
            "count": {"$sum": 1},
            "avg_age": {"$avg": "$Age_Months"}
        }},
        {"$sort": {"count": -1}},
        {"$project": {
            "_id": 0,
            "condition": "$_id.condition",
            "animal_type": "$_id.animal",
            "count": 1,
            "avg_age_months": {"$round": ["$avg_age", 1]}
        }}
    ]
    return pd.DataFrame(list(db["silver_intakes"].aggregate(pipeline)))


def agg_hourly_pattern(db) -> pd.DataFrame:
    """Intake count by hour and day of week (for heatmap)."""
    pipeline = [
        {"$group": {
            "_id": {"hour": "$Hour", "dow": "$DayOfWeek"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.hour": 1}},
        {"$project": {
            "_id": 0,
            "hour": "$_id.hour",
            "day_of_week": "$_id.dow",
            "count": 1
        }}
    ]
    return pd.DataFrame(list(db["silver_intakes"].aggregate(pipeline)))


def agg_top_breeds(db, animal_type="Dog", top_n=15) -> pd.DataFrame:
    """Top N breeds for given animal type with intake condition breakdown."""
    pipeline = [
        {"$match": {"Animal Type": animal_type}},
        {"$group": {
            "_id": "$Breed",
            "total": {"$sum": 1},
            "normal_pct": {
                "$avg": {"$cond": [{"$eq": ["$Intake Condition", "Normal"]}, 1, 0]}
            }
        }},
        {"$sort": {"total": -1}},
        {"$limit": top_n},
        {"$project": {
            "_id": 0,
            "breed": "$_id",
            "total": 1,
            "normal_pct": {"$round": [{"$multiply": ["$normal_pct", 100]}, 1]}
        }}
    ]
    return pd.DataFrame(list(db["silver_intakes"].aggregate(pipeline)))


def agg_monthly_seasonality(db) -> pd.DataFrame:
    """Monthly intake counts by animal type (averaged across years)."""
    pipeline = [
        {"$group": {
            "_id": {"month": "$Month", "animal": "$Animal Type"},
            "count": {"$sum": 1},
            "years_count": {"$addToSet": "$Year"}
        }},
        {"$project": {
            "_id": 0,
            "month": "$_id.month",
            "animal_type": "$_id.animal",
            "total_count": "$count",
            "avg_per_year": {"$round": [
                {"$divide": ["$count", {"$size": "$years_count"}]}, 0]}
        }},
        {"$sort": {"month": 1}}
    ]
    return pd.DataFrame(list(db["silver_intakes"].aggregate(pipeline)))


def agg_adoption_rate_by_age(db) -> pd.DataFrame:
    """Adoption rate bucketed by age group."""
    pipeline = [
        {"$match": {"Age_Months": {"$gt": 0, "$lt": 200}}},
        {"$bucket": {
            "groupBy": "$Age_Months",
            "boundaries": [0, 1, 3, 6, 12, 24, 48, 84, 200],
            "default": "Unknown",
            "output": {
                "total": {"$sum": 1},
                "adopted": {"$sum": "$Positive_Outcome"}
            }
        }},
        {"$project": {
            "_id": 0,
            "age_bucket_months": "$_id",
            "total": 1,
            "adopted": 1,
            "adoption_rate_pct": {
                "$round": [{"$multiply": [{"$divide": ["$adopted", "$total"]}, 100]}, 1]
            }
        }}
    ]
    return pd.DataFrame(list(db["silver_outcomes"].aggregate(pipeline)))


# ── Save Gold Layer ────────────────────────────────────────────────────────────

def build_gold_layer(db):
    print("🥇 Building Gold Layer aggregations...\n")

    pipelines = {
        "intake_trends":      agg_intake_trends,
        "outcome_dist":       agg_outcome_dist,
        "intake_condition":   agg_intake_by_condition,
        "hourly_pattern":     agg_hourly_pattern,
        "monthly_seasonality": agg_monthly_seasonality,
        "adoption_by_age":    agg_adoption_rate_by_age,
    }

    gold_col = db["gold_aggregates"]
    gold_col.drop()

    results = {}
    for name, fn in pipelines.items():
        try:
            df = fn(db)
            results[name] = df
            gold_col.insert_one({
                "report": name,
                "row_count": len(df),
                "data": df.to_dict("records"),
                "created_at": datetime.utcnow()
            })
            print(f"  ✅ {name:<28} → {len(df):>4} rows stored")
        except Exception as e:
            print(f"  ❌ {name}: {e}")

    # Top breeds stored separately
    for animal in ["Dog", "Cat"]:
        df_b = agg_top_breeds(db, animal_type=animal)
        gold_col.insert_one({
            "report": f"top_breeds_{animal.lower()}",
            "row_count": len(df_b),
            "data": df_b.to_dict("records"),
            "created_at": datetime.utcnow()
        })
        print(f"  ✅ top_breeds_{animal.lower():<21} → {len(df_b):>4} rows stored")
        results[f"top_breeds_{animal.lower()}"] = df_b

    print(f"\n📦 Gold layer complete. {gold_col.count_documents({})} reports in MongoDB.")
    return results


if __name__ == "__main__":
    db = get_db()
    results = build_gold_layer(db)
    print("\nSample — Intake Trends (first 5 rows):")
    print(results["intake_trends"].head().to_string(index=False))
