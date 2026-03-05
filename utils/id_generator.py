counter_booking = 1
counter_ticket = 1
counter_trip = 1
counter_round = 1
counter_payment = 1
def generate_booking_id():
    global counter_booking
    cid = f"B-{counter_booking:03}"
    counter_booking += 1
    return cid
def generate_ticket_id():
    global counter_ticket
    cid = f"T-{counter_ticket:03}"
    counter_ticket += 1
    return cid
def generate_trip_id():
    global counter_trip
    cid = f"TR-{counter_trip:03}"
    counter_trip += 1
    return cid
def generate_round_id():
    global counter_round
    cid = f"R-{counter_round:03}"
    counter_round += 1
    return cid
def generate_payment_id():
    global counter_payment
    cid = f"P-{counter_payment:03}"
    counter_payment += 1
    return cid