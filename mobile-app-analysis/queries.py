# ----------------------------------------------
# STEP 1 : USER SEGMENTATION
# ----------------------------------------------

USER_SEGMENT_QUERY = """

CREATE TEMPORARY TABLE user_segments AS

SELECT

    u.user_id,

    SUM(
        CASE
            WHEN e.event_type='app_open'
            THEN 1
            ELSE 0
        END
    ) AS app_open_count,

    SUM(
        CASE
            WHEN e.event_type='purchase'
            THEN 1
            ELSE 0
        END
    ) AS purchase_count,

    CASE

        WHEN
            SUM(CASE WHEN e.event_type='app_open' THEN 1 ELSE 0 END)>=10

        AND
            SUM(CASE WHEN e.event_type='purchase' THEN 1 ELSE 0 END)>=3

        THEN 'Highly Engaged'

        ELSE 'Low Engagement'

    END AS segment

FROM users u

LEFT JOIN events e

ON u.user_id=e.user_id

AND e.event_timestamp BETWEEN
u.signup_date
AND DATE_ADD(u.signup_date,INTERVAL 7 DAY)

GROUP BY u.user_id;

"""

# ----------------------------------------------
# STEP 2A : CHURN RATE
# ----------------------------------------------

CHURN_QUERY = """

SELECT

    us.segment,

    COUNT(*) AS total_users,

    SUM(

        CASE

            WHEN latest.last_open IS NULL
            OR latest.last_open < DATE_SUB(CURDATE(),INTERVAL 30 DAY)

            THEN 1

            ELSE 0

        END

    ) AS churned_users,

    ROUND(

        SUM(

            CASE

                WHEN latest.last_open IS NULL
                OR latest.last_open < DATE_SUB(CURDATE(),INTERVAL 30 DAY)

                THEN 1

                ELSE 0

            END

        )*100.0/COUNT(*),

        2

    ) AS churn_rate_percent

FROM user_segments us

LEFT JOIN

(

    SELECT

        user_id,

        MAX(event_timestamp) AS last_open

    FROM events

    WHERE event_type='app_open'

    GROUP BY user_id

) latest

ON us.user_id=latest.user_id

GROUP BY us.segment;

"""



# ----------------------------------------------
# STEP 2B : MOST COMMON EVENT
# ----------------------------------------------

COMMON_EVENT_QUERY = """

SELECT

    e.event_type,

    COUNT(*) AS frequency

FROM user_segments us

JOIN users u

ON us.user_id=u.user_id

JOIN events e

ON e.user_id=u.user_id

WHERE

    us.segment='Highly Engaged'

AND

    e.event_timestamp BETWEEN
    DATE_ADD(u.signup_date,INTERVAL 30 DAY)

AND
    DATE_ADD(u.signup_date,INTERVAL 60 DAY)

GROUP BY e.event_type

ORDER BY frequency DESC

LIMIT 1;

"""