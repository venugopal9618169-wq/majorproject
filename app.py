"""
Streamlit Web Application:
ETL/ELT Pipeline Optimization for Heterogeneous Sources via Apriori/FP-Growth
Applied to University/Enterprise Data Warehouse Consolidation

Faculty Guide: Ms. G. Hema Sri
Domain: Data Mining & Warehousing
"""

import time
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data_generator import generate_heterogeneous_sources, extract_etl_transactions
from src.mining_engine import FPGrowthMiner, AprioriMiner, generate_association_rules
from src.etl_optimizer import ETLPipelineOptimizer
from src.warehouse_loader import build_star_schema

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="ETL Optimization via ARM | DWH Consolidation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .badge {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 6px;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Header & Metadata
# ---------------------------------------------------------
st.markdown('<div class="main-title">ETL/ELT Pipeline Optimization via Association Rule Mining</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Heterogeneous Source Consolidation into Enterprise Data Warehouse using FP-Growth & Apriori</div>', unsafe_allow_html=True)

col_meta1, col_meta2, col_meta3 = st.columns(3)
with col_meta1:
    st.markdown('<span class="badge">Domain: Data Mining & Warehousing</span>', unsafe_allow_html=True)
with col_meta2:
    st.markdown('<span class="badge">Faculty Guide: Ms. G. Hema Sri</span>', unsafe_allow_html=True)
with col_meta3:
    st.markdown('<span class="badge">Architecture: Medallion / Star Schema</span>', unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
st.sidebar.header("⚙️ Mining & Pipeline Controls")

num_records = st.sidebar.slider("Dataset Record Volume", min_value=300, max_value=3000, value=1000, step=100)
min_support = st.sidebar.slider("Minimum Support (s)", min_value=0.05, max_value=0.40, value=0.15, step=0.01)
min_confidence = st.sidebar.slider("Minimum Confidence (c)", min_value=0.30, max_value=0.95, value=0.55, step=0.05)
min_lift = st.sidebar.slider("Minimum Lift (L)", min_value=1.0, max_value=2.5, value=1.1, step=0.1)

algo_choice = st.sidebar.selectbox("Algorithm Benchmark Mode", ["Compare FP-Growth vs Apriori", "FP-Growth Only (High Speed)", "Apriori Only"])

random_seed = st.sidebar.number_input("Random Seed", value=42, step=1)

# Cached generation
@st.cache_data
def load_data(records, seed):
    return generate_heterogeneous_sources(num_students=records, random_seed=seed)

df_sis, df_lms, df_exam, df_finance = load_data(num_records, random_seed)
transactions, merged_raw = extract_etl_transactions(df_sis, df_lms, df_exam, df_finance)

# ---------------------------------------------------------
# Main Tabs
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌐 1. Heterogeneous Sources",
    "⚡ 2. Mining Engine (FP-Growth vs Apriori)",
    "🚀 3. Rule-Guided ETL Optimization",
    "🏛️ 4. Consolidated Data Warehouse",
    "🎓 5. Academic Viva & Defense Kit"
])

# =========================================================
# TAB 1: Heterogeneous Sources Ingestion
# =========================================================
with tab1:
    st.subheader("Bronze Ingestion: Heterogeneous Subsystems")
    st.markdown("""
    In enterprise and university architectures, data originates in disparate formats with divergent cadences.
    Below are the 4 simulated source systems ingested into the raw staging lake:
    """)

    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.markdown("##### 1. SIS (Student Information System)")
        st.caption("Format: Relational PostgreSQL | Schema: Demographics, Admission, Department")
        st.dataframe(df_sis.head(5), use_container_width=True)

        st.markdown("##### 2. LMS Portal (Learning Management System)")
        st.caption("Format: Semi-structured JSON / MongoDB | Schema: Attendance, Quizzes, LMS Engagement")
        st.dataframe(df_lms.head(5), use_container_width=True)

    with sub_col2:
        st.markdown("##### 3. Examination & Grading System")
        st.caption("Format: Relational MySQL | Schema: SGPA, Grades, Backlogs, Hall Ticket Status")
        st.dataframe(df_exam.head(5), use_container_width=True)

        st.markdown("##### 4. Finance & Accounts Records")
        st.caption("Format: CSV / Flat File | Schema: Fee Status, Scholarships, Library Clearance")
        st.dataframe(df_finance.head(5), use_container_width=True)

    st.markdown("---")
    st.markdown("##### 🧩 Unified Transaction Itemset Profiling for ARM")
    st.caption("Cross-table attribute tuples mapped into discrete transactional baskets for Association Rule Mining:")
    sample_txns = [", ".join(t[:5]) + "..." for t in transactions[:5]]
    st.code("\n".join([f"Transaction {i+1}: [ {t} ]" for i, t in enumerate(sample_txns)]), language="text")

