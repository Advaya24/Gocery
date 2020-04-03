from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    content = {'text': "Hello from Flask"}
    return render_template('gocery/Index.html', text=content['text']), 200


if __name__ == '__main__':
    app.run()
