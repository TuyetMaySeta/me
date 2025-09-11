# Database Connection Management

## Overview

The EMS FastAPI server implements basic database connection management with proper connection pooling for reliability and performance.

## Database Connection Features

### Connection Pool Management
- **Pool Size**: 10 connections maintained
- **Max Overflow**: 20 additional connections
- **Pre-ping**: Tests connections before use
- **Recycle**: Connections recycled every 5 minutes
- **Timeout**: 30-second timeout for getting connections

### Connection Testing
Each database session is properly managed through SQLAlchemy's connection pooling system.

## Health Monitoring

### Health Check Endpoint

**Basic Health Check** (`/health`):
```json
{
  "status": "ok"
}
```

## Configuration

### Environment Variables
```bash
# Database connection settings
DATABASE_URL=postgresql://user:password@localhost:5432/ems_db
```

## Best Practices

### Database Operations
- Use proper session management through dependency injection
- Monitor connection pool metrics
- Handle database errors gracefully

### Error Handling
- Implement proper error responses
- Log database connection issues
- Use appropriate HTTP status codes

## Troubleshooting

### Common Issues

1. **Database Connection Failures**
   - Check PostgreSQL service status
   - Verify connection string
   - Review connection pool settings

### Health Check Commands
```bash
# Check application health
curl http://localhost:8000/ems/api/v1/health

# Test database connection directly
psql -h localhost -U user -d ems_db -c "SELECT 1"
```