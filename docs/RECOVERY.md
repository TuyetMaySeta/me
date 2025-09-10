# Recovery and Resilience Documentation

## Overview

The EMS FastAPI server implements **global recovery middleware** that wraps all router operations to ensure high availability and resilience against database failures, network issues, and other system disruptions. Recovery is applied at the application level, not individual service methods.

## Recovery Mechanisms

### 1. Database Connection Recovery

#### Connection Pool Management
- **Pool Size**: 10 connections maintained
- **Max Overflow**: 20 additional connections
- **Pre-ping**: Tests connections before use
- **Recycle**: Connections recycled every 5 minutes
- **Timeout**: 30-second timeout for getting connections

#### Retry Logic
- **Max Retries**: 3 attempts for database operations
- **Exponential Backoff**: Increasing delay between retries (1s, 2s, 4s)
- **Connection Testing**: Each connection is tested with `SELECT 1`

#### Startup Recovery
- **Startup Retries**: 5 attempts to connect on server startup
- **Retry Delay**: 2 seconds between startup attempts
- **Graceful Degradation**: Server starts even if database is unavailable

### 2. Global Recovery Middleware

#### Router-Level Recovery
All router operations are automatically wrapped with recovery logic:

```python
# Applied to ALL endpoints automatically
from src.present.middleware.recovery_middleware import RecoveryMiddleware
app.add_middleware(RecoveryMiddleware, max_retries=3, base_delay=1.0)
```

#### Features
- **Automatic Retry**: All database operations retried on failure
- **Exponential Backoff**: 1s, 2s, 4s delays between retries
- **Circuit Breaker**: Per-endpoint circuit breaker (5 failures → 60s timeout)
- **Smart Filtering**: Skips health checks and static endpoints
- **Error Classification**: Only retries database-related errors

#### Circuit Breaker Pattern
- **Failure Threshold**: 5 consecutive failures per endpoint
- **Recovery Timeout**: 60 seconds
- **Per-Endpoint**: Each endpoint has its own circuit breaker
- **Automatic Reset**: Circuit opens after threshold, resets after timeout

### 3. Recovery Monitoring

#### Recovery Status Endpoint
**Recovery Status** (`/recovery/status`):
```json
{
  "recovery_middleware": {
    "max_retries": 3,
    "base_delay": 1.0,
    "circuit_timeout": 60,
    "status": {
      "open_circuits": [],
      "failure_counts": {},
      "circuit_timeout": 60
    }
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### 4. Health Monitoring

#### Health Check Endpoints

**Basic Health Check** (`/health`):
```json
{
  "status": "healthy",
  "service": "EMS FastAPI Server",
  "version": "1.0.0",
  "database": {
    "status": "connected",
    "pool_status": {
      "pool_size": 10,
      "checked_in": 8,
      "checked_out": 2,
      "overflow": 0,
      "invalid": 0
    }
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

**Detailed Health Check** (`/health/detailed`):
```json
{
  "status": "healthy",
  "service": "EMS FastAPI Server",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "pool_status": {...},
      "connection_test": "passed"
    },
    "api": {
      "status": "healthy",
      "endpoints": 12
    }
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### 4. Graceful Shutdown

#### Shutdown Process
1. **Stop accepting new requests**
2. **Complete ongoing requests**
3. **Close database connections**
4. **Log shutdown status**

#### Connection Cleanup
- All database connections are properly closed
- Connection pool is disposed
- Error handling for shutdown failures

## Configuration

### Environment Variables
```bash
# Database connection settings
DATABASE_URL=postgresql://user:password@localhost:5432/ems_db

# Recovery settings (can be added to config)
MAX_RETRIES=3
BASE_DELAY=1.0
STARTUP_RETRIES=5
STARTUP_DELAY=2
```

### Recovery Service Configuration
```python
recovery_service = RecoveryService(
    max_retries=3,      # Number of retry attempts
    base_delay=1.0      # Base delay for exponential backoff
)
```

## Monitoring and Alerting

### Logging
- **INFO**: Successful operations and recovery
- **WARNING**: Retry attempts and circuit breaker events
- **ERROR**: Failed operations after all retries

### Metrics to Monitor
- Database connection pool status
- Retry attempt counts
- Circuit breaker state
- Health check response times
- Error rates by endpoint

## Best Practices

### 1. Database Operations
- Always use the `get_db()` dependency for automatic retry
- Wrap critical operations with retry decorators
- Monitor connection pool metrics

### 2. Error Handling
- Distinguish between retryable and non-retryable errors
- Log all retry attempts for debugging
- Implement proper error responses

### 3. Monitoring
- Set up alerts for health check failures
- Monitor database connection metrics
- Track retry patterns and failure rates

## Testing Recovery

### Manual Testing
1. **Database Disconnection**: Stop PostgreSQL and test endpoints
2. **Connection Pool Exhaustion**: Create many concurrent requests
3. **Network Issues**: Simulate network timeouts

### Automated Testing
```python
# Test retry logic
def test_database_retry():
    # Simulate database failure
    # Verify retry attempts
    # Check final success/failure

# Test circuit breaker
def test_circuit_breaker():
    # Trigger failures
    # Verify circuit opens
    # Test recovery after timeout
```

## Troubleshooting

### Common Issues

1. **Database Connection Failures**
   - Check PostgreSQL service status
   - Verify connection string
   - Review connection pool settings

2. **High Retry Rates**
   - Monitor database performance
   - Check network connectivity
   - Review connection pool configuration

3. **Circuit Breaker Activation**
   - Investigate root cause of failures
   - Check database logs
   - Verify application logs

### Recovery Commands
```bash
# Check database status
curl http://localhost:8000/health/detailed

# Test database connection
psql -h localhost -U user -d ems_db -c "SELECT 1"

# Check server logs
tail -f /var/log/ems/server.log
```

## Future Enhancements

1. **Distributed Circuit Breaker**: For microservices architecture
2. **Metrics Integration**: Prometheus/Grafana monitoring
3. **Auto-scaling**: Based on health metrics
4. **Backup Recovery**: Automatic failover to backup database
5. **Rate Limiting**: Protect against overwhelming the system
