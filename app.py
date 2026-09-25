import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from core import load_data, get_overview
from analytics import run_analysis, SNAPSHOT_SIZE


st.set_page_config(
    page_title="Adaptive Sharding Optimizer",
    page_icon="⚙️",
    layout="wide"
)


@st.cache_data
def get_data():
    return load_data()


df = get_data()
overview = get_overview(df)
analysis = run_analysis()


# ==================================================
# HEADER
# ==================================================

st.title("Cost-Aware Adaptive Hyper-Heuristic Framework")

st.subheader(
    "Cloud Database Sharding Optimisation — Working Proof of Concept"
)

st.info(
    "This prototype analyses real anonymised Snowflake query workload "
    "records from the public Snowset dataset."
)


# ==================================================
# 1. DATASET OVERVIEW
# ==================================================

st.header("1. Real Workload Dataset")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Real Queries Analysed",
    f"{overview['queries']:,}"
)

c2.metric(
    "Warehouses",
    f"{overview['warehouses']:,}"
)

c3.metric(
    "Databases",
    f"{overview['databases']:,}"
)

st.caption(
    "No synthetic query records are generated in this POC."
)


# ==================================================
# 2. WORKLOAD PROFILE
# ==================================================

st.header("2. Workload Profile")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Median Query Duration",
    f"{overview['median_duration']:,.2f} ms"
)

c2.metric(
    "P95 Query Duration",
    f"{overview['p95_duration']:,.2f} ms"
)

c3.metric(
    "Average Scan",
    f"{overview['average_scan_mb']:,.2f} MB"
)

c4.metric(
    "Average Network",
    f"{overview['average_network_mb']:,.2f} MB"
)

c5, c6 = st.columns(2)

c5.metric(
    "Average CPU Time",
    f"{overview['average_cpu']:,.2f}"
)

c6.metric(
    "Average Memory",
    f"{overview['average_memory_mb']:,.2f} MB"
)


# ==================================================
# 3. QUERY DURATION DISTRIBUTION
# ==================================================

st.header("3. Real Query Duration Distribution")

duration = df["durationTotal"].dropna()

upper_limit = duration.quantile(0.99)

visual_data = duration[
    duration <= upper_limit
]

fig, ax = plt.subplots(figsize=(10, 4))

ax.hist(
    visual_data,
    bins=40
)

ax.set_xlabel("Query Duration (ms)")
ax.set_ylabel("Number of Queries")
ax.set_title("Snowset Query Duration Distribution")

st.pyplot(fig)


# ==================================================
# 4. ADAPTIVE WORKLOAD ANALYSIS
# ==================================================

st.header("4. Adaptive Workload Analysis")

st.write(
    f"The **{overview['queries']:,} real queries** are processed "
    f"chronologically in snapshots of **{SNAPSHOT_SIZE:,} queries each**."
)

selected_snapshot = st.slider(
    "Select workload snapshot",
    min_value=1,
    max_value=len(analysis),
    value=len(analysis)
)

current = analysis.iloc[
    selected_snapshot - 1
]

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Queries in Snapshot",
    int(current["queryCount"])
)

c2.metric(
    "Average Scan",
    f"{current['avgScanMB']:.2f} MB"
)

c3.metric(
    "Average Network",
    f"{current['avgNetworkMB']:.2f} MB"
)

c4.metric(
    "Workload Drift",
    f"{current['Drift Score']:.3f}"
)

st.write(
    f"**Workload Drift Level:** {current['Drift Level']}"
)


# ==================================================
# 5. HYPER-HEURISTIC SELECTION
# ==================================================

st.header("5. Hyper-Heuristic Algorithm Selection")

scores = pd.DataFrame(
    {
        "Algorithm": [
            "Greedy",
            "Genetic Algorithm",
            "Tabu Search"
        ],
        "Suitability Score": [
            current["Greedy"],
            current["Genetic Algorithm"],
            current["Tabu Search"]
        ]
    }
)

st.bar_chart(
    scores.set_index("Algorithm")
)

st.success(
    "Recommended heuristic: "
    + current["Selected Algorithm"]
)

st.caption(
    "These values are prototype policy suitability scores calculated "
    "from observed workload characteristics. They are not execution "
    "benchmark results of the complete optimisation algorithms."
)


# ==================================================
# 6. CURRENT SNAPSHOT METRICS
# ==================================================

st.header("6. Current Snapshot Metrics")

snapshot_metrics = pd.DataFrame(
    {
        "Metric": [
            "Median Query Duration",
            "P95 Query Duration",
            "Average Scan MB",
            "Average Network MB",
            "Average CPU",
            "Average Memory MB",
            "Average Servers"
        ],
        "Value": [
            current["medianDuration"],
            current["p95Duration"],
            current["avgScanMB"],
            current["avgNetworkMB"],
            current["avgCpu"],
            current["avgMemoryMB"],
            current["avgServers"]
        ]
    }
)

st.dataframe(
    snapshot_metrics,
    width="stretch",
    hide_index=True
)


# ==================================================
# 7. ADAPTIVE HISTORY
# ==================================================

st.header("7. Adaptive Selection History")

history = analysis[
    [
        "snapshot",
        "queryCount",
        "medianDuration",
        "avgScanMB",
        "avgNetworkMB",
        "Selected Algorithm",
        "Drift Score",
        "Drift Level"
    ]
]

st.dataframe(
    history,
    width="stretch",
    hide_index=True
)


# ==================================================
# 8. SELECTION SUMMARY
# ==================================================

st.header("8. Algorithm Selection Summary")

selection_counts = (
    analysis["Selected Algorithm"]
    .value_counts()
    .reset_index()
)

selection_counts.columns = [
    "Algorithm",
    "Snapshots Selected"
]

st.dataframe(
    selection_counts,
    width="stretch",
    hide_index=True
)

st.bar_chart(
    selection_counts.set_index("Algorithm")
)


# ==================================================
# 9. CURRENT POC SCOPE
# ==================================================

st.header("9. Current POC Scope")

st.markdown(
    """
### Implemented

- Real Snowset workload ingestion
- Query-resource profiling
- Chronological workload snapshots
- Workload drift detection
- Greedy / Genetic Algorithm / Tabu Search suitability policy
- Adaptive heuristic recommendation
- Interactive Streamlit dashboard

### Next implementation stage

The public Snowset workload is anonymised and does not expose
the original SQL statements and table relationships.

Therefore, the next phase will integrate database schema and
SQL-query logs to construct the workload hypergraph and generate
actual table-level shard placements.
"""
)

st.divider()

st.caption(
    "Dataset used: Snowset public Snowflake workload trace."
)