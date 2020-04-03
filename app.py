from typing import Optional

from flask import Flask
from flask import render_template
from flask import request
import googlemaps

app = Flask(__name__)

gmaps = googlemaps.Client(key=***REMOVED***)


def get_place_ID(name: str, location: Optional[str]) -> str:
    """Get the place id for place of given name and location

    Returns place id as string for candidate with highest probability, or empty string if no candidate found
    """
    place_ID = str
    result = ''
    if location == None:
        result = gmaps.find_place(name, 'textquery')
    else:
        result = gmaps.find_place(name + ', ' + location, 'textquery')
    if len(result['candidates']) >= 1:
        place_ID = result['candidates'][0]['place_id']
    return place_ID

@app.route('/', methods=['GET'])
def hello_world():
    content = {'text': "Hello from Flask"}

    return render_template('gocery/Index.html', content=content), 200


@app.route('/stores', methods=['POST'])
def got_location():
    locations = {'location': request.form['location']}
    locations['possible_location'] = gmaps.place(get_place_ID(locations['location'], None))
    return render_template('gocery/Listing.html', locations=locations)


if __name__ == '__main__':
    app.run()
