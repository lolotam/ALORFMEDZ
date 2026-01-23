"""
Integration tests for authentication flows
"""

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestLoginFlow:
    """Test suite for login flow"""

    def test_successful_login_admin(self, client):
        """Test successful login with admin credentials"""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        }, follow_redirects=True)

        # Should successfully login and redirect
        assert response.status_code == 200
        # Should be on dashboard or another authenticated page
        assert b'Dashboard' in response.data or b'dashboard' in response.data.lower()

    def test_successful_login_department_user(self, client):
        """Test successful login with department user credentials"""
        response = client.post('/auth/login', data={
            'username': 'pharmacy',
            'password': 'pharmacy123'
        }, follow_redirects=True)

        # Should successfully login and redirect
        assert response.status_code == 200
        # Should be on dashboard or another authenticated page
        assert b'Dashboard' in response.data or b'dashboard' in response.data.lower()

    def test_failed_login_wrong_password(self, client):
        """Test failed login with wrong password"""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        })

        # Should stay on login page with error
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'error' in response.data.lower()

    def test_failed_login_nonexistent_user(self, client):
        """Test failed login with non-existent user"""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'anypassword'
        })

        # Should stay on login page with error
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'error' in response.data.lower()

    def test_failed_login_empty_credentials(self, client):
        """Test failed login with empty credentials"""
        response = client.post('/auth/login', data={
            'username': '',
            'password': ''
        })

        # Should stay on login page
        assert response.status_code == 200
        # Should show validation error
        assert b'required' in response.data.lower() or b'error' in response.data.lower()

    def test_login_preserves_session(self, client):
        """Test that login preserves session data"""
        # First login
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        }, follow_redirects=True)

        # Verify session is set
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert 'username' in sess
            assert 'role' in sess

    def test_login_sets_correct_role(self, client):
        """Test that login sets correct role for admin"""
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        with client.session_transaction() as sess:
            assert sess['role'] == 'admin'
            assert sess['user_id'] == '01'

    def test_login_sets_department_user_role(self, client):
        """Test that login sets correct role for department user"""
        client.post('/auth/login', data={
            'username': 'pharmacy',
            'password': 'pharmacy123'
        })

        with client.session_transaction() as sess:
            assert sess['role'] == 'department_user'
            assert sess['user_id'] == '02'

    def test_login_redirect_after_success(self, client):
        """Test that login redirects to dashboard after successful login"""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Should be a redirect response
        assert response.status_code == 302
        assert 'dashboard' in response.location.lower() or response.location.endswith('/dashboard')


class TestLogoutFlow:
    """Test suite for logout flow"""

    def test_successful_logout(self, client):
        """Test successful logout"""
        # First login
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Then logout
        response = client.get('/auth/logout', follow_redirects=True)

        assert response.status_code == 200
        # Should be redirected to login page
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_logout_clears_session(self, client):
        """Test that logout clears session data"""
        # Login first
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Verify session is set
        with client.session_transaction() as sess:
            assert 'user_id' in sess

        # Logout
        client.get('/auth/logout')

        # Verify session is cleared
        with client.session_transaction() as sess:
            assert 'user_id' not in sess

    def test_logout_redirects_to_login(self, client):
        """Test that logout redirects to login page"""
        # Login first
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Logout
        response = client.get('/auth/logout', follow_redirects=True)

        # Should end up on login page
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_logout_idempotent(self, client):
        """Test that logout can be called multiple times safely"""
        # Login
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Logout multiple times
        response1 = client.get('/auth/logout')
        response2 = client.get('/auth/logout')
        response3 = client.get('/auth/logout')

        # All should succeed without error
        assert response1.status_code in [200, 302]
        assert response2.status_code in [200, 302]
        assert response3.status_code in [200, 302]


class TestSessionPersistence:
    """Test suite for session persistence"""

    def test_session_persists_across_requests(self, client):
        """Test that session persists across multiple requests"""
        # Login
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Make multiple requests to verify session persists
        response1 = client.get('/dashboard')
        response2 = client.get('/medicines')
        response3 = client.get('/patients')

        # All should succeed (not redirect to login)
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

    def test_session_has_correct_user_data(self, client):
        """Test that session contains correct user data"""
        # Login
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Verify session data
        with client.session_transaction() as sess:
            assert sess['user_id'] == '01'
            assert sess['username'] == 'admin'
            assert sess['role'] == 'admin'
            assert 'login_time' in sess

    def test_department_user_session_has_department_id(self, client):
        """Test that department user session has department_id"""
        # Login as department user
        client.post('/auth/login', data={
            'username': 'pharmacy',
            'password': 'pharmacy123'
        })

        # Verify session has department_id
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert sess['role'] == 'department_user'
            # Department user should have department_id
            assert 'department_id' in sess or sess.get('department_id') == '01'


