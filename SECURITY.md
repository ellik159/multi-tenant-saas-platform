# Security Policy

## Supported Versions

Currently supporting version 1.0.0 with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Updates

### 2026-01-27: Dependency Security Patches

#### Fixed Vulnerabilities

1. **FastAPI Content-Type Header ReDoS**
   - **Package**: fastapi
   - **Previous Version**: 0.104.1
   - **Patched Version**: 0.109.1
   - **Severity**: Medium
   - **CVE**: Duplicate Advisory
   - **Description**: FastAPI was vulnerable to Regular Expression Denial of Service (ReDoS) via Content-Type header parsing
   - **Impact**: Could allow attackers to cause denial of service through crafted Content-Type headers
   - **Fix**: Upgraded to FastAPI 0.109.1

2. **Python-Multipart Arbitrary File Write**
   - **Package**: python-multipart
   - **Previous Version**: 0.0.6
   - **Patched Version**: 0.0.22
   - **Severity**: High
   - **Description**: Arbitrary file write vulnerability via non-default configuration
   - **Impact**: Could allow attackers to write arbitrary files to the server
   - **Fix**: Upgraded to python-multipart 0.0.22

3. **Python-Multipart DoS via Malformed Boundary**
   - **Package**: python-multipart
   - **Previous Version**: 0.0.6
   - **Patched Version**: 0.0.22 (fixed in 0.0.18)
   - **Severity**: Medium
   - **Description**: Denial of service via deformation multipart/form-data boundary
   - **Impact**: Could allow attackers to cause denial of service
   - **Fix**: Upgraded to python-multipart 0.0.22

4. **Python-Multipart Content-Type Header ReDoS**
   - **Package**: python-multipart
   - **Previous Version**: 0.0.6
   - **Patched Version**: 0.0.22 (fixed in 0.0.7)
   - **Severity**: Medium
   - **Description**: Vulnerable to Content-Type Header Regular Expression Denial of Service
   - **Impact**: Could allow attackers to cause denial of service through crafted Content-Type headers
   - **Fix**: Upgraded to python-multipart 0.0.22

## Previous Security Fixes

### Code-Level Security Fixes

1. **SQL Injection in Tenant Context Setting**
   - **Date**: 2026-01-27
   - **Severity**: Critical
   - **Description**: SQL injection vulnerability in `src/database/session.py` where organization_id was directly interpolated into SQL string
   - **Fix**: Implemented parameterized queries using SQLAlchemy's `text()` with parameter binding
   - **File**: `src/database/session.py`

2. **Potential AttributeError in Rate Limiter**
   - **Date**: 2026-01-27
   - **Severity**: Low
   - **Description**: AttributeError when `user_id` is None in rate limiter middleware
   - **Fix**: Added graceful handling with default value "anonymous"
   - **File**: `src/middleware/rate_limiter.py`

3. **Synchronous Database Operations Blocking Requests**
   - **Date**: 2026-01-27
   - **Severity**: Medium
   - **Description**: Audit logging middleware performed synchronous database operations, blocking request processing
   - **Fix**: Converted to async background task processing
   - **File**: `src/middleware/audit_logger.py`

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by:

1. **DO NOT** open a public GitHub issue
2. Email the security details to: [security contact would go here]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to respond to security reports within 48 hours and will keep you informed of the fix progress.

## Security Best Practices

When deploying this application:

1. **Environment Variables**
   - Always use strong, randomly generated values for `SECRET_KEY` and `JWT_SECRET_KEY`
   - Never commit `.env` file to version control
   - Use different secrets for production and development

2. **Database**
   - Use strong database passwords
   - Enable SSL connections in production
   - Regularly backup database
   - Keep PostgreSQL updated

3. **Dependencies**
   - Regularly run `pip list --outdated` to check for updates
   - Monitor security advisories for Python packages
   - Use tools like `safety` or `pip-audit` to scan for vulnerabilities

4. **Rate Limiting**
   - Keep rate limiting enabled in production
   - Adjust limits based on your tier structure
   - Monitor for abuse patterns

5. **Audit Logs**
   - Keep audit logs enabled
   - Regularly review logs for suspicious activity
   - Set up alerts for critical actions

6. **HTTPS**
   - Always use HTTPS in production
   - Configure proper SSL/TLS certificates
   - Enable HSTS headers

7. **CORS**
   - Configure CORS to only allow trusted origins
   - Never use `allow_origins=["*"]` in production

8. **Stripe**
   - Use Stripe test keys in development
   - Verify webhook signatures
   - Keep Stripe SDK updated

## Security Scanning

This project uses:
- **CodeQL**: Static code analysis (0 vulnerabilities found)
- **Dependency Scanning**: GitHub Advisory Database checks
- **Code Review**: Automated code review for security issues

Last security scan: 2026-01-27
Status: ✅ All known vulnerabilities addressed

## Contact

For security concerns, please contact the repository maintainers.
