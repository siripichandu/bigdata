# 🐾 Austin Animal Shelter — Big Data Analytics
### Big Data: Tools and Techniques | Spring 2026
### MongoDB + Medallion Architecture (Bronze → Silver → Gold)

---

## 📁 Project Structure

```
austin_animal_shelter/
├── notebooks/
│   └── austin_shelter_bigdata.ipynb   ← MAIN FILE — run this
├── scripts/
│   ├── mongo_setup.py                 ← Test MongoDB connection
│   ├── data_cleaning.py               ← Silver layer cleaning
│   ├── aggregations.py                ← Gold layer pipelines
│   ├── ml_model.py                    ← ML training & evaluation
│   └── visualizations.py             ← All 9 charts
├── data/                              ← Put your 3 CSV files here
├── charts/                            ← Generated charts saved here
├── models/                            ← Saved ML model (.pkl)
├── .env.example                       ← MongoDB URI template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️  STEP 1 — Setup Python Environment (VSCode)

Open VSCode, open the **Terminal** (Ctrl+` or View → Terminal), then run:

```bash
# Navigate to your project folder
cd /Users/siripi/Downloads/D/SEM\ 3/BIG\ DATA/Final\ Project

# Create a virtual environment
python3 -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate

# Install all dependencies
pip install -r austin_animal_shelter/requirements.txt
```

In VSCode:
- Press **Cmd+Shift+P** → "Python: Select Interpreter"
- Choose the `venv` interpreter (it ends with `venv/bin/python`)

---

## 🍃 STEP 2 — MongoDB Atlas Setup (Free Tier)

### 2a. Create Atlas Account
1. Go to **https://cloud.mongodb.com**
2. Sign up free → Create a **Shared (M0 Free)** cluster
3. Choose any region (e.g., AWS us-east-1)
4. Cluster name: `austin-shelter` (or anything)

### 2b. Create Database User
1. Left sidebar → **Database Access**
2. Click **Add New Database User**
3. Set username + password (save these!)
4. Role: **Read and write to any database**

### 2c. Whitelist Your IP
1. Left sidebar → **Network Access**
2. Click **Add IP Address**
3. Click **"Allow Access from Anywhere"** → `0.0.0.0/0` (fine for dev/school)
4. Click Confirm

### 2d. Get Connection String
1. Left sidebar → **Database** → Click your cluster → **Connect**
2. Choose **"Drivers"** → Python → version 3.12+
3. Copy the URI — looks like:
   ```
   mongodb+srv://myuser:mypassword@austin-shelter.abc123.mongodb.net/
   ```

### 2e. Set Your URI
```bash
# In your project folder:
cp austin_animal_shelter/.env.example austin_animal_shelter/.env
```
Open `.env` in VSCode and paste your real URI:
```
MONGO_URI=mongodb+srv://myuser:mypassword@austin-shelter.abc123.mongodb.net/?retryWrites=true&w=majority
```

### 2f. Test Connection
```bash
cd austin_animal_shelter
python scripts/mongo_setup.py
```
You should see: `✅ Successfully connected to MongoDB Atlas!`

---

## 📂 STEP 3 — Add Data Files

Copy your CSV files into the `data/` folder:
```
austin_animal_shelter/data/
    Austin_Animal_Center_Intakes.csv    (19.9 MB)
    Austin_Animal_Center_Outcomes.csv   (17.5 MB)
    Austin_Animal_Center_Stray_Map.csv  (3 KB)
```

From your archive folder at:
```
/Users/siripi/Downloads/D/SEM 3/BIG DATA/Final Project/archive/
```

Terminal shortcut:
```bash
cp "/Users/siripi/Downloads/D/SEM 3/BIG DATA/Final Project/archive/"*.csv \
   austin_animal_shelter/data/
```

---

## 🚀 STEP 4 — Run the Notebook (VSCode)

1. In VSCode, open `notebooks/austin_shelter_bigdata.ipynb`
2. Top-right → click **"Select Kernel"** → choose your `venv`
3. **IMPORTANT:** In Cell 3, update the data path:
   ```python
   DATA_PATH = '../data/'   # ← this is already correct if using the structure above
   ```
4. In Cell 3, update the MONGO_URI OR set it via .env:
   ```python
   from dotenv import load_dotenv
   load_dotenv('../.env')
   MONGO_URI = os.getenv('MONGO_URI')
   ```
