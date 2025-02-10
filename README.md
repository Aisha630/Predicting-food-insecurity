# 📊 Food Insecurity Predictions using NLP & Time Series Modelling

This repository contains **data analysis and machine learning models** to predict **food insecurity crises** using  **news-based NLP features and time-series data** . The analysis follows the methodology from the paper:

📝 **Paper:** [Predicting food crises using news streams](https://www.science.org/doi/10.1126/sciadv.abm3449)

📊 **Dataset:** [Harvard Dataverse Repository](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/CJDWUW)

🌟 **Original Repo & Methods:** [GitHub Repository - Step 5 (Regression Modelling)](https://github.com/philippzi98/food_insecurity_predictions_nlp/blob/main/Step%205%20-%20Regression%20Modelling/README.md)

---

## 🐂 **Repository Structure**

```
.
├── README.md  # Project Documentation
├── data
│   ├── famine-country-province-district-years-CS.csv
│   ├── fig_1_nodes.csv
│   ├── matching_districts.csv
│   ├── time_series_sample.csv
│   ├── time_series_with_causes_zscore_full.csv
├── explore.ipynb  # Exploratory Data Analysis Notebook
├── matching.png  # Visualization of district matching
├── our_implementation.ipynb  # Custom implementation of the models
├── source_rf_regression_modelling.ipynb  # Original model code
├── supplemental_material_from_paper.pdf  # Supporting paper material

```

---

## 📂 **Dataset Overview**

This repository analyzes and processes multiple datasets that contribute to  **food insecurity prediction models** . Below are the datasets used:

### **1️⃣ `famine-country-province-district-years-CS.csv`**

* **Purpose:** Provides district-level **food insecurity classifications** across multiple countries.
* **Key Column: `CS` (Crisis Severity)** → This aligns with the  **IPC Classification System** :
  * **1** = Minimal
  * **2** = Stressed
  * **3** = Crisis
  * **4** = Emergency
  * **5** = Famine
* **Use in Analysis:** This dataset serves as the **ground-truth labels** for food crisis prediction.

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

### **1. Data Cleaning & Standardization**

* Fix missing or inconsistent district names (`matching_districts.csv`).
* Standardize food insecurity levels using IPC classifications.

### **2. Feature Engineering & Time Series Processing**

* Normalize causal indicators using  **z-score normalization** .
* Include lagged variables (up to 6 months) to improve prediction accuracy.
* Aggregate features at  **district, province, and country levels** .
* The dataset includes **multiple lagged versions** of features:
  * `_0, _1, _2` suffixes indicate **spatial aggregation levels** (district, province, country).
  * Lagged versions **capture past trends** in food security drivers.

### **3. Regression Modelling for Food Crisis Prediction**

* Train **Random Forest Regression** and other time-series models.
* The model takes **167 traditional risk factors** and  **3006 news-based features** .
* Uses **six quarters of lagged IPC values** to predict future food insecurity.
* Ensures predictions are based only on  **observations from at least 3 months prior** .
* Compares against  **expert forecasts from FEWS NET** .

---

## 🌟 **Contributions & Updates**

We are actively refining our analysis! You can follow the progress in:

* **`explore.ipynb`** → Data exploration & preprocessing.
* **`our_implementation.ipynb`** → Our custom implementation of the models.
* **`source_rf_regression_modelling.ipynb`** → Original reference implementation.

👉 Stay tuned for further updates as we refine the model predictions and insights!

This repository contains **data analysis and machine learning models** to predict **food insecurity crises** using **news-based NLP features and time-series data**. The analysis follows the methodology from the paper:

📄 **Paper:** [Predicting food crises using news streams](https://www.science.org/doi/10.1126/sciadv.abm3449)
📊 **Dataset:** [Harvard Dataverse Repository](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/CJDWUW)
📜 **Original Repo & Methods:** [GitHub Repository - Step 5 (Regression Modelling)](https://github.com/philippzi98/food_insecurity_predictions_nlp/blob/main/Step%205%20-%20Regression%20Modelling/README.md)

---

## 📂 **Dataset Overview**

This repository analyzes and cleans multiple datasets that contribute to **food insecurity prediction models**. The datasets are stored in **Step 5 of this repository** and include:

### **1️⃣ `famine-country-province-district-years-CS.csv`**

- **Purpose:** Provides district-level **food insecurity classifications** across multiple countries.
- **Key Column: `CS` (Crisis Severity)** → This aligns with the **IPC Classification System**:
  - **1** = Minimal
  - **2** = Stressed
  - **3** = Crisis
  - **4** = Emergency
  - **5** = Famine
- **Use in Analysis:** This dataset serves as the **ground-truth labels** for food crisis prediction.

### **2️⃣ `matching_districts.csv`**

- **Purpose:** Standardizes district names across different data sources.
- **Key Columns:**
  - `missing` → District names that were misspelled or missing.
  - `district` → The **corrected** district name.
  - `province` → The administrative province.
  - `match` → Specifies whether it maps to a **district** or **province**.
- **Use in Analysis:** Ensures consistency when merging different data sources.

### **3️⃣ `time_series_with_causes_zscore_full.csv`**

- **Purpose:** Provides **time-series data** with **z-score normalized causal factors** that affect food insecurity.
- **Key Columns:**
  - `fews_ipc` → **IPC Phase Classification** (Food insecurity level to predict).
  - `carbon_2` → Climate indicator (e.g., CO2 emissions).
  - `mayhem_0, mayhem_1, mayhem_2` → Conflict-related variables.
  - `dehydrated_0, dehydrated_1, dehydrated_2` → Drought or rainfall measures.
  - `mismanagement_0, mismanagement_1, mismanagement_2` → Governance and economic indicators.
- **Use in Analysis:** This dataset is the **core input for training predictive models** in Step 5.

---

## 🔍 **Methodology**

1. **Data Cleaning & Standardization**

   - Fix missing or inconsistent district names (`matching_districts.csv`).
   - Standardize food insecurity levels using IPC classifications.
2. **Feature Engineering & Time Series Processing**

   - Normalize causal indicators using **z-score normalization**.
   - Include lagged variables to improve prediction accuracy.
3. **Regression Modelling for Food Crisis Prediction**

   - Train **Random Forest Regression** and other time-series models.
   - Predict future IPC classifications based on past data.

---
