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
def get_app_data():
    df = load_data()
    overview = get_overview(df)
    analysis = run_analysis()
    return df, overview, analysis


df, overview, analysis = get_app_data()

selection_summary = (
    analysis["Selected Algorithm"]
    .value_counts()
    .reset_index()
)
selection_summary.columns = [
    "Algorithm",
    "Snapshots Selected"
]

selection_summary["Share (%)"] = (
    selection_summary["Snapshots Selected"]
    / selection_summary["Snapshots Selected"].sum()
    * 100
).round(1)

latest_snapshot = analysis.iloc[-1]
top_algorithm = selection_summary.iloc[0]["Algorithm"]


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("Adaptive Sharding Optimizer")
st.sidebar.caption("Analytics Dashboard")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Snapshot Explorer",
        "Workload History",
        "Algorithm Summary"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("Quick Stats")
st.sidebar.metric("Queries", f"{overview['queries']:,}")
st.sidebar.metric("Snapshots", len(analysis))
st.sidebar.metric(
    "Current Recommendation",
    latest_snapshot["Selected Algorithm"]
)
st.sidebar.metric(
    "Current Drift Level",
    latest_snapshot["Drift Level"]
)

if page == "Snapshot Explorer":
    st.sidebar.divider()
    selected_snapshot = st.sidebar.slider(
        "Snapshot",
        min_value=1,
        max_value=len(analysis),
        value=len(analysis)
    )
else:
    selected_snapshot = len(analysis)


# ==================================================
# HEADER
# ==================================================

st.title("Adaptive Sharding Optimizer")
st.subheader("Cost-Aware Workload Analytics and Heuristic Selection")


# ==================================================
# PAGE 1 — OVERVIEW
# ==================================================

if page == "Overview":

    st.header("System Overview")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Queries", f"{overview['queries']:,}")
    c2.metric("Warehouses", f"{overview['warehouses']:,}")
    c3.metric("Databases", f"{overview['databases']:,}")

    st.divider()

    st.header("Workload Overview")

    c1, c2, c3 = st.columns(3)

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

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "Average Network",
        f"{overview['average_network_mb']:,.2f} MB"
    )

    c5.metric(
        "Average CPU Time",
        f"{overview['average_cpu']:,.2f}"
    )

    c6.metric(
        "Average Memory",
        f"{overview['average_memory_mb']:,.2f} MB"
    )

    st.divider()

    left, right = st.columns([2, 1])

    with left:
        st.header("Query Duration Distribution")

        duration = df["durationTotal"].dropna()
        upper_limit = duration.quantile(0.99)
        visual_data = duration[duration <= upper_limit]

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.hist(visual_data, bins=35)
        ax.set_xlabel("Query Duration (ms)")
        ax.set_ylabel("Number of Queries")
        ax.set_title("Query Duration Distribution")
        plt.tight_layout()

        st.pyplot(fig)

    with right:
        st.header("Adaptive Summary")

        st.metric(
            "Latest Recommended Heuristic",
            latest_snapshot["Selected Algorithm"]
        )

        st.metric(
            "Most Frequently Selected",
            top_algorithm
        )

        st.metric(
            "Latest Drift Score",
            f"{latest_snapshot['Drift Score']:.3f}"
        )

        st.metric(
            "Latest Drift Level",
            latest_snapshot["Drift Level"]
        )

        st.write("")
        st.write("**Snapshots per Algorithm**")

        st.dataframe(
            selection_summary,
            width="stretch",
            hide_index=True
        )


# ==================================================
# PAGE 2 — SNAPSHOT EXPLORER
# ==================================================