# =========================================================
# TAB 2: Mining Engine & Benchmarking
# =========================================================
with tab2:
    st.subheader("Frequent Pattern & Association Rule Mining Engine")
    st.markdown("""
    Comparing **Apriori** (Candidate Generation + Multiple Scans) against **FP-Growth** (Frequent Pattern Tree + 2 Scans)
    to discover hidden schema correlations for ETL pipeline optimization.
    """)

    # Execution
    t_apriori = 0.0
    itemsets_apriori = pd.DataFrame()
    t_fpgrowth = 0.0
    itemsets_fpgrowth = pd.DataFrame()

    with st.spinner("Mining frequent itemsets..."):
        if algo_choice in ["Compare FP-Growth vs Apriori", "FP-Growth Only (High Speed)"]:
            fp_miner = FPGrowthMiner(min_support=min_support)
            start_fp = time.perf_counter()
            itemsets_fpgrowth = fp_miner.fit_transform(transactions)
            t_fpgrowth = time.perf_counter() - start_fp

        if algo_choice in ["Compare FP-Growth vs Apriori", "Apriori Only"]:
            ap_miner = AprioriMiner(min_support=min_support)
            start_ap = time.perf_counter()
            itemsets_apriori = ap_miner.fit_transform(transactions)
            t_apriori = time.perf_counter() - start_ap

    # Benchmark Cards
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    with b_col1:
        st.metric("Total Transactions", f"{len(transactions):,}")
    with b_col2:
        if not itemsets_fpgrowth.empty:
            st.metric("FP-Growth Runtime", f"{t_fpgrowth:.4f} s", delta=f"{len(itemsets_fpgrowth)} itemsets")
        else:
            st.metric("FP-Growth Runtime", "N/A")
    with b_col3:
        if not itemsets_apriori.empty:
            st.metric("Apriori Runtime", f"{t_apriori:.4f} s", delta=f"{len(itemsets_apriori)} itemsets", delta_color="inverse")
        else:
            st.metric("Apriori Runtime", "N/A")
    with b_col4:
        if t_fpgrowth > 0 and t_apriori > 0:
            speedup = t_apriori / t_fpgrowth
            st.metric("FP-Growth Speedup Factor", f"{speedup:.2f}x Faster", delta="Optimal for Big Data")
        else:
            st.metric("Speedup Factor", "Single Algo Mode")

    # Benchmarking Chart
    if t_fpgrowth > 0 and t_apriori > 0:
        st.markdown("##### ⏱️ Execution Time Comparison (Lower is Better)")
        perf_df = pd.DataFrame({
            'Algorithm': ['Apriori (Candidate Generation)', 'FP-Growth (Prefix Tree)'],
            'Execution Time (Seconds)': [t_apriori, t_fpgrowth],
            'Scans Required': ['k Database Scans', '2 Database Scans']
        })
        fig_bar = px.bar(
            perf_df, x='Algorithm', y='Execution Time (Seconds)',
            color='Algorithm', text='Execution Time (Seconds)',
            color_discrete_sequence=['#EF4444', '#10B981']
        )
        fig_bar.update_traces(texttemplate='%{text:.4f}s', textposition='outside')
        fig_bar.update_layout(height=340, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Active itemsets
    active_itemsets = itemsets_fpgrowth if not itemsets_fpgrowth.empty else itemsets_apriori
    rules_df = generate_association_rules(active_itemsets, min_confidence=min_confidence, min_lift=min_lift)

    st.markdown("---")
    st.subheader(f"Discovered Association Rules (Found {len(rules_df)} Rules)")
    st.caption("Rules filtered by Min Confidence ≥ {:.2f} and Min Lift ≥ {:.2f}".format(min_confidence, min_lift))

    if not rules_df.empty:
        # Display formatted rules
        display_rules = rules_df.copy()
        display_rules['Antecedent'] = display_rules['antecedents'].apply(lambda x: " + ".join(x))
        display_rules['Consequent'] = display_rules['consequents'].apply(lambda x: " + ".join(x))
        table_cols = ['Antecedent', 'Consequent', 'support', 'confidence', 'lift', 'conviction']
        st.dataframe(display_rules[table_cols], use_container_width=True)

        # Plot Scatter Lift vs Confidence
        fig_scatter = px.scatter(
            rules_df, x='confidence', y='lift', size='support', color='lift',
            hover_data=['antecedents', 'consequents'],
            labels={'confidence': 'Confidence (P(Y|X))', 'lift': 'Lift (Correlation Strength)'},
            title="Rule Correlation Landscape (Confidence vs. Lift)",
            color_continuous_scale="Viridis"
        )
        fig_scatter.update_layout(height=380)
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("No rules met the current support/confidence threshold. Lower the thresholds in the sidebar.")

# =========================================================
# TAB 3: Rule-Guided ETL Optimization
# =========================================================
with tab3:
    st.subheader("🚀 Rule-Guided ETL/ELT Pipeline Optimizer")
    st.markdown("""
    How mined Association Rules optimize the Data Warehouse consolidation pipeline:
    1. **Dynamic Stage Fusion:** Pre-joining attributes with high Lift ($L > 1.2$) eliminates intermediate disk shuffle.
    2. **Semantic Data Quality Gate:** Vectorized validation derived from ARM catches dirty data before loading.
    3. **Elimination of Redundant Transformations:** Irrelevant fields pruned early in the staging stream.
    """)

    optimizer = ETLPipelineOptimizer(rules_df)
    
    col_run1, col_run2 = st.columns([1, 3])
    with col_run1:
        run_btn = st.button("▶️ Execute Pipeline Comparison", type="primary", use_container_width=True)

    conv_fact, conv_metrics = optimizer.run_conventional_pipeline(df_sis, df_lms, df_exam, df_finance)
    arm_fact, quarantined, arm_metrics = optimizer.run_arm_optimized_pipeline(df_sis, df_lms, df_exam, df_finance)

    opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4)
    with opt_col1:
        st.metric("Conventional ETL Time", f"{conv_metrics['duration_sec']:.4f} s", "Baseline")
    with opt_col2:
        st.metric("ARM-Optimized ETL Time", f"{arm_metrics['duration_sec']:.4f} s", 
                  f"-{((conv_metrics['duration_sec'] - arm_metrics['duration_sec'])/conv_metrics['duration_sec']*100):.1f}% faster",
                  delta_color="normal")
    with opt_col3:
        st.metric("Shuffle Cost Index", f"{arm_metrics['shuffle_cost_index']} pts", f"-{100 - arm_metrics['shuffle_cost_index']}% I/O Overhead")
    with opt_col4:
        st.metric("Semantic Anomalies Quarantined", f"{len(quarantined)} records", "Protected Gold DWH")

    st.markdown("---")
    st.markdown("##### 🛡️ Data Quality Quarantine Log (Semantic Violations Caught by ARM Rules)")
    st.caption("Records violating rules (e.g., Pending Fees but Hall Ticket Issued, or Low Attendance with Grade A):")
    if not quarantined.empty:
        st.dataframe(quarantined.head(10), use_container_width=True)
    else:
        st.info("No anomalies detected in the current partition.")

