

from google.cloud import bigquery
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="shammibaba",
  database="NFT"
)

# Construct a BigQuery client object.
client = bigquery.Client()
QUERY = (
    """select count(t3.token_address)cnt,address from 
    (`bigquery-public-data.crypto_ethereum.contracts` t2 join `bigquery-public-data.crypto_ethereum.token_transfers` t3 
    on t2.address = t3.token_address) 
    where t2.is_erc721 = TRUE group by t2.address order by cnt desc
"""
    # 'SELECT count(*),address FROM  `bigquery-public-data.crypto_ethereum.contracts` '
    # 'WHERE is_erc721 = TRUE group by address'
    )

query_job = client.query(QUERY)  # Make an API request.

mycursor = mydb.cursor()
# mycursor.execute("CREATE DATABASE NFT")
mycursor.execute("CREATE table test (transactions int, address VARCHAR(255))")

for row in query_job:
    # Row values can be accessed by field name or index.
    sql = "INSERT INTO test (transactions, address) VALUES (%s, %s)"
    val = (str(row[0]), row[1])
    mycursor.execute(sql, val)


mydb.commit()
print(mycursor.rowcount, "was inserted.")