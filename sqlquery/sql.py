import pandas as pd
from pandasql import sqldf

# Read CSV files
users = pd.read_csv("users_sample.csv")
events = pd.read_csv("events_sample.csv")

# Convert dates
users["signup_date"] = pd.to_datetime(users["signup_date"])
events["event_timestamp"] = pd.to_datetime(events["event_timestamp"])

pysqldf = lambda q: sqldf(q, globals())


# User Segmentation
print("-"*40,"User Segmentation","-"*40)

query1 = """
SELECT
    u.user_id,
    SUM(CASE WHEN e.event_type = 'app_open' THEN 1 ELSE 0 END) AS app_open_count,
    SUM(CASE WHEN e.event_type = 'purchase' THEN 1 ELSE 0 END) AS purchase_count,
    CASE
        WHEN SUM(CASE WHEN e.event_type='app_open' THEN 1 ELSE 0 END) >= 10
         AND SUM(CASE WHEN e.event_type='purchase' THEN 1 ELSE 0 END) >= 3
        THEN 'Highly Engaged'
        ELSE 'Low Engagement'
    END AS segment
FROM users u
JOIN events e
ON u.user_id = e.user_id
WHERE julianday(e.event_timestamp) - julianday(u.signup_date) <= 7
GROUP BY u.user_id
"""

user_segments = pysqldf(query1)

print(user_segments)


print("-"*40,"Churn Rate Calculation","-"*40)

latest_date = events["event_timestamp"].max().strftime("%Y-%m-%d %H:%M:%S")

query2 = f"""
SELECT
    us.segment,
    AVG(
        CASE
            WHEN julianday('{latest_date}') - julianday(last_open) > 30
            THEN 1
            ELSE 0
        END
    ) * 100 AS churn_rate
FROM
(
    SELECT
        user_id,
        MAX(event_timestamp) AS last_open
    FROM events
    WHERE event_type='app_open'
    GROUP BY user_id
) l
JOIN user_segments us
ON l.user_id = us.user_id
GROUP BY us.segment
"""

churn_rate = pysqldf(query2)

print(churn_rate)


print("-"*40,"Most Common Event Type for Highly Engaged Users (30-60 days after signup)","-"*40)
query3 = """
SELECT
    e.event_type,
    COUNT(*) AS total
FROM users u
JOIN events e
ON u.user_id = e.user_id
JOIN user_segments s
ON u.user_id = s.user_id
WHERE s.segment='Highly Engaged'
AND (julianday(e.event_timestamp)-julianday(u.signup_date))
BETWEEN 30 AND 60
GROUP BY e.event_type
ORDER BY total DESC
LIMIT 1
"""

common_event = pysqldf(query3)

print(common_event)


