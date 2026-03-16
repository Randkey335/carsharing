from flask import Blueprint, jsonify, request, abort
from .models import Car, Trip

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/cars/free', methods=['GET'])
def free_cars():
    cars = Car.query.filter_by(reserved=False).all()
    result = [{'id': c.id, 'model': c.model, 'number': c.number} for c in cars]
    return jsonify(result)

@bp.route('/cars/<int:car_id>', methods=['GET'])
def car_detail(car_id):
    phone = request.args.get('phone')
    code = request.args.get('code')
    if not phone or not code:
        abort(401, description='Missing credentials')
    trip = Trip.query.filter_by(phone=phone, sms_code=code).first()
    if not trip:
        abort(401, description='Invalid credentials')
    car = Car.query.get(car_id)
    if not car:
        abort(404, description='Car not found')
    last_trip = Trip.query.filter_by(car_model=car.model, car_number=car.number).order_by(Trip.id.desc()).first()
    fuel = last_trip.fuel_level if last_trip else None
    return jsonify({
        'model': car.model,
        'number': car.number,
        'fuel_level': fuel
    })