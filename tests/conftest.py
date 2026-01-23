"""
Pytest Configuration and Fixtures
"""

import sys
import os
import pytest
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


@pytest.fixture
def app():
    """Create application instance for testing"""
    app = create_app('testing')
    yield app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def reset_test_data(app):
    """Reset test data before each test"""
    # Setup: Create fresh test data directory
    test_data_dir = os.path.join(os.path.dirname(__file__), '..', 'test_data')
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir, exist_ok=True)

    # Create required JSON files with empty data
    import json
    json_files = ['users.json', 'medicines.json', 'patients.json', 'doctors.json',
                  'suppliers.json', 'departments.json', 'stores.json', 'purchases.json',
                  'consumption.json', 'transfers.json', 'history.json']

    for json_file in json_files:
        file_path = os.path.join(test_data_dir, json_file)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump({}, f)

    yield

    # Teardown: Clean up test data
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)


@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client"""
    # First, register a test user
    client.post('/auth/register', data={
        'username': 'testuser',
        'password': 'Test123!',
        'role': 'admin',
        'department_id': '01'
    })

    # Then login
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'Test123!'
    }, follow_redirects=True)

    return client


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_data_dir():
    """Create test data directory"""
    import tempfile
    import shutil

    test_data_dir = tempfile.mkdtemp()
    yield test_data_dir

    # Cleanup
    shutil.rmtree(test_data_dir, ignore_errors=True)


@pytest.fixture
def authenticated_admin_client(client):
    """Create authenticated admin test client"""
    # Login with admin credentials
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': '@Xx123456789xX@'
    }, follow_redirects=True)

    assert response.status_code == 200
    return client


@pytest.fixture
def authenticated_department_client(client):
    """Create authenticated department user test client"""
    # Login with department user credentials
    response = client.post('/auth/login', data={
        'username': 'pharmacy',
        'password': 'pharmacy123'
    }, follow_redirects=True)

    assert response.status_code == 200
    return client

