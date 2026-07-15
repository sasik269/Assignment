import mysql.connector
import pandas as pd

from config import DB_CONFIG
from queries import (
    USER_SEGMENT_QUERY,
    CHURN_QUERY,
    COMMON_EVENT_QUERY
)


def connect_database():

    connection = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )

    return connection


def create_user_segments(cursor):

    cursor.execute(USER_SEGMENT_QUERY)


def get_churn_rate(cursor):

    cursor.execute(CHURN_QUERY)

    result = cursor.fetchall()

    columns = [i[0] for i in cursor.description]

    return pd.DataFrame(result, columns=columns)


def get_common_event(cursor):

    cursor.execute(COMMON_EVENT_QUERY)

    result = cursor.fetchall()

    columns = [i[0] for i in cursor.description]

    return pd.DataFrame(result, columns=columns)


def main():

    connection = connect_database()

    cursor = connection.cursor()

    print("="*60)
    print("Creating User Segments...")
    print("="*60)

    create_user_segments(cursor)

    print("Done\n")

    print("="*60)
    print("Churn Analysis")
    print("="*60)

    churn_df = get_churn_rate(cursor)

    print(churn_df)

    print()

    print("="*60)
    print("Most Common Event (30-60 Days)")
    print("="*60)

    common_df = get_common_event(cursor)

    print(common_df)

    cursor.close()

    connection.close()


if __name__ == "__main__":
    main()