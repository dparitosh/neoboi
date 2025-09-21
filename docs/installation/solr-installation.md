# Apache Solr Installation and Configuration Guide

## Overview
Apache Solr is used for full-text search and indexing in the NeoBoi application.

## Installation

### Download and Setup
1. Download Apache Solr from: https://solr.apache.org/downloads.html
2. Choose version 9.4.1 (latest stable)
3. Extract to `C:\solr\solr-9.4.1`
4. Set environment variables:
   ```
   SOLR_HOME=C:\solr\solr-9.4.1
   PATH=%PATH%;%SOLR_HOME%\bin
   ```

## Configuration

### Start Solr
```batch
# Start Solr in cloud mode
solr start -c

# Or start with specific port
solr start -c -p 8983
```

### Create Core for NeoBoi
```batch
# Create a new core named 'neoboi'
solr create -c neoboi

# Or create with specific configuration
solr create -c neoboi -d basic_configs
```

### Core Configuration
1. Navigate to `%SOLR_HOME%\server\solr\neoboi\conf`
2. Update `solrconfig.xml` for your needs
3. Update `managed-schema.xml` or use schema API

## Schema Configuration

### Using Schema API (Recommended)
```bash
# Add fields to schema
curl -X POST -H 'Content-type:application/json' \
  'http://localhost:8983/solr/neoboi/schema' \
  -d '{
    "add-field": {
      "name": "title",
      "type": "text_general",
      "stored": true,
      "indexed": true
    }
  }'
```

### Basic Schema Fields for NeoBoi
```json
{
  "add-field": [
    {"name": "id", "type": "string", "stored": true, "indexed": true, "required": true},
    {"name": "title", "type": "text_general", "stored": true, "indexed": true},
    {"name": "content", "type": "text_general", "stored": true, "indexed": true},
    {"name": "author", "type": "string", "stored": true, "indexed": true},
    {"name": "created_at", "type": "pdate", "stored": true, "indexed": true},
    {"name": "tags", "type": "string", "stored": true, "indexed": true, "multiValued": true},
    {"name": "file_path", "type": "string", "stored": true, "indexed": false},
    {"name": "file_size", "type": "plong", "stored": true, "indexed": true}
  ]
}
```

## Service Management

### Windows Service Setup
```batch
# Install as Windows service
solr.cmd install

# Start service
solr start -all

# Stop service
solr stop -all

# Remove service
solr.cmd uninstall
```

### Manual Control
```batch
# Start Solr
solr start -c -p 8983

# Stop Solr
solr stop -all

# Check status
solr status
```

## Verification

1. Open browser to http://localhost:8983
2. Navigate to Core Admin
3. Verify 'neoboi' core exists
4. Test search: http://localhost:8983/solr/neoboi/select?q=*:*

## Integration with NeoBoi

Update your `.env.local` file:
```env
SOLR_URL=http://localhost:8983/solr/neoboi
SOLR_CORE=neoboi
```

## Data Import

### Using Post Tool
```batch
# Index documents
java -jar %SOLR_HOME%\example\exampledocs\post.jar *.pdf

# Or use curl
curl 'http://localhost:8983/solr/neoboi/update?commit=true' \
  -H 'Content-Type: application/json' \
  -d '[{"id": "doc1", "title": "Sample Document", "content": "Sample content"}]'
```

## Troubleshooting

### Common Issues
1. **Port conflicts**: Change port in solr.cmd or use -p flag
2. **Java version**: Ensure Java 11+ is installed
3. **Memory issues**: Adjust JVM settings in solr.in.cmd

### Logs
Solr logs are located in `%SOLR_HOME%\server\logs\solr.log`