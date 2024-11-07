'''
conda install sqlalchemy
conda install mysqlclient
'''

import mysql.connector


mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="451278"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE sei")

