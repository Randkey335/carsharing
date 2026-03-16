from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)

    with app.app_context():
        # Импортируем модели до создания таблиц
        from .models import Car, Trip
        db.create_all()
        
        # Заполняем начальными данными, если таблицы пусты
        if Car.query.count() == 0:
            cars_data = [
                {'id': 1, 'model': 'Kia Rio', 'number': 'о787оо50', 'reserved': True},
                {'id': 2, 'model': 'VW Polo', 'number': 'е887ео777', 'reserved': False},
                {'id': 3, 'model': 'VW Polo', 'number': 'м761он797', 'reserved': True},
                {'id': 4, 'model': 'Toyota RAV4', 'number': 'н761он797', 'reserved': True},
            ]
            for c in cars_data:
                car = Car(id=c['id'], model=c['model'], number=c['number'], reserved=c['reserved'])
                db.session.add(car)
            db.session.commit()
            
        if Trip.query.count() == 0:
            trips_data = [
                {'id': 1, 'phone': '+79846274627', 'sms_code': '1420', 'car_model': 'Kia Rio', 'car_number': 'о787оо50', 'fuel_level': '76%'},
                {'id': 2, 'phone': '+79175628572', 'sms_code': '1100', 'car_model': 'VW Polo', 'car_number': 'м761он797', 'fuel_level': '56%'},
                {'id': 3, 'phone': '+7916552451', 'sms_code': '1100', 'car_model': 'Toyota RAV4', 'car_number': 'н761он797', 'fuel_level': '11%'},
            ]
            for t in trips_data:
                trip = Trip(id=t['id'], phone=t['phone'], sms_code=t['sms_code'], car_model=t['car_model'], car_number=t['car_number'], fuel_level=t['fuel_level'])
                db.session.add(trip)
            db.session.commit()

        from . import routes
        app.register_blueprint(routes.bp)

        @app.errorhandler(401)
        def unauthorized(e):
            return jsonify(error=str(e.description)), 401
        @app.errorhandler(404)
        def not_found(e):
            return jsonify(error="Not found"), 404

    return app