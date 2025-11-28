# Docker Setup for Pharma Research Platform

This document explains how to run the Pharma Research Platform using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Quick Start

1. **Start all services:**

   ```bash
   docker-compose up -d
   ```

2. **View logs:**

   ```bash
   docker-compose logs -f web
   ```

3. **Access the application:**

   - Web Application: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

4. **Stop all services:**
   ```bash
   docker-compose down
   ```

## Services

### Web Application (`web`)

- FastAPI application with CrewAI agents
- Accessible at http://localhost:8000
- Auto-reloads on code changes (development mode)
- **Supports agent code execution**: Docker socket is mounted to allow CrewAI agents (like `visualization_agent`) to spawn containers for executing Python code safely

### Database (`db`)

- PostgreSQL 15 database
- Accessible at localhost:5432
- Data persisted in Docker volume `postgres_data`

### Database (`db`)

- PostgreSQL 15 database
- Accessible at localhost:5432
- Data persisted in Docker volume `postgres_data`

### PgAdmin (Optional)

- Database management interface
- Start with: `docker-compose --profile admin up -d`
- Accessible at http://localhost:5050
- Default credentials: admin@pharma.com / admin

## Agent Code Execution

The Docker setup supports **CrewAI agent code execution** for agents like `visualization_agent`. This is achieved by:

1. **Docker-in-Docker**: The Docker socket (`/var/run/docker.sock`) is mounted into the web container
2. **Docker CLI installed**: The container includes Docker CLI to communicate with the host Docker daemon
3. **Dynamic group mapping**: The container user is added to the host's docker group at runtime via `group_add`
4. **Full capabilities**: Capability restrictions (`cap_drop`/`cap_add`) are removed to allow subprocess execution

**Why dynamic group mapping:**

- Different systems have different docker group IDs
- `group_add: ${DOCKER_GID:-999}` adds the container user to the host's docker group
- This ensures Docker socket permissions work across all systems
- Set `DOCKER_GID` in `.env` to match your host (default: 999)

**Finding your docker GID:**

- Linux: `getent group docker | cut -d: -f3`
- Windows/Mac with Docker Desktop: Usually 999 (default)

**Why full capabilities are needed:**

- CrewAI spawns subprocesses for code execution
- Agents need to execute shell commands
- Docker-in-Docker requires filesystem read/write
- Subprocess creation requires standard Linux capabilities

When an agent needs to execute code (e.g., generating visualizations with matplotlib), CrewAI will:

- Spawn a new Docker container on the host
- Execute the Python code in isolation
- Return the results to the agent
- Clean up the container automatically

To enable code execution for an agent, uncomment `allow_code_execution: true` in `agents/src/pharma_researcher/config/agents.yaml`.

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Database
POSTGRES_DB=pharma_research
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PORT=5432

# Web Application
WEB_PORT=8000
SECRET_KEY=your-secret-key-here

# Docker Socket Access (for agent code execution)
# Get your docker group ID with: getent group docker | cut -d: -f3
# On Windows/Mac with Docker Desktop, use 999
DOCKER_GID=999

# API Keys
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
SERPER_API_KEY=your_serper_key
PATENTS_VIEW_API_KEY=your_patents_view_key

# PgAdmin (optional)
PGADMIN_EMAIL=admin@pharma.com
PGADMIN_PASSWORD=admin
PGADMIN_PORT=5050
```

## Common Commands

### Build and Start

```bash
# Build images and start services
docker-compose up --build -d

# Start services without building
docker-compose up -d

# Start with PgAdmin
docker-compose --profile admin up -d
```

### Logs and Monitoring

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f db

# Check service status
docker-compose ps
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d pharma_research

# Run migrations
docker-compose exec web python -m alembic upgrade head

# Backup database
docker-compose exec db pg_dump -U postgres pharma_research > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres pharma_research < backup.sql
```

### Maintenance

```bash
# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Restart a specific service
docker-compose restart web

# Rebuild a specific service
docker-compose up -d --build web

# Execute commands in container
docker-compose exec web bash
```

## Development Workflow

1. **Make code changes** - Changes are automatically reflected due to volume mounts
2. **View logs** - `docker-compose logs -f web`
3. **Restart if needed** - `docker-compose restart web`

## Production Deployment

For production, modify `docker-compose.yml`:

1. Remove `--reload` flag from uvicorn command
2. Set proper environment variables
3. Use secrets management for sensitive data
4. Configure proper resource limits
5. Set up SSL/TLS termination (nginx/traefik)

## Troubleshooting

### Port Already in Use

```bash
# Change ports in .env file
WEB_PORT=8001
POSTGRES_PORT=5433
```

### Database Connection Issues

```bash
# Check database health
docker-compose exec db pg_isready -U postgres

# Restart database
docker-compose restart db
```

### Container Won't Start

```bash
# View detailed logs
docker-compose logs web

# Check container status
docker-compose ps

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Database Initialization Errors

If you see errors like `ERROR: relation "queries" does not exist` during database startup:

**Problem:** Migration scripts in the `migrations/` folder are running before tables are created.

**Solution:**

1. The `migrations/` folder is for **initial schema setup only**
2. Move any ALTER TABLE scripts out of migrations (they're for existing databases)
3. The FastAPI app creates tables automatically via SQLAlchemy on startup
4. Clean up and restart:
   ```bash
   docker-compose down -v  # Remove volumes
   docker-compose up --build -d
   ```

**Note:** The `migrations/` folder is mounted as `/docker-entrypoint-initdb.d/` in PostgreSQL, which runs all `.sql` files during first-time initialization. Only put CREATE TABLE scripts here, not ALTER TABLE migrations.

### Clear Everything and Start Fresh

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Rebuild and start
docker-compose up --build -d
```

## Volume Management

Data is persisted in Docker volumes:

- `postgres_data` - Database files
- `pgadmin_data` - PgAdmin configuration

To backup volumes:

```bash
docker run --rm -v pharma_research_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## Security Notes

### General Security

- Change default passwords in production
- Use Docker secrets for sensitive data
- Run containers as non-root user (already configured)
- Keep images updated regularly
- Use specific image versions in production

### Agent Code Execution Security

**Trade-offs:**
The container runs with full capabilities and Docker socket access to enable CrewAI code execution. This provides:

- ✅ Agent code execution in isolated containers
- ✅ Subprocess and shell command support
- ⚠️ Elevated privileges (can spawn containers on host)

**Mitigation strategies:**

1. **Trust your agents**: Only enable `allow_code_execution` for agents you trust
2. **Network isolation**: Use Docker networks to limit container communication
3. **Resource limits**: CPU and memory limits are configured to prevent runaway processes
4. **Non-root user**: Container runs as `pharma_user` (UID 1000), not root
5. **No new privileges**: `security_opt: no-new-privileges:true` prevents privilege escalation
6. **Production hardening**: For production, consider:
   - Using Docker-in-Docker (DinD) sidecar instead of socket mounting
   - Implementing stricter AppArmor/SELinux profiles
   - Running in a dedicated VM or isolated environment
   - Using Kubernetes with Pod Security Standards
