import pymysql
from mysql.connector import Error
import mysql.connector as mariadb
 
#==============  SET UP ============
usermysql="root"
passmysql="root"
hostmysql="localhost"
database="hotel"

try:
    connection = mariadb.connect(host=hostmysql, user=usermysql, passwd=passmysql, db=database,connect_timeout=1000,autocommit=True)
    print("Connected to MySQL DOCKET ATP mp")
except Error as e:
    print("Error while connecting to MySQL Docker DBLivros", e)   


  
sql = """
SELECT count(*) as total from hotel; 
"""
try:
    cursor = connection.cursor()
    cursor.execute(sql)
    records = cursor.fetchall()
    for row in records:
        print(row[0]) 
except:
    print ("Error: unable to SELECT count(*) as total from hotel")
    
