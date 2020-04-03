from flask import Flask
from flask import render_template
from flask import request
import googlemaps

app = Flask(__name__)

gmaps = googlemaps.Client(key='')


@app.route('/', methods=['GET'])
def hello_world():
    content = {'text': "Hello from Flask"}

    return render_template('gocery/Index.html', content=content), 200


@app.route('/stores', methods=['POST'])
def got_location():
    locations = {'location': request.form['location']}
    return render_template('gocery/Listing.html', locations=locations)


if __name__ == '__main__':
    app.run()
