from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)

    with app.app_context():
        # Импортируем модели до создания таблиц
        from .models import Flight, Passenger
        db.create_all()

        # Ensure legacy DB schema supports hashed passwords.
        try:
            db.session.execute(text('ALTER TABLE passengers ALTER COLUMN password TYPE VARCHAR(255)'))
            db.session.commit()
        except Exception:
            db.session.rollback()
        
        # Заполняем начальными данными, если таблицы пусты
        if Flight.query.count() == 0:
            flights_data = [
                {'id': 1, 'flight_number': '1', 'departure_airport': 'Анапа', 'arrival_airport': 'Внуково', 'departure_time': '10:00', 'duration': '4:55'},
                {'id': 2, 'flight_number': '2', 'departure_airport': 'Шереметьево', 'arrival_airport': 'Калининград', 'departure_time': '11:20', 'duration': '2:55'},
                {'id': 3, 'flight_number': '3', 'departure_airport': 'Пулково', 'arrival_airport': 'Шереметьево', 'departure_time': '09:05', 'duration': '1:05'},
                {'id': 4, 'flight_number': '4', 'departure_airport': 'Саратов', 'arrival_airport': 'Толмачево', 'departure_time': '11:25', 'duration': '5:02'},
            ]
            for f in flights_data:
                flight = Flight(id=f['id'], flight_number=f['flight_number'], departure_airport=f['departure_airport'], arrival_airport=f['arrival_airport'], departure_time=f['departure_time'], duration=f['duration'])
                db.session.add(flight)
            db.session.commit()
            
        if Passenger.query.count() == 0:
            passengers_data = [
                {'id': 1, 'phone': '+7957285726', 'password': 'aercd112', 'miles': 123},
                {'id': 2, 'phone': '+7957385621', 'password': 'okliuj91', 'miles': 91},
                {'id': 3, 'phone': '+79175715718', 'password': '09ikjhbn12', 'miles': 192},
            ]
            for p in passengers_data:
                passenger = Passenger(
                    id=p['id'],
                    phone=p['phone'],
                    password=generate_password_hash(p['password']),
                    miles=p['miles']
                )
                db.session.add(passenger)
            db.session.commit()

        # One-time migration for legacy plaintext passwords.
        migrated = False
        for passenger in Passenger.query.all():
            if passenger.password and '$' not in passenger.password:
                passenger.password = generate_password_hash(passenger.password)
                migrated = True
        if migrated:
            db.session.commit()

        from . import routes
        app.register_blueprint(routes.bp)

        @app.get('/')
        def index():
            return render_template('index.html')

        @app.errorhandler(401)
        def unauthorized(e):
            return jsonify(error=str(e.description)), 401
        @app.errorhandler(404)
        def not_found(e):
            return jsonify(error="Not found"), 404

    return app 