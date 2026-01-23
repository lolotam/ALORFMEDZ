"""
Unit tests for authentication and authorization decorators
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestLoginRequired:
    """Test suite for login_required decorator"""

    def test_login_required_preserves_function_signature(self):
        """Test that login_required preserves the original function signature"""
        from app.utils.decorators import login_required

        def test_function(x, y, z=10):
            return x + y + z

        decorated = login_required(test_function)
        assert decorated.__name__ == 'test_function'
        assert decorated.__doc__ == test_function.__doc__


class TestAdminRequired:
    """Test suite for admin_required decorator"""

    def test_admin_required_preserves_function_signature(self):
        """Test that admin_required preserves the original function signature"""
        from app.utils.decorators import admin_required

        def test_function(x, y):
            return x + y

        decorated = admin_required(test_function)
        assert decorated.__name__ == 'test_function'
        assert decorated.__doc__ == test_function.__doc__


class TestDepartmentUserRequired:
    """Test suite for department_user_required decorator"""

    def test_department_user_required_preserves_function_signature(self):
        """Test that department_user_required preserves the original function signature"""
        from app.utils.decorators import department_user_required

        def test_function(x):
            return x * 2

        decorated = department_user_required(test_function)
        assert decorated.__name__ == 'test_function'
        assert decorated.__doc__ == test_function.__doc__


class TestAdminOrDepartmentUserRequired:
    """Test suite for admin_or_department_user_required decorator"""

    def test_admin_or_department_user_required_preserves_function_signature(self):
        """Test that admin_or_department_user_required preserves the original function signature"""
        from app.utils.decorators import admin_or_department_user_required

        def test_function():
            return "test"

        decorated = admin_or_department_user_required(test_function)
        assert decorated.__name__ == 'test_function'
        assert decorated.__doc__ == test_function.__doc__


class TestRestrictDepartmentUserAction:
    """Test suite for restrict_department_user_action decorator"""

    def test_restrict_department_user_action_preserves_function_signature(self):
        """Test that restrict_department_user_action preserves the original function signature"""
        from app.utils.decorators import restrict_department_user_action

        def test_function():
            return "test"

        decorated = restrict_department_user_action('delete')(test_function)
        assert decorated.__name__ == 'test_function'
        assert decorated.__doc__ == test_function.__doc__


class TestLogExecutionTime:
    """Test suite for log_execution_time decorator"""

    def test_log_execution_time_logs_execution_time(self, caplog):
        """Test that decorator logs execution time"""
        from app.utils.decorators import log_execution_time
        import time

        @log_execution_time
        def slow_function():
            time.sleep(0.01)
            return "Done"

        with caplog.at_level('DEBUG'):
            result = slow_function()

            assert result == "Done"
            assert "slow_function executed in" in caplog.text
            assert "s" in caplog.text

    def test_log_execution_time_handles_exceptions(self, caplog):
        """Test that decorator logs execution time even when function raises exception"""
        from app.utils.decorators import log_execution_time
        import time

        @log_execution_time
        def failing_function():
            time.sleep(0.01)
            raise ValueError("Test error")

        with caplog.at_level('ERROR'):
            with pytest.raises(ValueError, match="Test error"):
                failing_function()

            assert "failing_function failed after" in caplog.text


class TestLogRequest:
    """Test suite for log_request decorator"""

    def test_log_request_preserves_function_signature(self):
        """Test that log_request preserves the original function signature"""
        from app.utils.decorators import log_request

        def test_function():
            return "test"

        decorated = log_request(test_function)
        assert decorated.__name__ == 'test_function'
        assert decorated.__doc__ == test_function.__doc__
