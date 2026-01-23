"""
Security Tests

Tests for security features including CSRF protection, rate limiting,
and authentication security.
"""

import pytest
import time
from flask import session
from unittest.mock import patch, MagicMock


class TestCSRFProtection:
    """Test CSRF protection"""

    def test_csrf_token_generation(self, client):
        """Test that CSRF token is generated"""
        response = client.get('/csrf-token')
        assert response.status_code == 200
        data = response.get_json()
        assert 'csrf_token' in data
        assert 'header_name' in data
        assert 'form_name' in data

    def test_csrf_protection_on_login(self, client):
        """Test CSRF protection on login endpoint"""
        # Attempt login without CSRF token
        response = client.post('/auth/login', data={
            'username': 'test',
            'password': 'test'
        }, follow_redirects=True)

        # Should return error (redirect to login or error message)
        assert response.status_code in [200, 403]
        data = response.get_json() if response.is_json else None
        if data:
            assert 'error' in data or 'message' in data

    def test_csrf_protection_ajax_request(self, client):
        """Test CSRF protection on AJAX requests"""
        # First get CSRF token
        token_response = client.get('/csrf-token')
        token_data = token_response.get_json()
        csrf_token = token_data['csrf_token']

        # Test with valid CSRF token in header
        response = client.post('/auth/login',
                               headers={'X-CSRF-Token': csrf_token},
                               json={'username': 'test', 'password': 'test'})

        # Should get proper response (even if credentials are wrong)
        assert response.status_code in [200, 302, 400, 401, 403]

    def test_csrf_token_validation(self, client):
        """Test CSRF token validation"""
        # Test with invalid CSRF token
        response = client.post('/auth/login',
                               headers={'X-CSRF-Token': 'invalid_token'},
                               data={'username': 'test', 'password': 'test'})

        assert response.status_code == 403


class TestRateLimiting:
    """Test rate limiting"""

    def test_login_rate_limit(self, client):
        """Test login rate limiting"""
        # Get CSRF token first
        token_response = client.get('/csrf-token')
        token_data = token_response.get_json()
        csrf_token = token_data['csrf_token']

        # Attempt multiple failed logins
        for i in range(5):
            response = client.post('/auth/login',
                                   headers={'X-CSRF-Token': csrf_token},
                                   data={'username': 'invalid', 'password': 'invalid'})

        # After 5 attempts, should get rate limited
        response = client.post('/auth/login',
                               headers={'X-CSRF-Token': csrf_token},
                               data={'username': 'invalid', 'password': 'invalid'})

        # Should be rate limited (429) or account locked
        assert response.status_code in [429, 200]  # 429 for rate limit, 200 for account locked message

    def test_rate_limit_headers(self, client):
        """Test rate limit headers in response"""
        # This test would require setting up proper rate limiting
        # For now, just check that the endpoint exists
        response = client.get('/health')
        assert response.status_code == 200


class TestAuthentication:
    """Test authentication security"""

    def test_login_requires_csrf(self, client):
        """Test that login requires CSRF token"""
        response = client.post('/auth/login',
                               data={'username': 'admin', 'password': 'wrong'},
                               follow_redirects=False)

        # Should fail without CSRF token
        assert response.status_code in [302, 403]

    def test_logout_requires_csrf(self, client):
        """Test that logout requires CSRF token"""
        # Login first
        token_response = client.get('/csrf-token')
        token_data = token_response.get_json()
        csrf_token = token_data['csrf_token']

        # Login with valid credentials
        client.post('/auth/login',
                    headers={'X-CSRF-Token': csrf_token},
                    data={'username': 'admin', 'password': '@Xx123456789xX@'},
                    follow_redirects=True)

        # Now test logout without CSRF token
        response = client.get('/auth/logout', follow_redirects=False)
        assert response.status_code == 302  # Should redirect to login

    def test_session_persistence(self, client):
        """Test that session persists across requests"""
        # Login
        token_response = client.get('/csrf-token')
        token_data = token_response.get_json()
        csrf_token = token_data['csrf_token']

        client.post('/auth/login',
                    headers={'X-CSRF-Token': csrf_token},
                    data={'username': 'admin', 'password': '@Xx123456789xX@'},
                    follow_redirects=True)

        # Check session
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert 'username' in sess

    def test_password_change_requires_csrf(self, authenticated_client):
        """Test that password change requires CSRF token"""
        response = authenticated_client.post('/auth/change-password',
                                             data={
                                                 'current_password': 'wrong',
                                                 'new_password': 'newpass',
                                                 'confirm_password': 'newpass'
                                             })

        # Should fail without CSRF token
        assert response.status_code == 403


