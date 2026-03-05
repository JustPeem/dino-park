from datetime import datetime

_booking_counter = {}
_trip_counter = {}

from datetime import datetime

_booking_counter = {}

def generate_booking_id():

    today = datetime.now().strftime("%Y%m%d")

    if today not in _booking_counter:
        _booking_counter[today] = 1
    else:
        _booking_counter[today] += 1

    counter = _booking_counter[today]

    return f"B-{today}-{counter:03d}"


trip_counter = 1

def generate_trip_id():
    global trip_counter
    trip_id = f"T-{trip_counter:03d}"
    trip_counter += 1
    return trip_id

_payment_counter = {}

def generate_payment_id() -> str:
    today = datetime.now().strftime("%Y%m%d")

    if today not in _payment_counter:
        _payment_counter[today] = 1
    else:
        _payment_counter[today] += 1

    number = _payment_counter[today]

    return f"P-{today}-{number:03d}"