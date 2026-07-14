import json
import pandas as pd

LOG_FILE = r"C:\Users\Sasikumar\OneDrive\Documents\Assignment\Anamoly\Logs.log"

logs = []

# Read the log file

with open(LOG_FILE, "r") as f:
    for line_number, line in enumerate(f, start=1):
        try:
            log = json.loads(line)
            logs.append(log)
        except json.JSONDecodeError:
            print(f"Invalid JSON at line {line_number}")

df = pd.DataFrame(logs)
print(df.dtypes)
print(df.head())

# Data Cleaning
print( "-"*40,"Data Cleaning","-"*40)

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")


df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce")
df["response_time_ms"] = pd.to_numeric(df["response_time_ms"], errors="coerce")

df.dropna(subset=["timestamp", "status_code", "response_time_ms"], inplace=True)

print(df.dtypes)

# Feature Engineering
print( "-"*40,"Feature Engineering","-"*40)

# Create a new column with timestamp rounded down to the nearest minute
df["minute"] = df["timestamp"].dt.floor("min")

# Create an error flag:
# 1 = status code is 4xx or 5xx
# 0 = otherwise
df["is_error"] = df["status_code"].between(400, 599).astype(int)

# Aggregation
# print( "-"*15,"Aggregation","-"*15)

traffic_summary = (
    df.groupby(["ip_address", "minute"])
      .agg(
          total_requests=("ip_address", "count"),
          average_response_time=("response_time_ms", "mean"),
          error_rate=("is_error", "mean")
      )
      .reset_index()
)

# Convert error rate to percentage 

traffic_summary["error_rate"] = (
    traffic_summary["error_rate"] * 100
).round(2)

# Round average response time
traffic_summary["average_response_time"] = (
    traffic_summary["average_response_time"].round(2)
)
print(df.head())

print("\nTraffic Summary:")
print(traffic_summary.head(6))

# Anomaly Detection
print( "-"*40,"Anomaly Detection","-"*40)

print("\nAnomalies Detected:")

for _, row in traffic_summary.iterrows():

    # Condition 1: More than 1000 requests in a minute
    if row["total_requests"] > 1000:
        print(f"Timestamp: {row['minute']}, "
              f"IP: {row['ip_address']}, "
              f"Reason: More than 1000 requests in a minute")

    # Condition 2: Error rate greater than 50%
    if row["error_rate"] > 50:
        print(f"Timestamp: {row['minute']}, "
              f"IP: {row['ip_address']}, "
              f"Reason: Error rate greater than 50%")

    # Condition 3: Average response time > 500 ms and more than 10 requests
    if (row["average_response_time"] > 500) and (row["total_requests"] > 10):
        print(f"Timestamp: {row['minute']}, "
              f"IP: {row['ip_address']}, "
              f"Reason: Average response time > 500 ms with more than 10 requests")