import pandas as pd

DATA_FILE = "data/snowset_real.csv"


def load_data():

    df = pd.read_csv(
        DATA_FILE,
        na_values=["\\N"],
        low_memory=False
    )

    # Convert timestamps
    df["createdTime"] = pd.to_datetime(
        df["createdTime"],
        errors="coerce",
        utc=True
    )

    df["endTime"] = pd.to_datetime(
        df["endTime"],
        errors="coerce",
        utc=True
    )

    # Columns we need for the POC
    numeric_columns = [
        "durationTotal",
        "durationExec",
        "scanBytes",
        "userCpuTime",
        "systemCpuTime",
        "memoryUsed",
        "intDataNetReceivedBytes",
        "intDataNetSentBytes",
        "serverCount"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Derived metrics from REAL Snowset values
    df["cpuTime"] = (
        df["userCpuTime"].fillna(0)
        +
        df["systemCpuTime"].fillna(0)
    )

    df["networkBytes"] = (
        df["intDataNetReceivedBytes"].fillna(0)
        +
        df["intDataNetSentBytes"].fillna(0)
    )

    df["scanMB"] = (
        df["scanBytes"].fillna(0)
        /
        (1024 * 1024)
    )

    df["networkMB"] = (
        df["networkBytes"]
        /
        (1024 * 1024)
    )

    df["memoryMB"] = (
        df["memoryUsed"].fillna(0)
        /
        (1024 * 1024)
    )

    # Sort real queries chronologically
    df = df.sort_values(
        "createdTime"
    ).reset_index(drop=True)

    return df


def get_overview(df):

    return {
        "queries": len(df),

        "warehouses":
            df["warehouseId"].nunique(),

        "databases":
            df["databaseId"].nunique(),

        "median_duration":
            df["durationTotal"].median(),

        "p95_duration":
            df["durationTotal"].quantile(0.95),

        "average_scan_mb":
            df["scanMB"].mean(),

        "average_network_mb":
            df["networkMB"].mean(),

        "average_cpu":
            df["cpuTime"].mean(),

        "average_memory_mb":
            df["memoryMB"].mean()
    }


if __name__ == "__main__":

    df = load_data()

    print("REAL SNOWSET DATA LOADED")
    print("------------------------")

    print("Queries:", len(df))
    print("Warehouses:", df["warehouseId"].nunique())
    print("Databases:", df["databaseId"].nunique())

    print()
    print("Overview:")
    print(get_overview(df))