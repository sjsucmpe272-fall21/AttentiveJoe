import mysql.connector
mydb = mysql.connector.connect(
  host="indeeddb.c6sybz1oeksr.us-east-2.rds.amazonaws.com",
  user="root",
  password="indeed273",
  database="attentivejoe"
)

print(mydb)

mycursor = mydb.cursor()