elif page == "Snapshot Explorer":

    current = analysis.iloc[selected_snapshot - 1]

    st.header(f"Snapshot Explorer — Snapshot {selected_snapshot}")

    st.caption(
        f"Each snapshot contains {SNAPSHOT_SIZE:,} consecutive queries."
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Queries", int(current["queryCount"]))
    c2.metric("Average Scan", f"{current['avgScanMB']:.2f} MB")
    c3.metric("Average Network", f"{current['avgNetworkMB']:.2f} MB")
    c4.metric("Drift Score", f"{current['Drift Score']:.3f}")

    c5, c6, c7 = st.columns(3)

    c5.metric(
        "Median Duration",
        f"{current['medianDuration']:.2f} ms"
    )

    c6.metric(
        "P95 Duration",
        f"{current['p95Duration']:.2f} ms"
    )

    c7.metric(
        "Average Servers",
        f"{current['avgServers']:.2f}"
    )

    st.write(
        f"**Workload Drift Level:** {current['Drift Level']}"
    )

    st.success(
        f"Recommended Heuristic: {current['Selected Algorithm']}"
    )

    st.divider()

    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("Algorithm Suitability Scores")

        score_df = pd.DataFrame(
            {
                "Algorithm": [
                    "Greedy",
                    "Genetic Algorithm",
                    "Tabu Search"
                ],
                "Score": [
                    current["Greedy"],
                    current["Genetic Algorithm"],
                    current["Tabu Search"]
                ]
            }
        )

        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.barh(
            score_df["Algorithm"],
            score_df["Score"]
        )
        ax.set_xlabel("Suitability Score")
        ax.set_title("Current Snapshot Heuristic Scores")
        plt.tight_layout()

        st.pyplot(fig)

    with right:
        st.subheader("Snapshot Metrics")

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
                    round(current["medianDuration"], 2),
                    round(current["p95Duration"], 2),
                    round(current["avgScanMB"], 2),
                    round(current["avgNetworkMB"], 2),
                    round(current["avgCpu"], 2),
                    round(current["avgMemoryMB"], 2),
                    round(current["avgServers"], 2)
                ]
            }
        )

        st.dataframe(
            snapshot_metrics,
            width="stretch",
            hide_index=True
        )


# ==================================================
# PAGE 3 — WORKLOAD HISTORY
# ==================================================

elif page == "Workload History":

    st.header("Workload History")

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
    ].copy()

    history["medianDuration"] = history["medianDuration"].round(2)
    history["avgScanMB"] = history["avgScanMB"].round(2)
    history["avgNetworkMB"] = history["avgNetworkMB"].round(2)
    history["Drift Score"] = history["Drift Score"].round(3)

    st.dataframe(
        history,
        width="stretch",
        hide_index=True
    )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Drift Trend")

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(
            analysis["snapshot"],
            analysis["Drift Score"],
            marker="o"
        )
        ax.set_xlabel("Snapshot")
        ax.set_ylabel("Drift Score")
        ax.set_title("Workload Drift Across Snapshots")
        plt.tight_layout()

        st.pyplot(fig)

    with c2:
        st.subheader("Resource Trend")

        resource_trend = analysis[
            ["snapshot", "avgScanMB", "avgNetworkMB"]
        ].copy()

        resource_trend = resource_trend.set_index("snapshot")

        st.line_chart(resource_trend)


# ==================================================
# PAGE 4 — ALGORITHM SUMMARY
# ==================================================

elif page == "Algorithm Summary":

    st.header("Algorithm Selection Summary")

    st.dataframe(
        selection_summary,
        width="stretch",
        hide_index=True
    )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Selection Count")

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(
            selection_summary["Algorithm"],
            selection_summary["Snapshots Selected"]
        )
        ax.set_ylabel("Snapshots Selected")
        ax.set_title("Algorithm Selection Frequency")
        plt.xticks(rotation=15)
        plt.tight_layout()

        st.pyplot(fig)

    with c2:
        st.subheader("Selection Share")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(
            selection_summary["Snapshots Selected"],
            labels=selection_summary["Algorithm"],
            autopct="%1.1f%%"
        )
        ax.set_title("Algorithm Selection Distribution")
        plt.tight_layout()

        st.pyplot(fig)