# 📊 **Food Insecurity Predictions using NLP, Time Series Modeling, and LLMs**

This repository contains **data analysis, machine learning models, and large language model (LLM) based approaches** to predict **food insecurity crises** using **news-based NLP features** and **time-series modeling**. Our work builds on and extends the methodology from the original paper:

📄 **Paper:** [Predicting Food Crises Using News Streams](https://www.science.org/doi/10.1126/sciadv.abm3449)

📊 **Dataset:** [Harvard Dataverse Repository](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/CJDWUW)

📜 **Original Repo & Methods:** [GitHub - Regression Modelling (Step 5)](https://github.com/philippzi98/food_insecurity_predictions_nlp/blob/main/Step%205%20-%20Regression%20Modelling/README.md)

📜 **Our `Medium` Article:** [Medium Article](medium.com/@wajihanaveed.01/predicting-food-crises-with-news-data-fe714b01d7a3)


---

## 📂 **Repository Structure**

```
.
├── data/                          # Datasets for time series and ground truth labels
├── extras/                        # Extra resources (e.g., final maps)
├── LLM-based-modifications/       # Scripts for article classification using LLMs (Claude, OpenAI)
├── world-bank/                    # World Bank environment setup
├── explore_misc_files.ipynb        # Exploratory analysis of miscellaneous files
├── explore_time_series.ipynb       # Time series data exploration
├── graphs.ipynb                    # Visualization notebooks
├── our_implementation_pandas.ipynb # Our custom implementation using pandas
├── our_implementation_polars.ipynb # Our custom implementation using polars
├── source_rf_regression_modelling.ipynb # Original random forest modeling
├── matching.png                    # Visualization of district matching
├── environment.yml                 # Conda environment setup
├── requirements.txt                # Python package dependencies
├── supplemental_material_from_paper.pdf # Supplemental materials from the reference paper
├── worldbank_paper.pdf             # World Bank research paper
├── README.md                       # Project documentation (this file)
```

---

## 📂 **Key Datasets**

### **1️⃣ `famine-country-province-district-years-CS.csv`**
- **Description:** District-level food insecurity classification.
- **Main Column:** `CS` (Crisis Severity) aligned with IPC Phases:
  - 1: Minimal
  - 2: Stressed
  - 3: Crisis
  - 4: Emergency
  - 5: Famine

### **2️⃣ `matching_districts.csv`**
- **Description:** Corrects and standardizes district and province names.
- **Use:** Crucial for consistent merging of datasets.

### **3️⃣ `time_series_with_causes_zscore_full.csv`**
- **Description:** Time-series of causal factors (normalized via z-scores).
- **Features:** Climate, conflict, governance indicators.
- **Target:** `fews_ipc` — IPC Phase classification.

### **4️⃣ Other Data Files**
- `fig_1_nodes.csv`: Graph structure information for analysis.
- `pak_ipc.csv`: Pakistan-specific IPC phases.
- `their_modified_time_series_all_factors_and_rows.csv`: Modified external time series version.
- `ground_truth_ipc.csv`: Ground-truth IPC classifications.

---

## 🔍 **Methodology Overview**

### **1️⃣ Data Preprocessing**
- Fix missing and inconsistent district names.
- Standardize IPC classifications across datasets.

### **2️⃣ Feature Engineering**
- Normalize causal factors using z-scores.
- Generate lagged features (6 months historical).
- Multi-level aggregation (district, province, country).

### **3️⃣ Predictive Modeling**
- Train Random Forest and time series models.
- Combine:
  - 167 risk factor features
  - 3006 news-derived NLP features
- Incorporate six-quarters lag in IPC predictions.
- Compare model forecasts to FEWS NET expert projections.

---

## 🧠 **LLM-Based Enhancements**

We extend traditional modeling by using **Large Language Models** (LLMs) to classify and enrich article-based features:

| Script                         | Purpose |
|:-------------------------------|:--------|
| `agents.py`                    | LLM agents to classify text data |
| `classify-jung-dawn.py`         | Classify news articles from Jung and Dawn newspapers |
| `classify-urdupoint.py`         | Classify Urdu Point articles |
| `get_ipc_claude.py`, `get_ipc_openai.py` | Generate IPC phase predictions from article text |
| `prompts.py`                   | Custom prompts for LLM classification |
| `utils.py`                     | Utility functions for processing |

---

## 📰 **News Article Extraction Utilities**

We scrape Pakistani news articles to create **real-time event features**:

### **1. District-wise Extraction**

- **Files:** `extract-district-links.py`, `retrieve-district-articles.py`
- **Data:** `districts_urls.csv`
- **Goal:** Scrape Urdu Point articles district-by-district.

### **2. National Extraction (Past 2 Years)**

- **Files:** `retrieve-all-articles.py`
- **Data:** `2-years-links.txt`
- **Goal:** Scrape all Pakistan news articles from January 2023 to April 2025.

---

## 🚀 **Quickstart Guide**

### 📥 **Clone the Repository**

```bash
git clone https://github.com/your-repo-name/food_insecurity_predictions_nlp.git
cd food_insecurity_predictions_nlp
```

### 📦 **Install Dependencies**

Using Conda:

```bash
conda env create -f environment.yml
conda activate food-insecurity
```

Or using `uv`:

```bash
uv pip install -r requirements.txt
```

---

## 📈 **Tracking Progress**

| Notebook                               | Purpose |
|:---------------------------------------|:--------|
| `explore_time_series.ipynb`            | Analyze and clean time series data |
| `our_implementation_pandas.ipynb`      | Custom modeling with pandas |
| `our_implementation_polars.ipynb`      | Custom modeling with polars for faster processing |
| `source_rf_regression_modelling.ipynb` | Original regression modeling reference |
| `metrics.ipynb` (in LLM folder)         | Metrics for LLM-based classification tasks |

---

## ✨ **Highlights**

- 🔥 Blend **traditional statistical models** with **modern LLMs**.
- 🌍 Focused on **climate, conflict, and governance risks**.
- 📈 Predicts **food insecurity** months ahead.
- 🤖 Incorporates **news events** to enrich predictive power.

---

# 📬 **Contact**

If you have questions or suggestions, feel free to open an issue or reach out!  
Together, let's **predict and prevent** humanitarian food crises.
