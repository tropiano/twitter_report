from site import USER_BASE
import psycopg2
import os
import sys

DB_USER = os.environ.get('DB_USER', default='postgres')
DB_PWD = os.environ.get('DB_PWD', default='postgres')
data_file = sys.argv[1]

conn = psycopg2.connect(database="twitter_report",
                        user=DB_USER,
                        password=DB_PWD,
                        host='127.0.0.1',
                        port='5432'
                        )

conn.autocommit = False
cursor = conn.cursor()

sql2 = f'''COPY report_twitter_user(id,user_name)
FROM '{data_file}/report_twitter_user.csv'
DELIMITER ','
CSV HEADER;'''
cursor.execute(sql2)

sql3 = f'''COPY report_twitter_user_stats(id,tweets,retweets,likes,replies,followers,timestamp,user_id_id)
FROM '{data_file}/report_twitter_user_stats.csv'
DELIMITER ','
CSV HEADER;'''
cursor.execute(sql3)

sql4 = '''select * from report_twitter_user_stats;'''
cursor.execute(sql4)

for i in cursor.fetchall():
    print(i)

conn.commit()
conn.close()