5. Click **"Run All"** (▶▶ button at top) or run cells one by one (Shift+Enter)

---

## 🏃 STEP 5 — Run Scripts Individually (Optional)

You can also run each script standalone:

```bash
cd austin_animal_shelter

# Clean data only
python scripts/data_cleaning.py data/

# Build Gold layer aggregations
python scripts/aggregations.py

# Train ML model
python scripts/ml_model.py data/

# Generate all charts
python scripts/visualizations.py data/
```

---

## 📊 What the Notebook Does

| Layer | What Happens |
|-------|-------------|
| 🥉 **Bronze** | Raw CSVs ingested as-is into MongoDB (3 collections) |
| 🥈 **Silver** | Deduplication, datetime parsing, feature engineering, null handling |
| 🥇 **Gold** | 6 MongoDB Aggregation Pipelines → stored as reports |
| 📊 **Viz** | 9 charts: trends, heatmaps, seasonality, Sankey, geo map |
| 🤖 **ML** | Random Forest + Gradient Boosting + Logistic Regression, ROC-AUC, feature importance |

---

## 🤖 ML Model Details

**Target:** Predict whether an animal gets a **positive outcome** (Adopted / Returned to Owner)

**Features Used:**
- Animal Type, Intake Type, Intake Condition
- Age at Intake (months), Sex, Neutered status
- Mixed breed flag, Month, Hour of intake, Day of week

**Models Trained:**
- Random Forest (300 trees, balanced class weight)
- Gradient Boosting (150 trees, learning rate 0.08)
- Logistic Regression (with StandardScaler pipeline)

**Evaluation:** 5-fold stratified cross-validation + ROC-AUC + Precision-Recall

---

## 📦 MongoDB Collections

| Collection | Layer | Description |
|-----------|-------|-------------|
| `bronze_intakes` | Bronze | Raw intake records |
| `bronze_outcomes` | Bronze | Raw outcome records |
| `bronze_stray_map` | Bronze | Raw stray map records |
| `silver_intakes` | Silver | Cleaned, feature-engineered intakes |
| `silver_outcomes` | Silver | Cleaned outcomes + positive outcome flag |
| `gold_aggregates` | Gold | All aggregation pipeline results |

---

## 🐙 STEP 6 — Push to GitHub

```bash
# Initialize git in your project folder
cd austin_animal_shelter
git init
git add .
git commit -m "Initial commit: Austin Animal Shelter Big Data Project"

# Create a new PUBLIC repo on github.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/austin-animal-shelter-bigdata.git
git branch -M main
git push -u origin main
```

> **Note:** `.gitignore` already excludes `.env`, CSV files, and `.pkl` model files.
> Add a note in your README explaining the data source:
> [Kaggle Dataset](https://www.kaggle.com/datasets/jackdaoud/animal-shelter-analytics)

---

## 🎥 Video Recording Tips (5–6 min)

Suggested structure:
1. **0:00–0:30** — Intro: Why MongoDB? Medallion architecture overview
2. **0:30–1:30** — Show CSV files → run Bronze ingestion → show MongoDB Atlas collections
3. **1:30–2:30** — Silver layer: show cleaning code, before/after row counts
4. **2:30–3:30** — Gold layer: run aggregation pipelines, show results in Atlas UI
5. **3:30–4:30** — Walk through charts (trends, heatmap, seasonality)
6. **4:30–5:30** — ML model: explain features, show ROC curve + confusion matrix
7. **5:30–6:00** — Summary + GitHub link

Use **QuickTime** (Mac) or **OBS** for screen recording. Make sure text is readable at 1080p.

---

## 💡 Why MongoDB?

1. **Schema flexibility** — Animal records have inconsistent fields (intake condition, subtype) that would require NULL columns in SQL. MongoDB documents handle this naturally.
2. **Aggregation Pipeline** — MongoDB's `$group`, `$bucket`, `$lookup` operators replace complex SQL JOINs and GROUP BY statements with readable, chainable stages.
3. **Scalability** — The dataset (~130K+ records combined) will scale to millions with Atlas's horizontal sharding.
4. **JSON-native** — Animal shelter data maps directly to JSON documents without schema migration overhead.
