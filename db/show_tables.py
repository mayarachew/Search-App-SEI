import mysql.connector


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="451278",
  database="sei"
)

mycursor = mydb.cursor()

mycursor.execute("DESCRIBE acts")

print("Acts table:")
for x in mycursor:
  print(x)

print("\nAnnouncements table:")
mycursor.execute("DESCRIBE announcements")

for x in mycursor:
  print(x)