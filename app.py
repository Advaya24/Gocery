from typing import Optional, Dict

from flask import Flask
from flask import render_template
from flask import request
from flask_mail import Mail, Message
import googlemaps
from datetime import datetime, timedelta
import json
import re

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'justformuftnetflix@gmail.com'
app.config['MAIL_PASSWORD'] = 'justfornetflix123'
app.config['MAIL_DEFAULT_SENDER'] = 'justformuftnetflix@gmail.com'

mail = Mail(app)

gmaps = googlemaps.Client(key='AIzaSyB2FzTtHLFQEjOYzOXze6pXopbFUZlaR5o')

# Variable Declaration Center...
stores = []
store_ids = []
toggle = 5
timing = []
store_id_global = ''
slot_time_global = ''


def date_converter(obj):
    if isinstance(obj, datetime):
        return obj.__str__()


def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta


def am_pm_to_24_hour(input_time):
    array = input_time.split()
    array[1] = array[1].strip()
    if array[1] == "AM":
        return array[0]
    # PM Region...
    recon1 = array[0].split(':')
    hours = recon1[0]
    minute = recon1[1]
    hours = hours.strip()
    minute = minute.strip()
    check1 = int(hours)
    check1 = (check1 + 12) % 24
    hours = str(check1)
    input_time = hours + ':' + minute
    return input_time


def to_am_pm(input_time):
    array = input_time.split(':')
    hours = array[0]
    minute = array[1]
    second = array[2]
    hours = hours.strip()
    minute = minute.strip()
    second = second.strip()
    check_h = int(hours)
    if check_h == 0:
        # Edge Handler
        check_h = check_h + 12
        hours = str(check_h)
        return hours + ':' + minute + " am"

    if check_h > 12:
        # PM Zone
        check_h = check_h - 12
        hours = str(check_h)
        return hours + ':' + minute + " pm"

    # AM Zone
    return hours + ':' + minute + " am"


def generate_slots(open_time: str, close_time: str, avg_time: str,
                   num_cashiers: str) -> Dict[str, int]:
    open_dt = datetime.strptime(open_time, '%H:%M %p')
    close_dt = datetime.strptime(am_pm_to_24_hour(close_time), '%H:%M')
    slots_single = [to_am_pm(str(time.time())) for time in
                    datetime_range(open_dt, close_dt,
                                   timedelta(
                                       minutes=int(
                                           avg_time)))]

    slots = {time: int(num_cashiers) * 3 for time in slots_single}

    return slots


def get_place_id(name: str, location: Optional[str]) -> Optional[str]:
    """Get the place id for place of given name and location

    Returns place id as string for candidate with highest probability, or empty
    string if no candidate found
    """
    place_id = None
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
    stores.clear()
    store_ids.clear()

    locations = {'location': request.form['location']}
    locations['possible_location'] = get_place_id(locations['location'], None)
    with open('static/stores.json', 'r') as store_file:
        store_data = json.load(store_file)
        for store in store_data.keys():
            dist_matrix = gmaps.distance_matrix(
                origins='place_id:' + locations['possible_location'],
                destinations='place_id:' + store)
            try:
                distance_str = \
                    dist_matrix['rows'][0]['elements'][0]['distance']['text']
                distance = float(re.findall('\d+\.\d+', distance_str)[0])
                if distance <= 2:
                    stores.append(store_data[store]['store_name'])
                    store_ids.append(store)
            except:
                pass
    stores_found = len(stores) > 0
    num_stores = len(stores)
    return render_template('gocery/Listing.html', locations=locations,
                           stores=stores[:10], stores_found=stores_found,
                           store_ids=store_ids[:10], num_stores=num_stores)


@app.route('/content', methods=['POST'])
def selected_store():
    global store_id_global
    selected_store_id = request.form['store_id']
    store_data = {}
    timing.clear()
    with open('static/stores.json', 'r') as store_file:
        store_data.update(json.load(store_file))

    content = {
        'store_id': selected_store_id,
        'store_name': stores[store_ids.index(selected_store_id)],
    }

    open_time = store_data[selected_store_id]['open_time']
    close_time = store_data[selected_store_id]['close_time']
    avg_time = store_data[selected_store_id]['avg_time']
    num_cashiers = store_data[selected_store_id]['num_cashiers']

    content['slots'] = generate_slots(open_time, close_time, avg_time,
                                      num_cashiers)

    slot_data = {}
    with open('static/slots.json', 'r') as slot_file:
        slot_data.update(json.load(slot_file))

    to_update = False
    if selected_store_id in slot_data:
        last_updated = datetime.fromisoformat(slot_data[selected_store_id][0])
        if last_updated.date() < datetime.today().date():
            to_update = True
        else:
            content['slots'] = slot_data[selected_store_id][1]
    else:
        to_update = True
    if to_update:
        slot_data[selected_store_id] = (
            datetime.now().isoformat(), content['slots'])
        with open('static/slots.json', 'w') as slot_file:
            json.dump(slot_data, slot_file)

    for time in content['slots'].keys():
        if content['slots'][time] > 0:
            timing.append(time)
    content['timing'] = timing
    store_id_global += selected_store_id
    return render_template('gocery/Store.html', content=content,
                           toggle=len(timing))