# =========================================================
# TAB 4: Consolidated Enterprise Data Warehouse (Star Schema)
# =========================================================
with tab4:
    st.subheader("🏛️ Enterprise Data Warehouse: Gold Layer Consolidation")
    st.markdown("""
    Clean, transformed records loaded into a dimensional **Star Schema** designed for OLAP cubes and executive reporting:
    """)

    schema_dict = build_star_schema(arm_fact)
    fact_table = schema_dict['fact_student_performance']
    dim_stu = schema_dict['dim_student']
    dim_course = schema_dict['dim_course']
    dim_dept = schema_dict['dim_department']
    dim_time = schema_dict['dim_time']

    tab_f, tab_d1, tab_d2, tab_d3 = st.tabs([
        "📊 Fact_StudentAcademicPerformance",
        "👤 Dim_Student",
        "📚 Dim_Course",
        "🏢 Dim_Department & Dim_Time"
    ])

    with tab_f:
        st.markdown(f"**Total Records Consolidated in Fact Table:** `{len(fact_table):,}` rows")
        st.dataframe(fact_table.head(10), use_container_width=True)

        # OLAP Summary Charts
        st.markdown("##### 📈 Executive OLAP Insights from Consolidated Warehouse")
        c1, c2 = st.columns(2)
        with c1:
            # Grade Distribution
            fig_g = px.histogram(fact_table, x='grade', color='grade', title="Grade Distribution Across Consolidated Cohorts",
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_g.update_layout(height=320, showlegend=False)
            st.plotly_chart(fig_g, use_container_width=True)
        with c2:
            # GPA by Attendance Band
            gpa_summary = fact_table.groupby('attendance_band')['sgpa'].mean().reset_index()
            fig_a = px.bar(gpa_summary, x='attendance_band', y='sgpa', color='attendance_band',
                           title="Mean SGPA by Attendance Band (Consolidated)",
                           color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B'])
            fig_a.update_layout(height=320, showlegend=False)
            st.plotly_chart(fig_a, use_container_width=True)

        # Export Option
        csv_data = fact_table.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Fact Table (CSV)",
            data=csv_data,
            file_name="Fact_StudentAcademicPerformance.csv",
            mime="text/csv"
        )

    with tab_d1:
        st.dataframe(dim_stu.head(10), use_container_width=True)
    with tab_d2:
        st.dataframe(dim_course, use_container_width=True)
    with tab_d3:
        st.dataframe(dim_dept, use_container_width=True)
        st.dataframe(dim_time, use_container_width=True)

# =========================================================
# TAB 5: Academic Viva & Defense Kit
# =========================================================
with tab5:
    st.subheader("🎓 Academic Review & Viva Defense Documentation")
    st.markdown("""
    **Project Title:** ETL/ELT Pipeline Optimization for Heterogeneous Sources via Apriori/FP-Growth Based Association Rule Mining, Applied to University/enterprise Data Warehouse Consolidation  
    **Faculty Guide:** Ms. G. Hema Sri  
    **Domain:** Data Mining & Warehousing (DMW)
    """)

    st.markdown("---")
    st.markdown("#### ❓ Frequently Asked Viva Questions & Model Answers")

    with st.expander("Q1: What is the core novelty of using Association Rule Mining in an ETL pipeline?"):
        st.write("""
        **Answer:** In traditional Data Warehousing, Data Mining (ARM) is applied *downstream* after data is in the warehouse for reporting.
        In this research, we shift ARM *upstream into the ETL staging phase*. By profiling operational logs as transactions and schema attributes
        as items, mined rules dynamically inform:
        1. **Stage Fusion:** Pre-joining attributes with high Lift reduces cross-database network shuffling.
        2. **Semantic Data Quality:** Mined rules act as automated validation constraints to quarantine corrupt or inconsistent records before they enter the Star Schema.
        """)

    with st.expander("Q2: Why is FP-Growth preferred over Apriori in enterprise consolidation?"):
        st.write("""
        **Answer:** Apriori relies on the downward closure property to iteratively generate candidate itemsets ($C_k$) from frequent itemsets ($L_{k-1}$)
        and requires $k$ full scans over the transaction database. For an enterprise ETL with millions of records, repeated I/O leads to unacceptable pipeline lag.
        FP-Growth builds a compact prefix tree (**FP-Tree**) requiring only **2 database passes** and performs recursive mining on conditional pattern bases
        without candidate generation, yielding significant speedups.
        """)

    with st.expander("Q3: Explain the mathematical significance of Support, Confidence, and Lift in this project."):
        st.write("""
        * **Support ($s$):** $\\frac{\\text{Frequency}(X \\cup Y)}{N}$ — measures how frequently a co-occurring set of attributes is extracted together.
        * **Confidence ($c$):** $\\frac{\\text{Support}(X \\cup Y)}{\\text{Support}(X)}$ — conditional probability; measures the certainty of the transformation dependency.
        * **Lift ($L$):** $\\frac{P(X \\cap Y)}{P(X) \\cdot P(Y)}$ — measures correlation strength. Lift $> 1$ indicates strong positive association, making attributes prime candidates for pre-materialization and co-partitioning.
        """)

    with st.expander("Q4: How does this architecture handle schema heterogeneity?"):
        st.write("""
        **Answer:** Operational sources encompass relational DBMS (PostgreSQL/MySQL), document-based NoSQL (LMS JSON), and flat files (Finance CSV).
        The pipeline normalizes extracted field tokens into unified key-value transactions (`Source:Attribute=Value`). Association mining operates on these
        token sets uniformly, abstracting away the physical storage format.
        """)

    st.markdown("---")
    st.markdown("#### ☁️ How to Push to GitHub & Deploy to Streamlit Cloud")
    st.markdown("""
    1. **Push to GitHub:**
       * Create a new repository on your GitHub account (e.g., `etl-arm-dwh-consolidation`).
       * Run `push_to_github.bat` or execute:
         ```bash
         git init
         git add .
         git commit -m "Initial commit: ETL ARM DWH Consolidation App"
         git branch -M main
         git remote add origin https://github.com/<your-username>/etl-arm-dwh-consolidation.git
         git push -u origin main
         ```
    2. **Deploy to Streamlit Cloud (100% Free):**
       * Visit [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
       * Click **New app**.
       * Select your repository `etl-arm-dwh-consolidation`, Branch `main`, Main file path `app.py`.
       * Click **Deploy!** Your app will be live on the web with a public URL to submit to Ms. G. Hema Sri.
    """)
