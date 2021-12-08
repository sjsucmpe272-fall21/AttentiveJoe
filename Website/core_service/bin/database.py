import mysql.connector

def get_db_connection():
  mydb = mysql.connector.connect(
    host="indeeddb.c6sybz1oeksr.us-east-2.rds.amazonaws.com",
    user="root",
    password="indeed273",
    database="attentivejoe"
    # host="localhost",
    # user="root",
    # password="root@123",
    # database="cmpe272"
  )
  print(mydb)
  return mydb
  # mycursor = mydb.cursor()
  # return mycursor

get_db_connection()