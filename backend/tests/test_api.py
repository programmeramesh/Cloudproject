import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_login(client):
    """Test login endpoint"""
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'access_token' in data


def test_login_invalid(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'username': 'invalid',
        'password': 'invalid'
    })
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False


def test_get_metrics(client):
    """Test get metrics endpoint"""
    response = client.get('/api/metrics')
    assert response.status_code == 200
    data = response.get_json()
    assert 'metrics' in data


def test_get_current_metrics(client):
    """Test get current metrics endpoint"""
    response = client.get('/api/metrics/current')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'metrics' in data


def test_get_resources(client):
    """Test get resources endpoint"""
    response = client.get('/api/resources')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'allocation' in data


def test_get_system_info(client):
    """Test get system info endpoint"""
    response = client.get('/api/system/info')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'system_info' in data


def test_404_error(client):
    """Test 404 error handling"""
    response = client.get('/api/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
