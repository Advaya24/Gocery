import json

from flask import Flask
from flask import render_template
from flask import request
import requests

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello_world():
    content = {'text': "Hello from Flask"}

    return render_template('gocery/Index.html', content=content), 200


@app.route('/', methods=['POST'])
def got_location():
    return request.form['location']


if __name__ == '__main__':
    app.run()
