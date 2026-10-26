# ETL/ELT Pipeline Optimization for Heterogeneous Sources via Apriori/FP-Growth Based Association Rule Mining

### Applied to University / Enterprise Data Warehouse Consolidation

* **Domain:** Data Mining & Warehousing (DMW)
* **Faculty Guide:** Ms. G. Hema Sri
* **Author / Team:** B.Tech / M.Tech Computer Science & Engineering
* **Deployment:** [Streamlit Community Cloud](https://share.streamlit.io/)

---

## 📌 1. Project Overview

In large academic universities and enterprise environments, data resides in disparate, heterogeneous storage formats:
1. **SIS (Student Information System):** Relational PostgreSQL / SQL databases.
2. **LMS (Learning Management System):** Document-based JSON records (MongoDB/Moodle).
3. **Examination Portal:** Relational MySQL tables.
4. **Finance & Accounts:** Flat CSV and REST API feeds.

Traditional ETL/ELT pipelines execute costly full-table scans, repetitive cross-system joins, and uncoordinated transformations. 

### 💡 The Proposed Novel Solution
This project applies **Association Rule Mining (ARM)**—comparing **Apriori** and **FP-Growth** algorithms—directly onto operational transaction logs and staging tokens to dynamically optimize the ETL/ELT consolidation pipeline:
* **Dynamic Stage Fusion:** Pre-joining attributes exhibiting high Lift ($L > 1.2$) in memory, cutting cross-table shuffles and disk I/O.
* **Semantic Data Quality Gate:** Automatically enforcing mined association rules (e.g., fee clearance prerequisites) to quarantine dirty/anomalous records before DWH loading.
* **Star Schema Consolidation:** Ingesting clean data into an enterprise-ready dimensional model (`Fact_StudentAcademicPerformance`).

---

## 🏗️ 2. Architectural Pipeline

```
+-------------------------------------------------------------------------+
|                  Heterogeneous Operational Sources                      |
|   SIS (Postgres)  |  LMS (MongoDB)  |  Exam (MySQL)  |  Finance (CSV)   |
+-------------------------------------------------------------------------+
                                    |
                                    v (Bronze Raw Ingestion)
+-------------------------------------------------------------------------+
|                  Attribute Tokenization & Itemsets                      |
|                [Dept=CSE, Attn=High, Grade=A, Fee=Paid]                 |
+-------------------------------------------------------------------------+
                                    |
                                    v (ARM Engine)
+-------------------------------------------------------------------------+
|         Association Rule Mining (Apriori vs FP-Growth Benchmark)        |
|    Mined Rules: X => Y with Support (s), Confidence (c), Lift (L)       |
+-------------------------------------------------------------------------+
                                    |
                                    v (Optimization Core)
+-------------------------------------------------------------------------+
|                Adaptive ETL / ELT Pipeline Optimizer                    |
|   - Dynamic Stage Pre-Join       - Automated Data Quality Quarantine    |
+-------------------------------------------------------------------------+
                                    |
                                    v (Gold DWH)
+-------------------------------------------------------------------------+
|                Consolidated Star Schema Data Warehouse                  |
|    Fact_StudentPerformance | Dim_Student | Dim_Course | Dim_Department  |
+-------------------------------------------------------------------------+
```

---

## ⚡ 3. Mathematical Foundations: Apriori vs. FP-Growth

| Metric | Mathematical Formula | Meaning in ETL Pipeline |
| :--- | :--- | :--- |
| **Support ($s$)** | $s(X) = \frac{\sigma(X)}{\|D\|}$ | Frequency of attribute co-extraction in pipeline logs |
| **Confidence ($c$)** | $c(X \Rightarrow Y) = \frac{s(X \cup Y)}{s(X)}$ | Certainty that attribute $Y$ is needed whenever $X$ is loaded |
| **Lift ($L$)** | $L(X \Rightarrow Y) = \frac{c(X \Rightarrow Y)}{s(Y)}$ | Correlation strength; $L > 1$ prompts proactive stage pre-join |
| **Conviction** | $\frac{1 - s(Y)}{1 - c(X \Rightarrow Y)}$ | Implication dependency error penalty |

### Why FP-Growth outperforms Apriori:
* **Apriori:** Iterative candidate generation ($C_k$) with $k$ full scans of large transaction tables.
* **FP-Growth:** Builds an in-memory prefix tree (**FP-Tree**) requiring only **2 database scans**, achieving up to **10x-20x speedup**.

---

## 🚀 4. How to Run Locally

### Prerequisites
* Python 3.9+ or Python 3.10+ (Tested up to Python 3.14)
* pip package manager

### Steps
1. Clone or extract this repository:
   ```bash
   cd etl_arm_dwh_consolidation
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
   *(Or simply double-click `run_locally.bat` on Windows)*

---

## 🌐 5. Deploy to Streamlit Community Cloud (Step-by-Step)

Deploying this project online is 100% free:

1. **Push your code to GitHub:**
   * Create a new repository on [GitHub](https://github.com/new) named `etl-arm-dwh-consolidation`.
   * Initialize git and push:
     ```bash
     git init
     git add .
     git commit -m "Initial commit of ETL ARM DWH Consolidation Project"
     git branch -M main
     git remote add origin https://github.com/<your-github-username>/etl-arm-dwh-consolidation.git
     git push -u origin main
     ```
     *(Or double-click `push_to_github.bat` on Windows)*

2. **Deploy on Streamlit Cloud:**
   * Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
   * Click **New app**.
   * Under **Repository**, select `<your-github-username>/etl-arm-dwh-consolidation`.
   * Under **Branch**, select `main`.
   * Under **Main file path**, type `app.py`.
   * Click **Deploy!**

Your application will be live in 1-2 minutes with a shareable public URL!

---

## 📁 6. Repository File Structure

```
etl_arm_dwh_consolidation/
├── app.py                     # Main Streamlit Web Application
├── requirements.txt           # Cloud deployment dependencies
├── README.md                  # Comprehensive documentation & Viva guide
├── .gitignore                 # Python & OS ignore rules
├── run_locally.bat            # One-click local launch script
├── push_to_github.bat         # Automated GitHub push script
└── src/
    ├── __init__.py
    ├── data_generator.py      # Heterogeneous source simulators (SIS, LMS, Exam, Finance)
    ├── mining_engine.py       # Pure Python FP-Growth & Apriori engines
    ├── etl_optimizer.py       # Conventional vs ARM-Optimized ETL pipeline
    └── warehouse_loader.py    # Star Schema DWH generator (Fact & Dimensions)
```

---

## 🎓 7. Project Presentation & Viva Highlights

Prepared for evaluation by **Ms. G. Hema Sri**:
* **Novelty:** Moving Association Rule Mining from downstream reporting to upstream ETL staging.
* **Heterogeneity Management:** Unified tokenization of RDBMS, NoSQL JSON, and CSV records.
* **Demonstrated Speedup:** Live graphical benchmark of FP-Tree efficiency vs. classic Apriori candidate generation.
* **Quality Assurance:** Automated quarantine of dirty records violating mined constraints.
