"""
Form Validation Utilities

Common validation patterns for form data validation in Flask blueprints.
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_required_fields(data: Dict[str, Any], fields: List[str]) -> Optional[str]:
    """Validate that required fields are present and non-empty

    Args:
        data: Dictionary containing form data
        fields: List of required field names

    Returns:
        None if validation passes, error message string if validation fails
    """
    missing_fields = []
    for field in fields:
        value = data.get(field, '').strip() if isinstance(data.get(field), str) else data.get(field)
        if value is None or value == '':
            missing_fields.append(field)

    if missing_fields:
        return f"Required fields missing: {', '.join(missing_fields)}"
    return None


def validate_email(email: str) -> Optional[str]:
    """Validate email format

    Args:
        email: Email address string

    Returns:
        None if validation passes, error message string if validation fails
    """
    if not email:
        return None  # Email is optional in many contexts

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return "Invalid email format"
    return None


def validate_username(username: str) -> Optional[str]:
    """Validate username format

    Args:
        username: Username string

    Returns:
        None if validation passes, error message string if validation fails
    """
    if not username:
        return "Username is required"

    # Username should be 3-30 characters, alphanumeric with underscores
    username_pattern = r'^[a-zA-Z0-9_]{3,30}$'
    if not re.match(username_pattern, username):
        return "Username must be 3-30 characters (letters, numbers, underscores only)"
    return None


def validate_date_format(date_string: str, format_string: str = '%Y-%m-%d') -> Optional[str]:
    """Validate date string format

    Args:
        date_string: Date string to validate
        format_string: Expected date format (default: YYYY-MM-DD)

    Returns:
        None if validation passes, error message string if validation fails
    """
    if not date_string:
        return None  # Date is optional in many contexts

    try:
        datetime.strptime(date_string, format_string)
    except ValueError:
        return f"Invalid date format. Expected format: {format_string}"
    return None


def validate_numeric(value: Any, field_name: str = "Value",
                    min_value: Optional[float] = None,
                    max_value: Optional[float] = None) -> Optional[str]:
    """Validate that a value is numeric and within optional bounds

    Args:
        value: Value to validate
        field_name: Name of the field for error message
        min_value: Optional minimum value
        max_value: Optional maximum value

    Returns:
        None if validation passes, error message string if validation fails
    """
    try:
        numeric_value = float(value)
    except (ValueError, TypeError):
        return f"{field_name} must be a number"

    if min_value is not None and numeric_value < min_value:
        return f"{field_name} must be at least {min_value}"

    if max_value is not None and numeric_value > max_value:
        return f"{field_name} must be at most {max_value}"

    return None


def validate_phone(phone: str) -> Optional[str]:
    """Validate phone number format (international)

    Args:
        phone: Phone number string

    Returns:
        None if validation passes, error message string if validation fails
    """
    if not phone:
        return None  # Phone is optional in many contexts

    # Remove common separators
    clean_phone = re.sub(r'[\s\-\(\)\+]', '', phone)

    # Check if it's 7-15 digits
    if not re.match(r'^\d{7,15}$', clean_phone):
        return "Invalid phone number format"

    return None


def validate_positive_number(value: Any, field_name: str = "Value") -> Optional[str]:
    """Validate that a value is a positive number

    Args:
        value: Value to validate
        field_name: Name of the field for error message

    Returns:
        None if validation passes, error message string if validation fails
    """
    return validate_numeric(value, field_name, min_value=0.01)


def validate_positive_integer(value: Any, field_name: str = "Value") -> Optional[str]:
    """Validate that a value is a positive integer

    Args:
        value: Value to validate
        field_name: Name of the field for error message

    Returns:
        None if validation passes, error message string if validation fails
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        return f"{field_name} must be an integer"

    if int_value <= 0:
        return f"{field_name} must be a positive integer"

    return None


def validate_length(text: str, min_length: int = 0, max_length: int = 1000,
                   field_name: str = "Field") -> Optional[str]:
    """Validate text length

    Args:
        text: Text to validate
        min_length: Minimum length (default: 0)
        max_length: Maximum length (default: 1000)
        field_name: Name of the field for error message

    Returns:
        None if validation passes, error message string if validation fails
    """
    if not text:
        if min_length > 0:
            return f"{field_name} is required"
        return None

    text_length = len(text)
    if text_length < min_length:
        return f"{field_name} must be at least {min_length} characters"

    if text_length > max_length:
        return f"{field_name} must be at most {max_length} characters"

    return None


def validate_in_list(value: str, valid_values: List[str],
                    field_name: str = "Value", case_sensitive: bool = True) -> Optional[str]:
    """Validate that a value is in a list of valid values

    Args:
        value: Value to validate
        valid_values: List of valid values
        field_name: Name of the field for error message
        case_sensitive: Whether comparison should be case sensitive

    Returns:
        None if validation passes, error message string if validation fails
    """
    if not case_sensitive:
        value = value.lower()
        valid_values = [v.lower() for v in valid_values]

    if value not in valid_values:
        return f"{field_name} must be one of: {', '.join(map(str, valid_values))}"

    return None