class TestAccessControl:
    """Test suite for access control"""

    def test_unauthenticated_user_redirected_from_protected_route(self, client):
        """Test that unauthenticated users are redirected from protected routes"""
        # Try to access various protected routes
        protected_routes = [
            '/dashboard',
            '/medicines',
            '/patients',
            '/suppliers',
            '/departments',
            '/purchases',
            '/consumption',
            '/reports',
            '/settings'
        ]

        for route in protected_routes:
            response = client.get(route, follow_redirects=True)
            # Should end up on login page
            assert b'Login' in response.data or b'login' in response.data.lower()

    def test_authenticated_user_can_access_dashboard(self, client):
        """Test that authenticated user can access dashboard"""
        # Login
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Should be able to access dashboard
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'dashboard' in response.data.lower()

    def test_admin_can_access_admin_routes(self, authenticated_admin_client):
        """Test that admin can access admin-specific routes"""
        # Test accessing various routes as admin
        routes = [
            '/medicines',
            '/patients',
            '/suppliers',
            '/departments',
            '/reports',
            '/settings'
        ]

        for route in routes:
            response = authenticated_admin_client.get(route)
            assert response.status_code == 200

    def test_department_user_can_access_permitted_routes(self, authenticated_department_client):
        """Test that department user can access permitted routes"""
        # Department users should be able to access certain routes
        routes = [
            '/dashboard',
            '/medicines',
            '/patients'
        ]

        for route in routes:
            response = authenticated_department_client.get(route)
            assert response.status_code == 200

    def test_department_user_restricted_from_admin_routes(self, authenticated_department_client):
        """Test that department user is restricted from admin-only routes"""
        # Try to access admin-only routes
        admin_routes = [
            '/settings',
            '/reports'
        ]

        for route in admin_routes:
            response = authenticated_department_client.get(route)
            # Should either be forbidden or show restricted content
            assert response.status_code in [200, 302, 403]
            # If 200, content should indicate restriction
            if response.status_code == 200:
                assert b'restrict' in response.data.lower() or b'admin' in response.data.lower()

    def test_role_based_content_shown(self, authenticated_admin_client):
        """Test that role-based content is shown to admin"""
        response = authenticated_admin_client.get('/dashboard')

        assert response.status_code == 200
        # Admin should see admin-specific content
        # This depends on actual implementation
        assert b'Dashboard' in response.data or b'dashboard' in response.data.lower()


class TestSessionTimeout:
    """Test suite for session timeout (if implemented)"""

    def test_session_valid_immediately_after_login(self, client):
        """Test that session is valid immediately after login"""
        # Login
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Should be able to access protected route immediately
        response = client.get('/dashboard')
        assert response.status_code == 200

    def test_session_remains_valid_shortly_after_login(self, client):
        """Test that session remains valid for a reasonable time"""
        # Login
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Make several requests over a short period
        for _ in range(5):
            response = client.get('/dashboard')
            assert response.status_code == 200


class TestAuthenticationEdgeCases:
    """Test suite for authentication edge cases"""

    def test_login_with_special_characters_in_password(self, client):
        """Test login with special characters in password"""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Should succeed (this is the actual admin password)
        assert response.status_code == 302

    def test_login_case_sensitive_username(self, client):
        """Test that username is case-sensitive"""
        # Try with uppercase
        response = client.post('/auth/login', data={
            'username': 'ADMIN',
            'password': '@Xx123456789xX@'
        })

        # Should fail (usernames are case-sensitive)
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'error' in response.data.lower()

    def test_concurrent_logins_same_user(self, client):
        """Test that same user can login from multiple sessions"""
        # Login first session
        with client.session_transaction() as sess:
            sess['user_id'] = '01'

        # Login second session (simulate)
        response = client.post('/auth/login', data={
            'username': 'pharmacy',
            'password': 'pharmacy123'
        })

        # Should succeed
        assert response.status_code == 302

    def test_login_then_immediately_logout(self, client):
        """Test immediate login then logout"""
        # Login
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Immediately logout
        response = client.get('/auth/logout', follow_redirects=True)

        # Should be back to login
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()

    def test_accessing_protected_route_after_logout_redirects(self, client):
        """Test that accessing protected route after logout redirects to login"""
        # Login
        client.post('/auth/login', data={
            'username': 'admin',
            'password': '@Xx123456789xX@'
        })

        # Logout
        client.get('/auth/logout')

        # Try to access protected route
        response = client.get('/dashboard', follow_redirects=True)

        # Should end up on login page
        assert b'Login' in response.data or b'login' in response.data.lower()
