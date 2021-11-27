
from flask import Flask, escape, request, jsonify, g
from database import mycursor
app = Flask(__name__)



# mycursor.execute("CREATE DATABASE mydatabase")

def getCamera(json_obj):
    return json_obj, 200

if __name__ == '__main__':
    # create_table()
    app.run(debug=True)
