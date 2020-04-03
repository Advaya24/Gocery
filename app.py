from typing import Optional

from flask import Flask
from flask import render_template
from flask import request
import googlemaps

app = Flask(__name__)

gmaps = googlemaps.Client(key='AIzaSyB2FzTtHLFQEjOYzOXze6pXopbFUZlaR5o')


def get_place_id(name: str, location: Optional[str]) -> str:
    """Get the place id for place of given name and location

    Returns place id as string for candidate with highest probability, or empty string if no candidate found
    """
    place_id = str
    result = ''
    if location is None:
        result = gmaps.find_place(name, 'textquery')
    else:
        result = gmaps.find_place(name + ', ' + location, 'textquery')
    if len(result['candidates']) >= 1:
        place_id = result['candidates'][0]['place_id']
    return place_id


@app.route('/', methods=['GET'])
def hello_world():
    content = {'text': "Hello from Flask"}

    return render_template('gocery/Index.html', content=content), 200


@app.route('/stores', methods=['POST'])
def got_location():
    locations = {'location': request.form['location']}
    locations['possible_location'] = gmaps.place(
        get_place_id(locations['location'], None))
    return render_template('gocery/Listing.html', locations=locations)


@app.route('/select', methods=['POST'])
def selected_store():
    content = {}
    return render_template('gocery/Store.html', content=content)


if __name__ == '__main__':
    app.run()
