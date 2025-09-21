"""
Tika Service for parsing various document formats
"""
import requests
import logging
from typing import Optional, Dict, Any, Tuple
import os
import subprocess
import time
import socket
import io
from pathlib import Path

logger = logging.getLogger(__name__)

class TikaService:
    """Service for document parsing using Apache Tika"""

    def __init__(self, tika_server_url: str = None):
        """
        Initialize Tika service

        Args:
            tika_server_url: URL of the Tika server
        """
        if tika_server_url is None:
            tika_server_url = os.getenv("TIKA_SERVER_URL", "http://localhost:9998")
        self.server_url = tika_server_url
        self.tika_jar_path = None
        self.server_process = None

    def start_tika_server(self, tika_jar_path: Optional[str] = None) -> bool:
        """
        Start Tika server if not already running

        Args:
            tika_jar_path: Path to tika-server.jar file

        Returns:
            True if server is running
        """
        # Check if server is already running
        if self._is_server_running():
            logger.info("Tika server is already running")
            return True

        # Find tika jar if not provided
        if not tika_jar_path:
            tika_jar_path = self._find_tika_jar()

        if not tika_jar_path or not os.path.exists(tika_jar_path):
            logger.error("Tika server JAR not found")
            return False

        try:
            # Start Tika server
            cmd = ["java", "-jar", tika_jar_path, "--port", "9998"]
            logger.info(f"Starting Tika server: {' '.join(cmd)}")

            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(tika_jar_path)
            )

            # Wait for server to start
            for i in range(30):  # Wait up to 30 seconds
                if self._is_server_running():
                    logger.info("Tika server started successfully")
                    return True
                time.sleep(1)

            logger.error("Tika server failed to start within timeout")
            return False

        except Exception as e:
            logger.error(f"Failed to start Tika server: {str(e)}")
            return False

    def stop_tika_server(self) -> bool:
        """
        Stop Tika server

        Returns:
            True if stopped successfully
        """
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                logger.info("Tika server stopped")
                return True
            except Exception as e:
                logger.error(f"Failed to stop Tika server: {str(e)}")
                return False
        return True

    def _is_server_running(self) -> bool:
        """Check if Tika server is running"""
        try:
            response = requests.get(f"{self.server_url}/version", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _find_tika_jar(self) -> Optional[str]:
        """Find tika-server.jar in common locations"""
        common_paths = [
            "tika-server.jar",
            "lib/tika-server.jar",
            "../lib/tika-server.jar",
            "tika/tika-server.jar"
        ]

        for path in common_paths:
            if os.path.exists(path):
                return os.path.abspath(path)

        return None

    def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parse document using Tika server

        Args:
            file_path: Path to document file

        Returns:
            Dictionary containing parsed content and metadata
        """
        if not self._is_server_running():
            logger.error("Tika server is not running")
            return {
                'success': False,
                'error': 'Tika server not running',
                'content': '',
                'metadata': {}
            }

        try:
            with open(file_path, 'rb') as f:
                files = {'upload': (os.path.basename(file_path), f, 'application/octet-stream')}

                # Get text content
                response = requests.put(
                    f"{self.server_url}/tika",
                    files=files,
                    headers={'Accept': 'text/plain'}
                )

                if response.status_code != 200:
                    return {
                        'success': False,
                        'error': f'Tika parsing failed: {response.status_code}',
                        'content': '',
                        'metadata': {}
                    }

                content = response.text

                # Get metadata
                response = requests.put(
                    f"{self.server_url}/meta",
                    files=files,
                    headers={'Accept': 'application/json'}
                )

                metadata = {}
                if response.status_code == 200:
                    metadata = response.json()

                result = {
                    'success': True,
                    'content': content,
                    'metadata': metadata,
                    'filename': os.path.basename(file_path),
                    'file_size': os.path.getsize(file_path),
                    'word_count': len(content.split()),
                    'processing_method': 'apache_tika'
                }

                logger.info(f"Tika parsing successful for {os.path.basename(file_path)}: {len(content)} characters")
                return result

        except Exception as e:
            logger.error(f"Tika parsing failed for {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'metadata': {},
                'filename': os.path.basename(file_path)
            }

    def parse_document_bytes(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse document from bytes using Tika server

        Args:
            file_data: Raw file bytes
            filename: Original filename

        Returns:
            Dictionary containing parsed content and metadata
        """
        if not self._is_server_running():
            logger.error("Tika server is not running")
            return {
                'success': False,
                'error': 'Tika server not running',
                'content': '',
                'metadata': {}
            }

        try:
            files = {'upload': (filename, io.BytesIO(file_data), 'application/octet-stream')}

            # Get text content
            response = requests.put(
                f"{self.server_url}/tika",
                files=files,
                headers={'Accept': 'text/plain'}
            )

            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Tika parsing failed: {response.status_code}',
                    'content': '',
                    'metadata': {}
                }

            content = response.text

            # Get metadata
            response = requests.put(
                f"{self.server_url}/meta",
                files=files,
                headers={'Accept': 'application/json'}
            )

            metadata = {}
            if response.status_code == 200:
                metadata = response.json()

            result = {
                'success': True,
                'content': content,
                'metadata': metadata,
                'filename': filename,
                'file_size': len(file_data),
                'word_count': len(content.split()),
                'processing_method': 'apache_tika'
            }

            logger.info(f"Tika parsing successful for {filename}: {len(content)} characters")
            return result

        except Exception as e:
            logger.error(f"Tika parsing failed for {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'metadata': {},
                'filename': filename
            }

    def get_supported_formats(self) -> list:
        """
        Get list of supported document formats

        Returns:
            List of supported file extensions
        """
        return [
            '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
            '.txt', '.rtf', '.odt', '.ods', '.odp', '.html', '.xml',
            '.csv', '.json', '.zip', '.tar', '.gz'
        ]

    def is_format_supported(self, filename: str) -> bool:
        """
        Check if file format is supported for Tika parsing

        Args:
            filename: Filename to check

        Returns:
            True if format is supported
        """
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.get_supported_formats()