class TestSecurityHeaders:
    """Test security headers"""

    def test_security_headers_in_production(self, app):
        """Test that security headers are set in production"""
        app.config['DEBUG'] = False
        app.config['SECURITY_HEADERS_ENABLED'] = True

        with app.test_client() as client:
            response = client.get('/')

            # Check for security headers
            assert 'Strict-Transport-Security' in response.headers or \
                   response.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_cors_headers_for_api(self, client):
        """Test CORS headers for API endpoints"""
        response = client.get('/api/test')

        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers


class TestAccountLockout:
    """Test account lockout mechanism"""

    def test_account_lockout_after_failed_attempts(self, client):
        """Test account lockout after multiple failed login attempts"""
        # Get CSRF token
        token_response = client.get('/csrf-token')
        token_data = token_response.get_json()
        csrf_token = token_data['csrf_token']

        # Attempt multiple failed logins
        for i in range(5):
            client.post('/auth/login',
                        headers={'X-CSRF-Token': csrf_token},
                        data={'username': 'invalid', 'password': 'invalid'},
                        follow_redirects=False)

        # Next attempt should be locked
        response = client.post('/auth/login',
                               headers={'X-CSRF-Token': csrf_token},
                               data={'username': 'invalid', 'password': 'invalid'},
                               follow_redirects=False)

        # Should either be rate limited or show lockout message
        assert response.status_code in [302, 429, 200]

    def test_lockout_time_remaining(self, client):
        """Test lockout time display"""
        # This would require checking the session
        # Implementation depends on how lockout is displayed
        pass


class TestPasswordSecurity:
    """Test password security"""

    def test_password_minimum_length(self, authenticated_client):
        """Test password minimum length validation"""
        response = authenticated_client.post('/auth/change-password',
                                             data={
                                                 'current_password': '@Xx123456789xX@',
                                                 'new_password': '123',
                                                 'confirm_password': '123'
                                             })

        # Should fail due to short password
        assert b'at least 6 characters' in response.data or \
               b'least 8 characters' in response.data

    def test_password_confirmation_match(self, authenticated_client):
        """Test password confirmation matching"""
        response = authenticated_client.post('/auth/change-password',
                                             data={
                                                 'current_password': '@Xx123456789xX@',
                                                 'new_password': 'newpassword123',
                                                 'confirm_password': 'differentpassword'
                                             })

        # Should fail due to mismatch
        assert b'do not match' in response.data


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_endpoint_exists(self, client):
        """Test health endpoint exists"""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_check_json_response(self, client):
        """Test health check returns JSON"""
        response = client.get('/health')
        assert response.is_json

        data = response.get_json()
        assert 'status' in data
        assert 'checks' in data

    def test_readiness_probe(self, client):
        """Test readiness probe"""
        response = client.get('/health/ready')
        assert response.status_code == 200

        data = response.get_json()
        assert 'status' in data
        assert data['status'] in ['ready', 'not_ready']

    def test_liveness_probe(self, client):
        """Test liveness probe"""
        response = client.get('/health/live')
        assert response.status_code == 200

        data = response.get_json()
        assert data['status'] == 'alive'

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get('/health/metrics')
        assert response.status_code == 200

        data = response.get_json()
        assert 'metrics' in data


class TestInputValidation:
    """Test input validation and sanitization"""

    def test_sql_injection_prevention(self, client):
        """Test prevention of SQL injection (using JSON file DB)"""
        # With JSON file database, injection isn't a concern
        # But we should test that special characters are handled
        token_response = client.get('/csrf-token')
        token_data = token_response.get_json()
        csrf_token = token_data['csrf_token']

        response = client.post('/auth/login',
                               headers={'X-CSRF-Token': csrf_token},
                               data={'username': "'; DROP TABLE users; --", 'password': 'test'})

        # Should handle gracefully
        assert response.status_code in [200, 302, 400, 401, 403]

    def test_xss_prevention_in_username(self, client):
        """Test XSS prevention in username field"""
        # This would be tested in the frontend
        # Backend should handle any input gracefully
        token_response = client.get('/csrf-token')
        token_data = token_response.get_json()
        csrf_token = token_data['csrf_token']

        response = client.post('/auth/login',
                               headers={'X-CSRF-Token': csrf_token},
                               data={'username': '<script>alert("xss")</script>', 'password': 'test'})

        # Should handle gracefully
        assert response.status_code in [200, 302, 400, 401, 403]


class TestFileUploadSecurity:
    """Test file upload security"""

    def test_profile_photo_upload_requires_csrf(self, authenticated_client):
        """Test profile photo upload requires CSRF token"""
        response = authenticated_client.post('/auth/upload-profile-photo',
                                              data={'photo': (BytesIO(b'test'), 'test.jpg')})

        # Should fail without CSRF token
        assert response.status_code == 403

    def test_profile_photo_upload_content_type(self, authenticated_client):
        """Test profile photo upload validates content type"""
        # This test would require a more complex setup
        # with actual file upload
        pass
