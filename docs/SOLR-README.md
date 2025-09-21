# Solr Service Management

This directory contains scripts to manage the Apache Solr service for the Neo4j Graph Visualization application.

## Environment Configuration

Solr configuration is stored in `.env.local`:

```bash
# Solr Configuration
SOLR_HOME="D:\Software\solr-9.9.0"
SOLR_PORT="8983"
SOLR_BIN_PATH="D:\Software\solr-9.9.0\bin"
SOLR_START_COMMAND="cmd /c solr.cmd start"
SOLR_STOP_COMMAND="cmd /c solr.cmd stop"
SOLR_STATUS_COMMAND="cmd /c solr.cmd status"
```

## Service Management Scripts

### Individual Scripts

- `start-solr.bat` - Start the Solr service
- `stop-solr.bat` - Stop the Solr service
- `status-solr.bat` - Check Solr service status
- `restart-solr.bat` - Restart the Solr service

### Unified Script

- `solr-service.bat [command]` - Unified service management

#### Usage Examples:

```batch
# Start Solr
solr-service.bat start

# Stop Solr
solr-service.bat stop

# Check status
solr-service.bat status

# Restart Solr
solr-service.bat restart
```

## Service URLs

- Solr Admin Interface: http://localhost:8983
- Solr System Info: http://localhost:8983/solr/admin/info/system

## Integration with Application

The Solr service is used by the backend for:
- Full-text search capabilities
- Document indexing
- Query processing

## Troubleshooting

1. **Port already in use**: Check if another Solr instance is running
2. **Permission errors**: Run as administrator
3. **Java not found**: Ensure Java 11+ is installed and in PATH
4. **Configuration issues**: Verify paths in .env.local are correct

## Monitoring

Use `test-services.bat` to check the status of all services including Solr.