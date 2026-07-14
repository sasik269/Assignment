import json
import pandas as pd

LOG_FILE = r"C:\Users\Sasikumar\OneDrive\Documents\Assignment\Logs.log"

def read_log_file(log_file):
    records = []

    with open(log_file, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Malformed JSON skipped -> Line {line_no}")

    return pd.DataFrame(records)

df = read_log_file(LOG_FILE)

print(df)
print(f"\nTotal records loaded: {len(df)}")

# -----------------------------
# Step 2: Data Cleaning
# -----------------------------

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Convert numeric columns
numeric_columns = [
    "status_code",
    "response_time_ms"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove invalid rows
df = df.dropna(
    subset=[
        "timestamp",
        "ip_address",
        "status_code",
        "response_time_ms"
    ]
)

# Create minute column
df["minute"] = df["timestamp"].dt.floor("min")


# -----------------------------
# Step 3: Feature Engineering
# -----------------------------

# Error flag
df["is_error"] = df["status_code"].between(400, 599)

aggregated = (
    df.groupby(["minute", "ip_address"])
    .agg(
        total_requests=("ip_address", "count"),
        average_response_time=("response_time_ms", "mean"),
        error_rate=("is_error", "mean")
    )
    .reset_index()
)

# Convert error rate to percentage
aggregated["error_rate"] *= 100


# -----------------------------
# Step 4: Anomaly Detection
# -----------------------------

print("\n========== ANOMALIES ==========\n")

for _, row in aggregated.iterrows():

    reasons = []

    if row["total_requests"] > 1000:
        reasons.append("More than 1000 requests in one minute")

    if row["error_rate"] > 50:
        reasons.append("Error rate > 50%")

    if (
        row["average_response_time"] > 500
        and row["total_requests"] > 10
    ):
        reasons.append(
            "Average response time > 500 ms with more than 10 requests"
        )

    if reasons:
        print(
            f"Timestamp : {row['minute']}"
        )
        print(
            f"IP Address: {row['ip_address']}"
        )
        print(
            f"Reason    : {', '.join(reasons)}"
        )
        print("-" * 60)


# -----------------------------
# Optional: Save Aggregated Data
# -----------------------------
aggregated.to_csv("aggregated_log_summary.csv", index=False)

print("\nAggregated summary saved to aggregated_log_summary.csv")