from . import db

class Flight(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(10), unique=True)
    departure_airport = db.Column(db.String(100))
    arrival_airport = db.Column(db.String(100))
    departure_time = db.Column(db.String(10))
    duration = db.Column(db.String(10))

class Passenger(db.Model):
    __tablename__ = 'passengers'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(50))
    miles = db.Column(db.Integer)