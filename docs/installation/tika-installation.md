# Apache Tika Installation and Configuration Guide

## Overview
Apache Tika is used for document parsing and metadata extraction in the NeoBoi application.

## Installation

### Option 1: Download JAR File (Standalone)
1. Download from: https://tika.apache.org/download.html
2. Choose the latest stable release (e.g., tika-app-2.9.1.jar)
3. Place in a dedicated directory: `C:\tika\tika-app-2.9.1.jar`

### Option 2: Using Maven/Gradle (For Development)
```xml
<!-- Maven dependency -->
<dependency>
    <groupId>org.apache.tika</groupId>
    <artifactId>tika-core</artifactId>
    <version>2.9.1</version>
</dependency>

<dependency>
    <groupId>org.apache.tika</groupId>
    <artifactId>tika-parsers-standard-package</artifactId>
    <version>2.9.1</version>
</dependency>
```

### Option 3: Using pip (Python)
```bash
pip install tika
```

## Configuration

### Environment Setup
```batch
# Set environment variables
TIKA_HOME=C:\tika
TIKA_JAR=%TIKA_HOME%\tika-app-2.9.1.jar

# Add to PATH
PATH=%PATH%;%TIKA_HOME%
```

### Java Requirements
Ensure Java 8+ is installed:
```batch
java -version
```

## Service Management

### Start Tika Server
```batch
# Start Tika server on default port 9998
java -jar %TIKA_JAR% --server --host 0.0.0.0 --port 9998

# Start with custom configuration
java -jar %TIKA_JAR% --server --host localhost --port 9998 --cors
```

### Windows Service Setup
Create a batch file for service management:

```batch
@echo off
REM tika-service.bat
java -jar "C:\tika\tika-app-2.9.1.jar" --server --host 0.0.0.0 --port 9998
```

## Verification

### Test Server
```batch
# Test server connectivity
curl http://localhost:9998/version

# Test document parsing
curl -X PUT --data-binary @sample.pdf \
  -H "Content-Type: application/pdf" \
  http://localhost:9998/tika
```

### Python Integration Test
```python
import requests

# Test Tika server
try:
    response = requests.get('http://localhost:9998/version')
    print(f"Tika version: {response.text}")

    # Test document parsing
    with open('sample.pdf', 'rb') as f:
        response = requests.put(
            'http://localhost:9998/tika',
            data=f,
            headers={'Content-Type': 'application/pdf'}
        )
        print(f"Extracted text: {response.text[:200]}...")

except Exception as e:
    print(f"Error: {e}")
```

## Integration with NeoBoi

Update your `.env.local` file:
```env
TIKA_URL=http://localhost:9998
TIKA_TIMEOUT=300
TIKA_MAX_FILE_SIZE=100MB
```

## Supported File Types

Tika supports 1400+ file types including:
- **Documents**: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX
- **Text files**: TXT, RTF, ODT, ODS, ODP
- **Images**: JPEG, PNG, GIF, BMP, TIFF
- **Archives**: ZIP, TAR, GZ, BZ2
- **Email**: EML, MSG
- **Web**: HTML, XML, JSON
- **Audio/Video**: MP3, MP4, AVI, etc.

## Python Integration

### Using tika-python
```python
from tika import parser
import requests

# Method 1: Using tika-python library
def extract_with_tika_python(file_path):
    parsed = parser.from_file(file_path)
    return {
        'content': parsed['content'],
        'metadata': parsed['metadata']
    }

# Method 2: Using requests directly
def extract_with_requests(file_path):
    url = 'http://localhost:9998/tika'
    headers = {'Content-Type': 'application/pdf'}  # Adjust based on file type

    with open(file_path, 'rb') as f:
        response = requests.put(url, data=f, headers=headers)

    return response.text
```

### Advanced Configuration
```python
import tika
from tika import config

# Configure Tika
config.configure({
    'tika': {
        'server': 'http://localhost:9998',
        'timeout': 300,
        'max_filesize': 100 * 1024 * 1024  # 100MB
    }
})

# Extract with metadata
parsed = parser.from_file('document.pdf', xmlContent=True)
print(f"Title: {parsed['metadata'].get('title')}")
print(f"Author: {parsed['metadata'].get('Author')}")
print(f"Content: {parsed['content'][:500]}...")
```

## Performance Optimization

### Server Configuration
```java
// JVM settings for better performance
java -Xmx2g -Xms512m -jar tika-app-2.9.1.jar --server
```

### Connection Pooling
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure session with retries
session = requests.Session()
retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Use session for requests
response = session.put('http://localhost:9998/tika', data=file_data)
```

## Troubleshooting

### Common Issues
1. **Server won't start**: Check Java version and port availability
2. **Timeout errors**: Increase timeout in configuration
3. **Memory issues**: Adjust JVM heap size
4. **File parsing errors**: Check file format support

### Error Handling
```python
def safe_tika_extract(file_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            parsed = parser.from_file(file_path)
            return parsed
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff

    return None
```

### Logs
Tika server logs errors to console. For production, redirect output:
```batch
java -jar tika-app-2.9.1.jar --server > tika.log 2>&1
```

## Security Considerations

### File Upload Limits
```python
# Implement file size limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def validate_file(file_path):
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        raise ValueError("File too large")

    # Check file type
    import magic
    mime = magic.from_file(file_path, mime=True)
    allowed_types = ['application/pdf', 'text/plain', 'application/msword']
    if mime not in allowed_types:
        raise ValueError(f"Unsupported file type: {mime}")
```

### CORS Configuration
```batch
# Start with CORS enabled
java -jar tika-app-2.9.1.jar --server --cors
```