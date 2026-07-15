import pandas as pd
import mysql.connector

from config import DB_CONFIG


# -------------------------------
# Connect to MySQL
# -------------------------------

connection = mysql.connector.connect(
    host=DB_CONFIG["host"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    database=DB_CONFIG["database"]
)

cursor = connection.cursor()


# -------------------------------
# Read CSV Files
# -------------------------------

users_df = pd.read_csv("users.csv")

events_df = pd.read_csv("events.csv")


# -------------------------------
# Insert Users
# -------------------------------

for row in users_df.itertuples(index=False):

    cursor.execute(
        """
        INSERT INTO users
        (user_id, signup_date, country)
        VALUES (%s, %s, %s)
        """,
        (
            row.user_id,
            row.signup_date,
            row.country
        )
    )


# -------------------------------
# Insert Events
# -------------------------------

for row in events_df.itertuples(index=False):

    cursor.execute(
        """
        INSERT INTO events
        (event_id,user_id,event_type,event_timestamp)
        VALUES (%s,%s,%s,%s)
        """,
        (
            row.event_id,
            row.user_id,
            row.event_type,
            row.event_timestamp
        )
    )


# Save changes
connection.commit()

print("Data Imported Successfully")


cursor.close()
connection.close()