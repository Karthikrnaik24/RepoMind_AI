# Docker

Docker-related assets live here.

## Files

- `web.Dockerfile`: Production container definition for the Next.js frontend.
- `api.Dockerfile`: Production container definition for the FastAPI backend.

The root `docker-compose.yml` wires the application containers to PostgreSQL and Redis for local infrastructure.

Keep production images minimal and free of secrets.
