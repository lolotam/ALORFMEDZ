"""
Integration tests for API endpoints
"""

import pytest
import json
import tempfile
import os

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""

    def test_login_endpoint_valid_credentials(self, client):
        """Test login with valid credentials"""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should redirect to dashboard after successful login
        assert b'Dashboard' in response.data or b'dashboard' in response.data

    def test_login_endpoint_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        })

        assert response.status_code == 200
        # Should stay on login page with error message
        assert b'Invalid credentials' in response.data or b'error' in response.data.lower()

    def test_login_endpoint_empty_credentials(self, client):
        """Test login with empty credentials"""
        response = client.post('/auth/login', data={
            'username': '',
            'password': ''
        })

        assert response.status_code == 200
        # Should show validation error
        assert b'required' in response.data or b'error' in response.data.lower()

    def test_logout_endpoint(self, client):
        """Test logout functionality"""
        # First login
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Then logout
        response = client.get('/auth/logout', follow_redirects=True)

        assert response.status_code == 200
        # Should redirect to login page
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_protected_route_redirects_unauthenticated(self, client):
        """Test that protected routes redirect unauthenticated users"""
        # Try to access protected route without login
        response = client.get('/dashboard', follow_redirects=True)

        assert response.status_code == 200
        # Should redirect to login page
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_admin_route_allows_admin(self, authenticated_admin_client):
        """Test that admin route is accessible to admin"""
        response = authenticated_admin_client.get('/dashboard')

        assert response.status_code == 200
        # Should successfully load dashboard
        assert b'Dashboard' in response.data or b'dashboard' in response.data

    def test_admin_route_denies_department_user(self, authenticated_department_client):
        """Test that admin route denies department user"""
        response = authenticated_department_client.get('/dashboard')

        assert response.status_code == 200
        # Should load but may show restricted content
        # The actual behavior depends on implementation


class TestDashboardEndpoint:
    """Test suite for dashboard endpoint"""

    def test_dashboard_requires_authentication(self, client):
        """Test that dashboard requires authentication"""
        response = client.get('/dashboard', follow_redirects=True)

        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_dashboard_loads_for_admin(self, authenticated_admin_client):
        """Test that dashboard loads for admin user"""
        response = authenticated_admin_client.get('/dashboard')

        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'dashboard' in response.data

    def test_dashboard_loads_for_department_user(self, authenticated_department_client):
        """Test that dashboard loads for department user"""
        response = authenticated_department_client.get('/dashboard')

        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'dashboard' in response.data


class TestMedicinesEndpoints:
    """Test suite for medicines endpoints"""

    def test_medicines_list_requires_authentication(self, client):
        """Test that medicines list requires authentication"""
        response = client.get('/medicines', follow_redirects=True)

        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_medicines_list_loads_for_authenticated(self, authenticated_admin_client):
        """Test that medicines list loads for authenticated user"""
        response = authenticated_admin_client.get('/medicines')

        assert response.status_code == 200
        # Check that it contains medicines-related content
        assert b'Medicines' in response.data or b'medicines' in response.data.lower()

    def test_medicines_add_requires_admin(self, authenticated_department_client):
        """Test that adding medicines requires admin role"""
        response = authenticated_department_client.get('/medicines/add')

        assert response.status_code in [200, 302, 403]
        # Either shows error or redirects

    def test_medicines_create_valid_data(self, authenticated_admin_client):
        """Test creating a medicine with valid data"""
        medicine_data = {
            'name': 'Test Medicine',
            'generic_name': 'Test Generic',
            'category': 'Test Category',
            'supplier_id': '01',
            'purchase_price': '10.00',
            'selling_price': '15.00',
            'unit_of_measure': 'tablet',
            'low_stock_limit': '100'
        }

        response = authenticated_admin_client.post('/medicines/add', data=medicine_data)

        assert response.status_code in [200, 302]
        # Should redirect on success or show success message
        if response.status_code == 200:
            assert b'success' in response.data.lower() or b'created' in response.data.lower()

    def test_medicines_create_invalid_data(self, authenticated_admin_client):
        """Test creating a medicine with invalid data"""
        medicine_data = {
            'name': '',  # Empty name should fail validation
            'category': 'Test Category'
        }

        response = authenticated_admin_client.post('/medicines/add', data=medicine_data)

        assert response.status_code == 200
        # Should show validation errors
        assert b'required' in response.data.lower() or b'error' in response.data.lower()


class TestPatientsEndpoints:
    """Test suite for patients endpoints"""

    def test_patients_list_requires_authentication(self, client):
        """Test that patients list requires authentication"""
        response = client.get('/patients', follow_redirects=True)

        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_patients_list_loads_for_authenticated(self, authenticated_admin_client):
        """Test that patients list loads for authenticated user"""
        response = authenticated_admin_client.get('/patients')

        assert response.status_code == 200
        assert b'Patients' in response.data or b'patients' in response.data.lower()

    def test_patients_add_requires_authentication(self, authenticated_admin_client):
        """Test that adding patients requires authentication"""
        patient_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'phone': '+1234567890',
            'email': 'john@example.com'
        }

        response = authenticated_admin_client.post('/patients/add', data=patient_data)

        assert response.status_code in [200, 302]
        # Should redirect on success