@app.route('/email_generator', methods=['POST'])
def email_generator():
    global slot_time_global
    # selected_store_id = store_id_global
    selected_time = request.form['selected_time']
    content = {'timing': selected_time}
    slot_time_global += selected_time
    return render_template('gocery/Mail.html', content=content)


@app.route('/sentmail', methods=['POST'])
def mail_sent():
    email_id = request.form['email']
    # is_valid = validate_email(email_id['email_id'])
    # if is_valid == 1:
    to_send = False
    email_data = {}
    with open('static/emails.json', 'r') as email_file:
        email_data.update(json.load(email_file))
        if email_id in email_data:
            # Check last access time
            diff = datetime.now() - datetime.fromisoformat(
                email_data[email_id][0])
            num_hours = diff.total_seconds() / 3600
            if num_hours >= 72:
                email_data[email_id] = [datetime.now()]
                to_send = True
        else:
            email_data[email_id] = [datetime.now()]
            to_send = True

    cust_id = 0
    if to_send:
        try:
            with open('static/id.txt', 'r') as id_file:
                cust_id += int(id_file.read())
                cust_id += 1
                msg = Message('Hello', recipients=[email_id])
                msg.body = f'Your uid is: {cust_id}'
                mail.send(msg)
                email_data[email_id].append(cust_id)
            with open('static/id.txt', 'w') as id_file:
                id_file.write(f'{cust_id}')
        except:
            to_send = False

        selected_time = slot_time_global
        selected_store_id = store_id_global
        slot_data = {}
        with open('static/slots.json', 'r') as slot_file:
            slot_data.update(json.load(slot_file))
        if selected_store_id in slot_data:
            slot_data[selected_store_id][1][selected_time] -= 1
            with open('static/slots.json', 'w') as slot_file:
                json.dump(slot_data, slot_file)

        booked_data = {}
        with open('static/booked.json', 'r') as booked_file:
            booked_data.update(json.load(booked_file))
        to_update_bookings = True
        if selected_store_id in booked_data:
            if datetime.fromisoformat(booked_data[selected_store_id][
                                          0]).date() == datetime.today().date():
                to_update_bookings = False
        if to_update_bookings:
            booked_data[selected_store_id] = (
                datetime.today().isoformat(), [(cust_id, selected_time)])
        else:
            booked_data[selected_store_id][1].append((cust_id, selected_time))
        with open('static/booked.json', 'w') as booked_file:
            json.dump(booked_data, booked_file)

    if to_send:
        with open('static/emails.json', 'w') as email_file:
            json.dump(email_data, email_file, default=date_converter)

    return render_template('gocery/MailConf.html', to_send=to_send,
                           email_id=email_id)


@app.route('/providers', methods=['GET'])
def store_welcome():
    return render_template('gocery/StoreWelcome.html')


@app.route('/providers/register', methods=['POST'])
def store_registration():
    times = []
    hours = []
    for i in range(1, 13):
        hours.append(str(i))
    minutes = [':00', ':30']

    for section in [' am', ' pm']:
        for hour in hours:
            for minute in minutes:
                times.append(hour + minute + section)
    average_times = [15, 30, 45, 60]
    return render_template('gocery/Registration.html', times=times,
                           average_times=average_times)


@app.route('/providers/register/done', methods=['POST'])
def store_register():
    store_data = {}
    store_id = ''
    with open('static/stores.json', 'r') as store_file:
        store_data.update(json.load(store_file))
        store_name = request.form['store_name']
        store_address = request.form['store_address']
        open_time = request.form['open_time']
        close_time = request.form['close_time']
        avg_time = request.form['avg_time']
        num_cashiers = request.form['num_cashiers']
        store_dict = {
            'store_name': store_name,
            'store_address': store_address,
            'open_time': open_time,
            'close_time': close_time,
            'avg_time': avg_time,
            'num_cashiers': num_cashiers
        }
        place_id = get_place_id(store_address, None)
        if place_id is not None:
            store_id += place_id
        else:
            return 'Invalid address', 400
        store_data[store_id] = store_dict
    with open('static/stores.json', 'w') as store_file:
        json.dump(store_data, store_file)
    return render_template('gocery/RegistrationSuccess.html', store_id=store_id)


@app.route('/providers/checkin', methods=['POST'])
def check_in():
    return render_template('gocery/CheckIn.html')


@app.route('/providers/checkin/done', methods=['POST'])
def checked_in():
    invalid_store_id = False
    slot_found = False
    store_id = request.form['store_id']
    customer_id = request.form['customer_id']
    booking_data = {}
    time_slot = ''
    with open('static/booked.json', 'r') as booked_file:
        booking_data.update(json.load(booked_file))
    store_data = {}
    with open('static/stores.json', 'r') as store_file:
        store_data.update(json.load(store_file))
    booking_lst = []
    dt = datetime.fromisoformat(
        booking_data[store_id][0]).date()
    if store_id not in booking_data:
        invalid_store_id = True
    elif dt == datetime.today().date():
        booking_lst += booking_data[store_id][1]
    for tup in booking_lst:
        if tup[0] == int(customer_id):
            time_slot += tup[1]
            slot_found = True
    slot_duration = store_data[store_id]['avg_time']

    return render_template('gocery/CheckedIn.html',
                           invalid_store_id=invalid_store_id,
                           slot_found=slot_found, customer_id=customer_id,
                           time_slot=time_slot, slot_duration=slot_duration)


if __name__ == '__main__':
    app.run()
