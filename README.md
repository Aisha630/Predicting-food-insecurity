# 📊 **Food Insecurity Predictions using NLP & Time Series Modeling**

This repository contains **data analysis and machine learning models** to predict **food insecurity crises** using  **news-based NLP features and time-series data**. The analysis follows the methodology from the paper:

📄 **Paper:** [Predicting Food Crises Using News Streams](https://www.science.org/doi/10.1126/sciadv.abm3449)

📊 **Dataset:** [Harvard Dataverse Repository](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/CJDWUW)

📜 **Original Repo & Methods:** [GitHub Repository - Step 5 (Regression Modelling)](https://github.com/philippzi98/food_insecurity_predictions_nlp/blob/main/Step%205%20-%20Regression%20Modelling/README.md)

---

## 📂 **Repository Structure**

```
.
├── data                         # Datasets for the project
│   ├── famine-country-province-district-years-CS.csv
│   ├── fig_1_nodes.csv
│   ├── matching_districts.csv
│   ├── time_series_sample.csv
│   ├── time_series_with_causes_zscore_full.csv
├── explore_misc_files.ipynb      # Miscellaneous exploratory analysis
├── explore_time_series.ipynb     # Exploratory Data Analysis (EDA) for time series file
├── matching.png                  # Visualization of district matching
├── our_implementation.ipynb      # Custom reimplementation of the models
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── source_rf_regression_modelling.ipynb # Original reference model
├── supplemental_material_from_paper.pdf # Supporting paper material
├── worldbank_paper.pdf            # World Bank research paper
```

---

## 📂 **Dataset Overview**

This repository processes multiple datasets that contribute to  **food insecurity prediction models** . Below are the key datasets:

### **1️⃣ `famine-country-province-district-years-CS.csv`**

* **Purpose:** Provides district-level **food insecurity classifications** across multiple countries.
* **Key Column: `CS` (Crisis Severity)** → This aligns with the  **IPC Classification System** :
  * **1** = Minimal
  * **2** = Stressed
  * **3** = Crisis
  * **4** = Emergency
  * **5** = Famine
* **Use in Analysis:** Serves as the **ground-truth labels** for food crisis prediction.

### **2️⃣ `matching_districts.csv`**

* **Purpose:** Standardizes district names across different data sources.
* **Key Columns:**
  * `missing` → District names that were misspelled or missing.
  * `district` → The **corrected** district name.
  * `province` → The administrative province.
  * `match` → Specifies whether it maps to a **district** or  **province** .
* **Use in Analysis:** Ensures consistency when merging different data sources.

### **3️⃣ `time_series_with_causes_zscore_full.csv`**

* **Purpose:** Provides **time-series data** with **z-score normalized causal factors** that affect food insecurity.
* **Key Columns:**
  * `fews_ipc` → **IPC Phase Classification** (Food insecurity level to predict).
  * `carbon_2` → Climate indicator (e.g., CO2 emissions).
  * `mayhem_0, mayhem_1, mayhem_2` → Conflict-related variables.
  * `dehydrated_0, dehydrated_1, dehydrated_2` → Drought or rainfall measures.
  * `mismanagement_0, mismanagement_1, mismanagement_2` → Governance and economic indicators.
* **Use in Analysis:** This dataset is the **core input for training predictive models** in Step 5.

---

## 🔍 **Methodology**

### **1️⃣ Data Cleaning & Standardization**

* Fix missing or inconsistent district names (`matching_districts.csv`).
* Standardize food insecurity levels using IPC classifications.

### **2️⃣ Feature Engineering & Time Series Processing**

* Normalize causal indicators using  **z-score normalization** .
* Include **6 months of lagged variables** to improve prediction accuracy.
* Aggregate features at  **district, province, and country levels** .
* **Handling `_0, _1, _2` Columns:**
  * `_0` = District-level features.
  * `_1` = Province-level features.
  * `_2` = Country-level features.
  * **We recompute aggregations from scratch, so `_1` and `_2` columns may be dropped** .

### **3️⃣ Regression Modelling for Food Crisis Prediction**

* Train **Random Forest Regression** and other time-series models.
* The model takes:
  * **167 traditional risk factors**
  * **3006 news-based features**
* Uses **six quarters of lagged IPC values** to predict future food insecurity.
* Ensures predictions use  **observations from at least 3 months prior** .
* Compares against  **expert forecasts from FEWS NET** .

---

## 🚀 **Project Progress & Contributions**

We are actively refining our analysis! You can follow the progress in:

* **📂 `explore_time_series.ipynb`** → Data exploration of `time_series.csv`.
* **📂 `our_implementation.ipynb`** → Our custom implementation of the models.
* **📂 `source_rf_regression_modelling.ipynb`** → Original reference implementation.

## 💻 **How to Use This Repository**

### 📥 **Clone the Repository**

```bash
git clone https://github.com/your-repo-name/food_insecurity_predictions_nlp.git
cd food_insecurity_predictions_nlp
```

### 📦 **Install Dependencies**

```bash
uv pip install -r requirements.txt
```


# Articles Extractions

The part focused on how to extract articles from Urdu Point, focusing on two main approaches:

1. **District-wise Article Extraction**  
2. **Entire Pakistan Article Extraction (Past 2 Years)**

---

## 1. District-wise Extraction

This approach scrapes articles district wise.

### `districts_urls.csv`
- **Description:**  
  This CSV file contains a list of districts along with their corresponding URLs.  
  - **district** column: Contains the district names for which we have classifications and whose articles are available on Urdu Point.
  - **url** column: Contains the link to the main page of that district on Urdu Point. This main page is used to extract additional article links related to that district.

### `extract-district-links.py`
- **Description:**  
  This Python script reads from `districts_urls.csv` and fetches links specific to each district by crawling the corresponding main page. It retrieves the links of articles for every district.

### `retrieve-district-articles.py`
- **Description:**  
  This Python script processes the links in each of the `<district_article_links.csv`, retrieves the associated articles, and extracts the title, publication date, and the article content.
---

## 2. Entire Pakistan Extraction (Past 2 Years)

This approach scrapes articles published on Urdu Point over the past two years across Pakistan.

### `2-years-links.txt`
- **Description:**  
  This text file contains a list of links covering the past two years on Urdu Point. The date range starts from **1st January 2023** and continues until **10th April 2025**.

### `retrieve-all-articles.py`
- **Description:**  
  This Python script processes each link listed in `2-years-links.txt`, retrieves the associated articles, and extracts the title, publication date, and the article content.

---
