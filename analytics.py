import pandas as pd
from core import load_data

SNAPSHOT_SIZE = 1000


def normalize(series):
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(0.5, index=series.index)

    return (series - minimum) / (maximum - minimum)


def build_snapshots(df):
    data = df.copy()

    # 1000 consecutive real queries = 1 workload snapshot
    data["snapshot"] = (data.index // SNAPSHOT_SIZE) + 1

    snapshots = (
        data.groupby("snapshot")
        .agg(
            queryCount=("queryId", "count"),
            medianDuration=("durationTotal", "median"),
            p95Duration=("durationTotal", lambda x: x.quantile(0.95)),
            avgScanMB=("scanMB", "mean"),
            avgNetworkMB=("networkMB", "mean"),
            avgCpu=("cpuTime", "mean"),
            avgMemoryMB=("memoryMB", "mean"),
            avgServers=("serverCount", "mean"),
        )
        .reset_index()
    )

    snapshots["durationSkew"] = (
        snapshots["p95Duration"]
        / snapshots["medianDuration"].clip(lower=1)
    )

    return snapshots


def calculate_scores(snapshots):
    result = snapshots.copy()

    result["durationIntensity"] = normalize(result["medianDuration"])
    result["skewIntensity"] = normalize(result["durationSkew"])
    result["ioIntensity"] = normalize(result["avgScanMB"])
    result["networkIntensity"] = normalize(result["avgNetworkMB"])
    result["cpuIntensity"] = normalize(result["avgCpu"])

    # Prototype hyper-heuristic suitability policy

    result["Greedy"] = (
        0.40 * (1 - result["skewIntensity"])
        + 0.30 * (1 - result["ioIntensity"])
        + 0.30 * (1 - result["networkIntensity"])
    ) * 100

    result["Genetic Algorithm"] = (
        0.40 * result["skewIntensity"]
        + 0.30 * result["cpuIntensity"]
        + 0.30 * result["durationIntensity"]
    ) * 100

    result["Tabu Search"] = (
        0.45 * result["networkIntensity"]
        + 0.35 * result["ioIntensity"]
        + 0.20 * result["skewIntensity"]
    ) * 100

    algorithms = [
        "Greedy",
        "Genetic Algorithm",
        "Tabu Search"
    ]

    result["Selected Algorithm"] = (
        result[algorithms].idxmax(axis=1)
    )

    return result


def calculate_drift(result):
    data = result.copy()

    features = [
        "durationIntensity",
        "skewIntensity",
        "ioIntensity",
        "networkIntensity",
        "cpuIntensity"
    ]

    change = (
        data[features]
        - data[features].shift(1)
    ).abs()

    data["Drift Score"] = (
        change.mean(axis=1).fillna(0)
    )

    def classify(value):
        if value >= 0.30:
            return "High"
        elif value >= 0.15:
            return "Moderate"
        else:
            return "Low"

    data["Drift Level"] = (
        data["Drift Score"].apply(classify)
    )

    return data


def run_analysis():
    df = load_data()

    snapshots = build_snapshots(df)
    snapshots = calculate_scores(snapshots)
    snapshots = calculate_drift(snapshots)

    return snapshots


if __name__ == "__main__":
    result = run_analysis()

    print()
    print("ADAPTIVE WORKLOAD ANALYSIS")
    print("--------------------------")
    print("Real queries per snapshot:", SNAPSHOT_SIZE)
    print("Number of snapshots:", len(result))
    print()

    print(
        result[
            [
                "snapshot",
                "medianDuration",
                "avgScanMB",
                "avgNetworkMB",
                "Greedy",
                "Genetic Algorithm",
                "Tabu Search",
                "Selected Algorithm",
                "Drift Score",
                "Drift Level"
            ]
        ].to_string(index=False)
    )

    print()
    print("Algorithm selection summary:")
    print(result["Selected Algorithm"].value_counts())