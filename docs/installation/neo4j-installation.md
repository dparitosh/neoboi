# Neo4j Configuration Guide

## Overview
This application supports both **Neo4j Aura** (cloud) and **On-Premise Neo4j** deployments. The system automatically detects your deployment type and configures itself accordingly.

## Deployment Options

### Option 1: Neo4j Aura (Cloud) - RECOMMENDED

#### Advantages
- Fully managed cloud service
- Automatic scaling and backups
- Native vector index support (5.17+)
- No local installation required
- Enterprise-grade security

#### Setup Steps
1. Visit: https://neo4j.com/cloud/aura/
2. Sign up for a free account (or use existing account)
3. Create a new AuraDB instance
4. Choose instance type: AuraDB Free or Professional
5. Select region for best performance
6. Ensure version 5.17+ for vector support

#### Connection Details
After creating the instance, note these details:
- **Connection URI**: `neo4j+s://xxxxx.databases.neo4j.io`
- **Username**: `neo4j`
- **Password**: Generated password (save securely)
- **Database**: `neo4j`

### Option 2: On-Premise Neo4j

#### Advantages
- Full control over infrastructure
- Custom configurations
- No cloud dependency
- Suitable for air-gapped environments

#### Requirements
- Neo4j 5.17+ for vector index support
- Java 17+
- Sufficient RAM (4GB+ recommended)
- Vector indexes require Enterprise Edition or 5.17+ Community

#### Installation Options

##### Option 2a: Neo4j Desktop
1. Download from: https://neo4j.com/download/
2. Install and create local database instance
3. Start the database
4. Note connection details:
   - **URI**: `bolt://localhost:7687`
   - **Username**: `neo4j`
   - **Password**: Set during installation
   - **Database**: `neo4j`

##### Option 2b: Neo4j Server
1. Download Community/Enterprise Server 5.17+
2. Extract to desired location
3. Configure `neo4j.conf` if needed
4. Start with: `bin/neo4j console` or `bin/neo4j start`
5. Default connection:
   - **URI**: `bolt://localhost:7687`
   - **Username**: `neo4j`
   - **Password**: Set during first start

## Configuration

### Environment Configuration
Update your `.env.local` file based on your deployment choice:

#### For Neo4j Aura (Cloud):
```env
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_generated_password
NEO4J_DATABASE=neo4j
```

#### For On-Premise Neo4j:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_local_password
NEO4J_DATABASE=neo4j
```

### Automatic Deployment Detection
The application automatically detects your deployment type:
- **Aura**: URI starts with `neo4j+s://` or contains `databases.neo4j.io`
- **On-Premise**: URI starts with `bolt://` or `neo4j://`

## Vector Index Support

### Neo4j Aura
- ✅ Native vector index support (5.17+)
- ✅ Automatic configuration
- ✅ Optimized for cloud performance

### On-Premise Neo4j
- ✅ Vector indexes supported in 5.17+
- ⚠️ Requires Enterprise Edition for production
- ⚠️ Manual configuration may be needed

## Verification

### Test Connection
```bash
# The application will test connection on startup
# Check backend logs for connection status and deployment type
```

### Browser Access
- **Neo4j Aura**: Access via https://your-instance.databases.neo4j.io/browser/
- **On-Premise**: Access via http://localhost:7474 (if enabled)

## Troubleshooting

### Connection Issues
1. **Aura**: Check IP whitelisting in Neo4j Aura dashboard
2. **On-Premise**: Verify Neo4j service is running: `bin/neo4j status`
3. Check firewall settings for database port (7687)
4. Verify credentials in `.env.local`

### Vector Index Issues
1. **Aura**: Ensure instance version is 5.17+
2. **On-Premise**: Check Neo4j version: `bin/neo4j --version`
3. Verify Enterprise Edition for production use

### Performance Considerations
- **Aura**: Automatically optimized for your workload
- **On-Premise**: Monitor system resources (RAM, CPU, Disk I/O)
- Consider vector index memory requirements

## Migration Between Deployments

### From On-Premise to Aura
1. Create Neo4j Aura instance
2. Export data from on-premise: `bin/neo4j-admin database dump neo4j`
3. Import to Aura using Neo4j Admin or data import tools
4. Update `.env.local` with Aura credentials
5. Restart application

### From Aura to On-Premise
1. Set up on-premise Neo4j instance
2. Export data from Aura (if supported by your plan)
3. Import to on-premise instance
4. Update `.env.local` with local credentials
5. Restart application

## Best Practices

### Security
- Use strong passwords
- Enable encryption in transit (`neo4j+s://` for Aura)
- Configure IP whitelisting for Aura
- Regular password rotation

### Performance
- Monitor query performance
- Use appropriate instance sizes
- Configure connection pooling
- Optimize vector index usage

### Backup & Recovery
- **Aura**: Automatic backups included
- **On-Premise**: Implement regular backup strategy
- Test restore procedures regularly

### Option 2: Neo4j Server
1. Download Community Server 5.17+
2. Extract and configure
3. Start with: `neo4j console`
4. Use same connection settings as above

**Note**: Vector indexes require Neo4j 5.17+. Local installations may have compatibility issues.