# Getting Started with Multi-Tenant SaaS Platform

This guide will help you get the project up and running.

## Prerequisites

- Docker and Docker Compose
- Git (for setting up commit history)
- (Optional) Python 3.11+ for local development

## Step 1: Review the Project

Take a look at the project structure:

```bash
tree -L 2 -I '__pycache__|*.pyc'
```

Key files to review:
- `README.md` - Main project documentation
- `SECURITY.md` - Security policy and best practices
- `.env.example` - Environment configuration template

## Step 2: Set Up Environment

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Edit `.env` and update:
- `SECRET_KEY` - Generate a secure random key
- `JWT_SECRET_KEY` - Generate another secure random key
- `STRIPE_SECRET_KEY` - Add your Stripe test key (if testing billing)
- `STRIPE_WEBHOOK_SECRET` - Add your Stripe webhook secret

Generate secure keys with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Start Services

Start all services with Docker Compose:

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis cache
- FastAPI application
- Celery worker
- Celery beat scheduler

Check logs:
```bash
docker-compose logs -f
```

## Step 4: Run Database Migrations

Create the database schema with Row-Level Security policies:

```bash
docker-compose exec api alembic upgrade head
```

## Step 5: Create Admin User (Optional)

Create an initial admin user for testing:

```bash
docker-compose exec api python -m src.cli create-superuser \
  --email admin@example.com \
  --password admin123 \
  --org-name "My Organization" \
  --org-slug my-org
```

## Step 6: Access the API

The API is now running at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Try the interactive API documentation at `/docs` to test endpoints.

## Step 7: Run Tests

Run the test suite:

```bash
# Run all tests
docker-compose exec api pytest

# With coverage report
docker-compose exec api pytest --cov=src --cov-report=html

# View coverage report (generates in htmlcov/)
docker-compose exec api pytest --cov=src --cov-report=term
```

## Quick Commands

Use the Makefile for common tasks:

```bash
make up        # Start services
make down      # Stop services
make migrate   # Run migrations
make test      # Run tests
make logs      # View logs
make shell     # Open shell in API container
make clean     # Clean up everything
```

## Testing the API

### 1. Register a New Organization

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Test Company",
    "organization_slug": "test-company",
    "email": "user@test.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

This returns access and refresh tokens.

### 2. Use the Access Token

```bash
# Get current user profile
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get organization details
curl -X GET http://localhost:8000/api/v1/organizations/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Test Rate Limiting

The free tier allows 100 requests per hour. Try making multiple requests and check the rate limit headers:

```bash
curl -i http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Look for headers:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## Development Workflow

### Local Development (Without Docker)

If you prefer to develop without Docker:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://..."
export REDIS_URL="redis://..."
# ... other env vars

# Run the application
uvicorn src.main:app --reload

# Run tests
pytest
```

### Making Changes

1. Make code changes
2. Run tests: `docker-compose exec api pytest`
3. Check logs: `docker-compose logs -f api`
4. Restart services if needed: `docker-compose restart api`

### Creating New Migrations

After changing models:

```bash
docker-compose exec api alembic revision --autogenerate -m "description of changes"
docker-compose exec api alembic upgrade head
```

## Architecture Overview

```
Client → FastAPI → Middleware Stack → Database/Redis
                   ↓
            - Tenant Context
            - Rate Limiter
            - Audit Logger
```

### Data Flow

1. **Request arrives** → Tenant Context Middleware extracts org_id from JWT
2. **Rate Limiter** → Checks Redis for request count
3. **Route Handler** → Processes request with DB session
4. **Database** → RLS policies filter by org_id automatically
5. **Response** → Audit Logger records action
6. **Client** → Receives response with rate limit headers

## Common Issues

### Port Already in Use

If port 8000, 5432, or 6379 is already in use:

```bash
# Change ports in docker-compose.yml
# For example: "8001:8000" instead of "8000:8000"
```

### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker-compose ps

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Redis Connection Errors

```bash
# Check Redis status
docker-compose exec redis redis-cli ping
# Should return: PONG
```

### Migration Errors

```bash
# Reset migrations (WARNING: destroys data)
docker-compose down -v
docker-compose up -d
docker-compose exec api alembic upgrade head
```

## Project Features

- ✅ Multi-tenant architecture with RLS
- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Rate limiting per organization
- ✅ Audit logging
- ✅ Stripe subscription billing
- ✅ Background jobs with Celery
- ✅ Comprehensive API documentation
- ✅ Docker-based development
- ✅ Test suite with pytest

## Next Steps

1. Explore the API documentation at http://localhost:8000/docs
2. Review the code in `src/` to understand the architecture
3. Customize for your needs!

## Support

For questions or issues, review the code and documentation.

## License

MIT License - See LICENSE file
