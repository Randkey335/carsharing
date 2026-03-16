from . import db

class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100))
    number = db.Column(db.String(20), unique=True)
    reserved = db.Column(db.Boolean)

class Trip(db.Model):
    __tablename__ = 'trips'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20))
    sms_code = db.Column(db.String(10))
    car_model = db.Column(db.String(100))
    car_number = db.Column(db.String(20))
    fuel_level = db.Column(db.String(10))