"""
OCR Service for extracting text from images and scanned documents
"""
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

class OCRService:
    """Service for OCR text extraction from images and documents"""

    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize OCR service

        Args:
            tesseract_path: Path to tesseract executable (optional)
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            # Try to find tesseract in common locations
            common_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'D:\Program Files\Tesseract-OCR\tesseract.exe'
            ]
            for path in common_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break

        # Configure Tesseract for better accuracy
        self.config = '--oem 3 --psm 6'

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy

        Args:
            image: Input image as numpy array

        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        return thresh

    def extract_text(self, image_data: bytes, filename: str = "") -> Dict[str, Any]:
        """
        Extract text from image data

        Args:
            image_data: Raw image bytes
            filename: Original filename for context

        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))

            # Convert PIL to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Preprocess image
            processed_image = self.preprocess_image(opencv_image)

            # Extract text using Tesseract
            text = pytesseract.image_to_string(processed_image, config=self.config)

            # Get additional data
            data = pytesseract.image_to_data(processed_image, config=self.config, output_type=pytesseract.Output.DICT)

            # Calculate confidence score
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            result = {
                'text': text.strip(),
                'confidence': avg_confidence,
                'word_count': len(text.split()),
                'filename': filename,
                'success': True,
                'metadata': {
                    'image_width': image.width,
                    'image_height': image.height,
                    'processing_method': 'tesseract_ocr'
                }
            }

            logger.info(f"OCR extraction successful for {filename}: {len(text)} characters, {avg_confidence:.1f}% confidence")
            return result

        except Exception as e:
            logger.error(f"OCR extraction failed for {filename}: {str(e)}")
            return {
                'text': '',
                'confidence': 0,
                'word_count': 0,
                'filename': filename,
                'success': False,
                'error': str(e),
                'metadata': {}
            }

    def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from image file

        Args:
            file_path: Path to image file

        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()

            filename = os.path.basename(file_path)
            return self.extract_text(image_data, filename)

        except Exception as e:
            logger.error(f"Failed to read image file {file_path}: {str(e)}")
            return {
                'text': '',
                'confidence': 0,
                'word_count': 0,
                'filename': os.path.basename(file_path),
                'success': False,
                'error': str(e),
                'metadata': {}
            }

    def get_supported_formats(self) -> list:
        """
        Get list of supported image formats

        Returns:
            List of supported file extensions
        """
        return ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif', '.webp']

    def is_format_supported(self, filename: str) -> bool:
        """
        Check if file format is supported for OCR

        Args:
            filename: Filename to check

        Returns:
            True if format is supported
        """
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.get_supported_formats()