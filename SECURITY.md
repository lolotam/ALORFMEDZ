# Security Documentation

## Overview

This document describes the security features implemented in the ALORF Hospital Pharmacy Management System. The application implements multiple layers of security to protect against common web vulnerabilities and attacks.

## Security Features

### 1. CSRF Protection

**Implementation**: Custom CSRF protection with Flask integration

**Location**: `app/utils/csrf.py`

**Features**:
- Automatic CSRF token generation for each session
- Token validation for all POST, PUT, DELETE requests
- Support for both form-based and AJAX requests
- Configurable token timeout
- Constant-time comparison to prevent timing attacks

**Usage**:
```python
from app.utils.csrf import csrf_protect, get_csrf_token

@auth_bp.route('/login', methods=['POST'])
@csrf_protect
def login():
    # CSRF protection automatically applied
    pass
```

**Template Usage**:
```html
<!-- For regular forms -->
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ get_csrf_token() }}">
    ...
</form>

<!-- For AJAX requests -->
<script>
fetch('/csrf-token')
    .then(response => response.json())
    .then(data => {
        fetch('/endpoint', {
            method: 'POST',
            headers: {
                'X-CSRF-Token': data.csrf_token
            },
            body: JSON.stringify(data)
        });
    });
</script>
```

### 2. Rate Limiting

**Implementation**: In-memory rate limiter (Redis recommended for production)

**Location**: `app/utils/rate_limiter.py`

**Features**:
- Configurable rate limits per endpoint
- Different limits for different endpoints:
  - Login: 5 attempts per 15 minutes
  - API: 100 requests per hour
  - Upload: 10 uploads per minute
  - General: 200 requests per hour
- Uses IP address or session ID for tracking
- Rate limit headers in responses

**Usage**:
```python
from app.utils.rate_limiter import rate_limit, login_rate_limit

# Using predefined rate limiter
@auth_bp.route('/login', methods=['POST'])
@login_rate_limit
def login():
    pass

# Custom rate limit
@api_bp.route('/data')
@rate_limit(50, 3600)  # 50 requests per hour
def get_data():
    pass
```

### 3. Account Lockout

**Implementation**: Automatic account lockout after failed login attempts

**Features**:
- 5 failed login attempts = 15-minute lockout
- Tracks failed attempts in session
- Automatically unlocks after timeout
- Logs lockout events for security monitoring

**Configuration** (in `.env`):
```bash
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=30  # minutes
```

### 4. Security Logging

**Implementation**: Structured logging with specialized loggers

**Location**: `app/utils/logging_config.py`

**Features**:
- Separate log files for different event types:
  - `app.log` - General application logs
  - `errors.log` - Error logs
  - `security.log` - Security events
  - `performance.log` - Performance metrics
- Logged events:
  - Login attempts (success/failure)
  - Failed login tracking
  - Account lockouts
  - CSRF violations
  - Rate limit violations
  - Unauthorized access attempts
  - Password changes

**Usage**:
```python
from app.utils.logging_config import security_logger

security_logger.log_login_attempt(
    username='john',
    success=True,
    ip_address='192.168.1.1',
    user_agent='Mozilla/5.0...'
)
```

### 5. Security Headers

**Implementation**: Automatic security headers in production

**Headers Set**:
- `Strict-Transport-Security`: Force HTTPS
- `X-Content-Type-Options`: Prevent MIME sniffing
- `X-Frame-Options`: Prevent clickjacking
- `X-XSS-Protection`: Enable XSS protection
- `Content-Security-Policy`: Limit resource loading
- `Referrer-Policy`: Control referrer information

**Configuration**:
```python
# In production config
SECURITY_HEADERS_ENABLED=True
```

### 6. Session Security

**Implementation**: Secure session configuration

**Features**:
- HTTPOnly cookies (prevents JavaScript access)
- Secure cookies in production (HTTPS only)
- SameSite cookie attribute (prevents CSRF)
- Session signing to prevent tampering
- Session key prefix to avoid conflicts

**Configuration**:
```bash
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
SESSION_USE_SIGNER=True
SESSION_KEY_PREFIX=pharmacy:
```

### 7. Password Policy

**Implementation**: Configurable password requirements

**Features**:
- Minimum length (default: 8 characters)
- Uppercase letter requirement
- Lowercase letter requirement
- Digit requirement
- Special character requirement

**Configuration**:
```bash
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_DIGITS=True
PASSWORD_REQUIRE_SPECIAL=True
```

### 8. File Upload Security

**Implementation**: Secure file upload handling

**Features**:
- File size limits (16MB default)
- Content type validation
- File extension validation
- Secure file naming
-隔离存储目录

