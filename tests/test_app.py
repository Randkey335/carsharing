import pytest
import sys
import os
from flask import Flask
from flask import render_template
from werkzeug.security import generate_password_hash

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
from app.models import Flight, Passenger
from app.routes import bp


@pytest.fixture
def app():
    """Create application for testing."""
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    db.init_app(app)
    app.register_blueprint(bp)

    @app.get('/')
    def index():
        return render_template('index.html')
    
    # Add error handlers
    @app.errorhandler(401)
    def unauthorized(e):
        from flask import jsonify
        return jsonify(error=str(e.description)), 401
    
    @app.errorhandler(404)
    def not_found(e):
        from flask import jsonify
        return jsonify(error="Not found"), 404
    
    with app.app_context():
        db.create_all()
        # Add test data
        flights = [
            Flight(id=1, flight_number='1', departure_airport='Анапа', arrival_airport='Внуково', departure_time='10:00', duration='4:55'),
            Flight(id=2, flight_number='2', departure_airport='Шереметьево', arrival_airport='Калининград', departure_time='11:20', duration='2:55'),
            Flight(id=3, flight_number='3', departure_airport='Пулково', arrival_airport='Шереметьево', departure_time='09:05', duration='1:05'),
            Flight(id=4, flight_number='4', departure_airport='Саратов', arrival_airport='Толмачево', departure_time='11:25', duration='5:02'),
        ]
        passengers = [
            Passenger(id=1, phone='+7957285726', password=generate_password_hash('aercd112'), miles=123),
            Passenger(id=2, phone='+7957385621', password=generate_password_hash('okliuj91'), miles=91),
            Passenger(id=3, phone='+79175715718', password=generate_password_hash('09ikjhbn12'), miles=192),
        ]
        for flight in flights:
            db.session.add(flight)
        for passenger in passengers:
            db.session.add(passenger)
        db.session.commit()
        
    yield app
    
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestFlights:
    """Tests for flights API."""

    def test_index_page(self, client):
        """Test that HTML page is available."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_get_flights(self, client):
        """Test getting all flights."""
        response = client.get('/api/flights')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 4
        assert data[0]['flight_number'] == '1'
        assert data[0]['departure_airport'] == 'Анапа'
        assert data[0]['arrival_airport'] == 'Внуково'
        assert data[0]['departure_time'] == '10:00'
        assert data[0]['duration'] == '4:55'
    
    def test_get_flights_structure(self, client):
        """Test flights response structure."""
        response = client.get('/api/flights')
        data = response.get_json()
        assert isinstance(data, list)
        flight = data[0]
        required_fields = ['flight_number', 'departure_airport', 'arrival_airport', 'departure_time', 'duration']
        for field in required_fields:
            assert field in flight
    
    def test_get_flights_all_fields(self, client):
        """Test that all flights have correct data."""
        response = client.get('/api/flights')
        data = response.get_json()
        assert data[3]['flight_number'] == '4'
        assert data[3]['departure_airport'] == 'Саратов'
        assert data[3]['duration'] == '5:02'


class TestPassengers:
    """Tests for miles API with authentication."""
    
    def test_get_miles_valid_credentials(self, client):
        """Test getting miles with valid credentials."""
        response = client.get('/api/miles?phone=%2B7957285726&password=aercd112')
        assert response.status_code == 200
        data = response.get_json()
        assert data['miles'] == 123
        assert data['phone'] == '+7957285726'
    
    def test_get_miles_valid_credentials_second_passenger(self, client):
        """Test getting miles for second passenger."""
        response = client.get('/api/miles?phone=%2B7957385621&password=okliuj91')
        assert response.status_code == 200
        data = response.get_json()
        assert data['miles'] == 91
    
    def test_get_miles_valid_credentials_third_passenger(self, client):
        """Test getting miles for third passenger."""
        response = client.get('/api/miles?phone=%2B79175715718&password=09ikjhbn12')
        assert response.status_code == 200
        data = response.get_json()
        assert data['miles'] == 192
    
    def test_get_miles_invalid_password(self, client):
        """Test getting miles with wrong password."""
        response = client.get('/api/miles?phone=%2B7957285726&password=wrongpassword')
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid credentials' in data['error']
    
    def test_get_miles_invalid_phone(self, client):
        """Test getting miles with wrong phone."""
        response = client.get('/api/miles?phone=%2B7999999999&password=aercd112')
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_get_miles_missing_phone(self, client):
        """Test getting miles without phone parameter."""
        response = client.get('/api/miles?password=aercd112')
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'Missing credentials' in data['error']
    
    def test_get_miles_missing_password(self, client):
        """Test getting miles without password parameter."""
        response = client.get('/api/miles?phone=%2B7957285726')
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'Missing credentials' in data['error']
    
    def test_get_miles_missing_both(self, client):
        """Test getting miles without both parameters."""
        response = client.get('/api/miles')
        assert response.status_code == 401


class TestModels:
    """Tests for database models."""
    
    def test_flight_model_creation(self, app):
        """Test Flight model can be created."""
        with app.app_context():
            flight = Flight(
                flight_number='TEST123',
                departure_airport='TestCity1',
                arrival_airport='TestCity2',
                departure_time='12:00',
                duration='2:30'
            )
            db.session.add(flight)
            db.session.commit()
            
            retrieved = Flight.query.filter_by(flight_number='TEST123').first()
            assert retrieved is not None
            assert retrieved.departure_airport == 'TestCity1'
    
    def test_passenger_model_creation(self, app):
        """Test Passenger model can be created."""
        with app.app_context():
            passenger = Passenger(
                phone='+79999999999',
                password=generate_password_hash('testpass123'),
                miles=500
            )
            db.session.add(passenger)
            db.session.commit()
            
            retrieved = Passenger.query.filter_by(phone='+79999999999').first()
            assert retrieved is not None
            assert retrieved.password != 'testpass123'
            assert retrieved.miles == 500
    
    def test_flight_unique_number(self, app):
        """Test that flight number must be unique."""
        with app.app_context():
            flight1 = Flight(
                flight_number='DUP123',
                departure_airport='City1',
                arrival_airport='City2',
                departure_time='10:00',
                duration='2:00'
            )
            db.session.add(flight1)
            db.session.commit()
            
            flight2 = Flight(
                flight_number='DUP123',
                departure_airport='City3',
                arrival_airport='City4',
                departure_time='11:00',
                duration='2:30'
            )
            db.session.add(flight2)
            
            with pytest.raises(Exception):  # Will raise IntegrityError for duplicate
                db.session.commit()
    
    def test_passenger_unique_phone(self, app):
        """Test that phone must be unique for passengers."""
        with app.app_context():
            passenger1 = Passenger(
                phone='+78888888888',
                password=generate_password_hash('pass1'),
                miles=100
            )
            db.session.add(passenger1)
            db.session.commit()
            
            passenger2 = Passenger(
                phone='+78888888888',
                password=generate_password_hash('pass2'),
                miles=200
            )
            db.session.add(passenger2)
            
            with pytest.raises(Exception):  # Will raise IntegrityError for duplicate
                db.session.commit()


class TestErrorHandlers:
    """Tests for error handlers."""
    
    def test_404_not_found(self, client):
        """Test 404 error handler."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_401_unauthorized_response_format(self, client):
        """Test 401 error response format."""
        response = client.get('/api/miles?phone=%2B7999999999&password=wrongpass')
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data


class TestIntegration:
    """Integration tests."""
    
    def test_full_workflow(self, client):
        """Test complete workflow: get flights and then get miles."""
        # Get flights
        flights_response = client.get('/api/flights')
        assert flights_response.status_code == 200
        flights = flights_response.get_json()
        assert len(flights) == 4
        
        # Get miles with authentication
        miles_response = client.get('/api/miles?phone=%2B7957285726&password=aercd112')
        assert miles_response.status_code == 200
        miles_data = miles_response.get_json()
        assert miles_data['miles'] == 123
    
    def test_multiple_passengers_different_miles(self, client):
        """Test that different passengers have different miles."""
        pass1 = client.get('/api/miles?phone=%2B7957285726&password=aercd112').get_json()
        pass2 = client.get('/api/miles?phone=%2B7957385621&password=okliuj91').get_json()
        pass3 = client.get('/api/miles?phone=%2B79175715718&password=09ikjhbn12').get_json()
        
        assert pass1['miles'] == 123
        assert pass2['miles'] == 91
        assert pass3['miles'] == 192
        assert pass1['miles'] != pass2['miles'] != pass3['miles']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
