import json

from flask import Flask, escape, request, jsonify, g

import controller


app = Flask(__name__)


@app.route('/camera', methods=['POST'])
def create_bitly():
    json_obj = request.get_json()
    return controller.getCamera(json_obj)


if __name__ == '__main__':
    app.run(debug=True)
