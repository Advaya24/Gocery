from typing import Optional

from flask import Flask
from flask import render_template
from flask import request
from flask_mail import Mail, Message
import googlemaps

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'justformuftnetflix@gmail.com'
app.config['MAIL_PASSWORD'] = 'justfornetflix123'
app.config['MAIL_DEFAULT_SENDER'] = 'justformuftnetflix@gmail.com'

mail = Mail(app)

gmaps = googlemaps.Client(key='AIzaSyB2FzTtHLFQEjOYzOXze6pXopbFUZlaR5o')

#Variable Declaration Center...
stores = []
toggle = 5
timing = []

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

    for i in range(10):
        stores.append("Store : " + str(i + 1))

    recon = len(stores) # Length of the stores variable!

    locations = {'location': request.form['location']}
    locations['possible_location'] = gmaps.place(
        get_place_id(locations['location'], None))
    return render_template('gocery/Listing.html', locations=locations, stores=stores, recon = recon)


@app.route('/content', methods=['POST'])
def selected_store():
    i = request.form["Button"]
    content = {'store' : stores[int(i)]}

    for i in range(toggle):
        timing.append(i)
    content['timing'] = timing
    return render_template('gocery/Store.html', content=content, toggle = toggle)

@app.route('/email_generator', methods=['POST'])
def email_generator():
    i = request.form["Button"]
    content = {'timing' : timing[int(i)]}
    return render_template('gocery/Mail.html', content=content)

@app.route('/sentmail', methods=['POST'])
def mail_sent():
    email_id = {'email_id' : request.form['email']}
    msg = Message('Hello', recipients=[email_id['email_id']])
    mail.send(msg)
    return render_template('gocery/MailConf.html', email_id=email_id)




if __name__ == '__main__':
    app.run()