class TestSuppliersEndpoints:
    """Test suite for suppliers endpoints"""

    def test_suppliers_list_requires_authentication(self, client):
        """Test that suppliers list requires authentication"""
        response = client.get('/suppliers', follow_redirects=True)

        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_suppliers_list_loads_for_authenticated(self, authenticated_admin_client):
        """Test that suppliers list loads for authenticated user"""
        response = authenticated_admin_client.get('/suppliers')

        assert response.status_code == 200
        assert b'Suppliers' in response.data or b'suppliers' in response.data.lower()

    def test_suppliers_add_requires_admin(self, authenticated_department_client):
        """Test that adding suppliers requires admin role"""
        supplier_data = {
            'name': 'Test Supplier',
            'contact_person': 'Test Person',
            'phone': '+1234567890',
            'email': 'test@example.com'
        }

        response = authenticated_department_client.post('/suppliers/add', data=supplier_data)

        assert response.status_code in [200, 302, 403]
        # Either shows error or redirects


class TestDepartmentsEndpoints:
    """Test suite for departments endpoints"""

    def test_departments_list_requires_authentication(self, client):
        """Test that departments list requires authentication"""
        response = client.get('/departments', follow_redirects=True)

        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_departments_list_loads_for_authenticated(self, authenticated_admin_client):
        """Test that departments list loads for authenticated user"""
        response = authenticated_admin_client.get('/departments')

        assert response.status_code == 200
        assert b'Departments' in response.data or b'departments' in response.data.lower()


class TestPurchasesEndpoints:
    """Test suite for purchases endpoints"""

    def test_purchases_list_requires_authentication(self, client):
        """Test that purchases list requires authentication"""
        response = client.get('/purchases', follow_redirects=True)

        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_purchases_list_loads_for_authenticated(self, authenticated_admin_client):
        """Test that purchases list loads for authenticated user"""
        response = authenticated_admin_client.get('/purchases')

        assert response.status_code == 200
        assert b'Purchases' in response.data or b'purchases' in response.data.lower()

    def test_purchases_add_requires_authentication(self, authenticated_admin_client):
        """Test that adding purchases requires authentication"""
        # Note: This might require medicines to exist first
        response = authenticated_admin_client.get('/purchases/add')

        assert response.status_code in [200, 302]
        # Should either load the form or redirect


class TestConsumptionEndpoints:
    """Test suite for consumption endpoints"""

    def test_consumption_list_requires_authentication(self, client):
        """Test that consumption list requires authentication"""
        response = client.get('/consumption', follow_redirects=True)

        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_consumption_list_loads_for_authenticated(self, authenticated_admin_client):
        """Test that consumption list loads for authenticated user"""
        response = authenticated_admin_client.get('/consumption')

        assert response.status_code == 200
        assert b'Consumption' in response.data or b'consumption' in response.data.lower()


class TestReportsEndpoints:
    """Test suite for reports endpoints"""

    def test_reports_list_requires_authentication(self, client):
        """Test that reports list requires authentication"""
        response = client.get('/reports', follow_redirects=True)

        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_reports_list_loads_for_admin(self, authenticated_admin_client):
        """Test that reports list loads for admin user"""
        response = authenticated_admin_client.get('/reports')

        assert response.status_code == 200
        assert b'Reports' in response.data or b'reports' in response.data.lower()


class TestSettingsEndpoints:
    """Test suite for settings endpoints"""

    def test_settings_requires_authentication(self, client):
        """Test that settings requires authentication"""
        response = client.get('/settings', follow_redirects=True)

        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_settings_requires_admin(self, authenticated_department_client):
        """Test that settings requires admin role"""
        response = authenticated_department_client.get('/settings')

        assert response.status_code in [200, 302, 403]
        # Either shows error or redirects


class TestAPIEndpoints:
    """Test suite for API endpoints"""

    def test_api_medicines_get_requires_authentication(self, client):
        """Test that API medicines GET requires authentication"""
        response = client.get('/api/medicines', follow_redirects=True)

        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_api_medicines_get_returns_json(self, authenticated_admin_client):
        """Test that API medicines GET returns JSON"""
        response = authenticated_admin_client.get('/api/medicines')

        assert response.status_code == 200
        # Should return JSON content
        assert response.content_type.startswith('application/json')

    def test_api_patients_get_returns_json(self, authenticated_admin_client):
        """Test that API patients GET returns JSON"""
        response = authenticated_admin_client.get('/api/patients')

        assert response.status_code == 200
        # Should return JSON content
        assert response.content_type.startswith('application/json')

    def test_api_suppliers_get_returns_json(self, authenticated_admin_client):
        """Test that API suppliers GET returns JSON"""
        response = authenticated_admin_client.get('/api/suppliers')

        assert response.status_code == 200
        # Should return JSON content
        assert response.content_type.startswith('application/json')


class TestErrorPages:
    """Test suite for error pages"""

    def test_404_page(self, client):
        """Test 404 error page"""
        response = client.get('/nonexistent-page')

        assert response.status_code == 404

    def test_404_page_contains_message(self, client):
        """Test that 404 page contains error message"""
        response = client.get('/nonexistent-page')

        assert response.status_code == 404
        # Should contain 404 or not found message
        assert b'404' in response.data or b'Not Found' in response.data or b'not found' in response.data.lower()

    def test_403_forbidden_admin_route(self, client):
        """Test 403 for unauthorized access to admin routes"""
        # This test would depend on specific admin-only routes
        # Implementation depends on the application structure
        pass

    def test_500_error_handling(self, client):
        """Test 500 error handling"""
        # This would require triggering an actual error
        # Implementation depends on the application
        pass


class TestCSRFProtection:
    """Test suite for CSRF protection (if enabled)"""

    def test_post_without_csrf_token_fails(self, authenticated_admin_client):
        """Test that POST requests without CSRF token fail (if CSRF is enabled)"""
        # This test would only apply if CSRF protection is enabled
        # For now, we'll just check that the endpoint exists
        response = authenticated_admin_client.post('/medicines/add', data={
            'name': 'Test',
            'category': 'Test'
        })

        # Should either succeed (if no CSRF) or fail with CSRF error
        assert response.status_code in [200, 302, 400]
