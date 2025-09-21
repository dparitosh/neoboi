# Tesseract OCR Installation and Configuration Guide

## Overview
Tesseract OCR is used for optical character recognition in documents processed by the NeoBoi application.

## Installation

### Option 1: Using Chocolatey (Recommended)
```powershell
# Install Chocolatey if not already installed
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install Tesseract
choco install tesseract
```

### Option 2: Manual Installation
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Choose the Windows installer (tesseract-ocr-w64-setup-v5.3.0.20221214.exe)
3. Run installer and follow prompts
4. Install to default location: `C:\Program Files\Tesseract-OCR`

### Option 3: Using conda
```bash
# Create conda environment
conda create -n ocr python=3.9
conda activate ocr

# Install Tesseract
conda install -c conda-forge tesseract
```

## Language Data Installation

### Download Language Files
```batch
# Create tessdata directory if it doesn't exist
mkdir "C:\Program Files\Tesseract-OCR\tessdata"

# Download English language data
curl -o "C:\Program Files\Tesseract-OCR\tessdata\eng.traineddata" https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata

# Download additional languages as needed
curl -o "C:\Program Files\Tesseract-OCR\tessdata\fra.traineddata" https://github.com/tesseract-ocr/tessdata/raw/main/fra.traineddata
```

## Configuration

### Environment Variables
Add to system PATH:
```
TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```

### Python Integration
```python
import pytesseract
from PIL import Image

# Configure Tesseract path (if not in PATH)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Test OCR
image = Image.open('sample.png')
text = pytesseract.image_to_string(image)
print(text)
```

## Verification

### Command Line Test
```batch
# Test Tesseract installation
tesseract --version

# Test OCR on an image
tesseract sample.png output -l eng

# List available languages
tesseract --list-langs
```

### Python Test
```python
import pytesseract
from PIL import Image

# Test basic functionality
try:
    version = pytesseract.get_tesseract_version()
    print(f"Tesseract version: {version}")

    # Test with a simple image
    image = Image.new('RGB', (100, 30), color='white')
    text = pytesseract.image_to_string(image)
    print("OCR test successful")

except Exception as e:
    print(f"Error: {e}")
```

## Integration with NeoBoi

Update your `.env.local` file:
```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
TESSERACT_DATA=C:\Program Files\Tesseract-OCR\tessdata
OCR_LANGUAGES=eng,fra
```

## Supported File Types

Tesseract supports various image formats:
- PNG, JPEG, TIFF, BMP, GIF
- PDF (with pdf2image conversion)
- Multi-page TIFF files

## Performance Optimization

### Image Preprocessing
```python
import cv2
import numpy as np
from PIL import Image

def preprocess_image(image_path):
    # Read image
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply threshold to get binary image
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Save preprocessed image
    cv2.imwrite('preprocessed.png', thresh)
    return 'preprocessed.png'
```

### Configuration Options
```python
# High accuracy configuration
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# Fast configuration
fast_config = r'--oem 1 --psm 8'
```

## Troubleshooting

### Common Issues
1. **"tesseract is not recognized"**: Add Tesseract to PATH
2. **Language data not found**: Ensure TESSDATA_PREFIX is set correctly
3. **Poor OCR quality**: Preprocess images or adjust PSM mode
4. **Memory issues**: Process images in batches

### Error Messages
- **"Error opening data file"**: Check TESSDATA_PREFIX and language files
- **"Image too large"**: Resize large images before processing
- **"Empty page"**: Check image quality and preprocessing

### Logs and Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test with verbose output
text = pytesseract.image_to_string(image, config='--psm 6', lang='eng')
```