from flask import Blueprint, jsonify, request, abort
from werkzeug.security import check_password_hash
from .models import Flight, Passenger

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/flights', methods=['GET'])
def get_flights():
    flights = Flight.query.all()
    result = [{
        'flight_number': f.flight_number,
        'departure_airport': f.departure_airport,
        'arrival_airport': f.arrival_airport,
        'departure_time': f.departure_time,
        'duration': f.duration
    } for f in flights]
    return jsonify(result)

@bp.route('/miles', methods=['GET'])
def get_miles():
    phone = request.args.get('phone')
    password = request.args.get('password')
    if not phone or not password:
        abort(401, description='Missing credentials')
    passenger = Passenger.query.filter_by(phone=phone).first()
    if not passenger or not check_password_hash(passenger.password, password):
        abort(401, description='Invalid credentials')
    return jsonify({
        'miles': passenger.miles,
        'phone': passenger.phone
    })