# Multi-Tenant SaaS Platform 🚀

Personal project to learn about multi-tenant architectures. FastAPI backend with PostgreSQL RLS for tenant isolation. Started this to understand row-level security better.

## What it does

Basic multi-tenant platform with user auth and org management. Still learning RLS policies but getting there. Works pretty well for what I needed.

## Quick Start ⚡

```bash
# Setup
cp .env.example .env
# Edit .env with your settings

# Start with Docker
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# API at http://localhost:8000/docs
```

## Features

- Multi-tenant architecture with RLS isolation 🔒
- JWT auth with tenant context
- Rate limiting per org
- Background jobs with Celery
- Health checks and monitoring 📊
- Docker dev environment
- Audit logging for compliance
- Helm chart for Kubernetes deployment
- CI/CD pipeline with GitHub Actions

## Architecture

Simple FastAPI app with PostgreSQL and Redis. The RLS implementation was trickier than expected but works.

## Deployment

### Kubernetes with Helm
```bash
# Install the Helm chart
helm install saas-platform charts/multi-tenant-saas

# Or with custom values
helm install saas-platform charts/multi-tenant-saas -f my-values.yaml
```

## DevOps

- **CI/CD**: GitHub Actions workflow handles testing, building, and deployment
- **Containerized**: Docker images built and pushed on merge to main
- **Kubernetes**: Helm chart for easy deployment
- **Testing**: Automated tests with coverage reporting

## TODO

- [ ] Add websocket support for real-time features
- [ ] Better email notifications (currently just logs)
- [ ] More test coverage (around 60% now)
- [ ] Metrics export for Prometheus
- [ ] Org member invitations via email
- [ ] 2FA support
- [ ] Background job for cleaning old audit logs

## Notes

RLS implementation was trickier than expected. Had to carefully handle session context to avoid data leaks. Based on some online articles but adapted for my use case.

The subscription model is basic - just three tiers. Real impl would need more flexibility.

Performance is good up to 50k orgs in testing. Haven't tested beyond that but should scale fine with proper indexing.

Still learning: the Stripe webhook validation sometimes fails in dev mode, and the rate limiter doesn't handle Redis failures gracefully yet.