### 9. Input Validation

**Implementation**: Input sanitization and validation

**Features**:
- HTML escaping in templates
- SQL injection prevention (using JSON database)
- XSS prevention through template filters
- Length validation for all inputs
- Type validation for form fields

### 10. Error Handling

**Implementation**: Secure error handling

**Features**:
- Generic error messages (no sensitive info leaked)
- Different handling for API vs web requests
- Logging of all errors
- Custom error pages for 404, 403, 500

## Security Configuration

### Environment Variables

All security settings are configured through environment variables in `.env`:

```bash
# Security - MUST CHANGE
SECRET_KEY=your-secret-key-here

# Rate Limiting
LOGIN_RATE_LIMIT=5/15m
API_RATE_LIMIT=100/hour
UPLOAD_RATE_LIMIT=10/m

# Session Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_USE_SIGNER=True

# Password Policy
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_DIGITS=True

# Account Lockout
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=30
```

### Production Deployment Checklist

- [ ] Change default SECRET_KEY
- [ ] Set SESSION_COOKIE_SECURE=True
- [ ] Enable SESSION_USE_SIGNER
- [ ] Set DEBUG=False
- [ ] Configure firewall rules
- [ ] Enable HTTPS/SSL
- [ ] Set up log monitoring
- [ ] Configure backup encryption
- [ ] Set up intrusion detection
- [ ] Enable audit logging
- [ ] Review and test all security features
- [ ] Set up monitoring alerts
- [ ] Configure rate limiting for all endpoints
- [ ] Enable CSRF protection on all forms
- [ ] Set up secure file upload handling
- [ ] Configure content security policy
- [ ] Set up security headers
- [ ] Review password policy
- [ ] Enable account lockout
- [ ] Configure logging levels
- [ ] Set up log rotation

## Monitoring Security Events

### Log Files

Monitor these log files for security events:

1. **security.log**: All security-related events
2. **errors.log**: Application errors (may include security errors)
3. **app.log**: General application logs

### Key Events to Monitor

- Failed login attempts (especially multiple failures)
- Account lockouts
- CSRF violations
- Rate limit violations
- Unauthorized access attempts
- Password changes
- Unusual access patterns

### Automated Alerts

Consider setting up alerts for:
- Multiple failed login attempts (brute force)
- Account lockouts
- Rate limit violations
- Unusual traffic patterns
- Security header violations

## Vulnerability Management

### Regular Security Updates

1. Keep dependencies updated
2. Review security advisories
3. Perform regular security audits
4. Test security features
5. Review and rotate secrets
6. Update password policies
7. Review access logs
8. Test incident response procedures

### Security Testing

Run security tests regularly:

```bash
# Run all tests including security tests
pytest

# Run only security tests
pytest tests/test_security.py

# Run performance tests
pytest tests/test_performance.py
```

## Incident Response

### Detecting Security Incidents

1. Monitor log files for anomalies
2. Set up alerts for suspicious activity
3. Review access patterns regularly
4. Monitor for unusual login patterns
5. Track file upload patterns

### Response Procedures

1. **Immediate Response**:
   - Identify the incident
   - Contain the threat
   - Assess the impact

2. **Investigation**:
   - Review logs
   - Identify root cause
   - Document findings

3. **Recovery**:
   - Restore affected systems
   - Update security measures
   - Verify system integrity

4. **Post-Incident**:
   - Document lessons learned
   - Update security policies
   - Improve monitoring
   - Conduct security training

## Best Practices

### For Developers

1. Always validate user input
2. Use parameterized queries (if using SQL)
3. Implement CSRF protection on all forms
4. Validate file uploads
5. Use secure session configuration
6. Log security events
7. Follow principle of least privilege
8. Keep dependencies updated
9. Use environment variables for secrets
10. Never commit secrets to version control

### For Administrators

1. Monitor security logs regularly
2. Review user access patterns
3. Conduct security audits
4. Update security policies
5. Train users on security best practices
6. Maintain backup and recovery procedures
7. Keep systems updated
8. Configure monitoring and alerting
9. Review and rotate credentials
10. Document security procedures

## Security Contact

For security-related questions or to report vulnerabilities, please contact the system administrator.

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Guide](https://flask.palletsprojects.com/security/)
- [Python Security Best Practices](https://python-security.readthedocs.io/)

## Changelog

### Version 1.0.0 (Phase 7)
- Implemented CSRF protection
- Added rate limiting
- Implemented account lockout
- Added security logging
- Configured security headers
- Enhanced session security
- Added password policy enforcement
- Implemented health check endpoint
- Added performance monitoring
- Created comprehensive security tests
