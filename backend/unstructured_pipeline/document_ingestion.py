"""
Document Ingestion Service for processing unstructured data
Combines OCR, Tika, and LLM processing for comprehensive document understanding
"""
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime

from .ocr_service import OCRService
from .tika_service import TikaService

logger = logging.getLogger(__name__)

class DocumentIngestionService:
    """Main service for ingesting and processing unstructured documents"""

    def __init__(self, upload_dir: str = "uploads", processed_dir: str = "processed"):
        """
        Initialize document ingestion service

        Args:
            upload_dir: Directory for uploaded files
            processed_dir: Directory for processed files
        """
        self.upload_dir = Path(upload_dir)
        self.processed_dir = Path(processed_dir)

        # Create directories if they don't exist
        self.upload_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)

        # Initialize services with error handling
        try:
            self.ocr_service = OCRService()
            self.ocr_available = False  # OCR disabled due to dependencies
        except Exception as e:
            logger.warning(f"OCR service initialization failed: {str(e)}")
            self.ocr_service = None
            self.ocr_available = False

        try:
            self.tika_service = TikaService()
            # Try to start Tika server automatically
            tika_jar_path = os.path.join(os.path.dirname(__file__), '..', 'lib', 'tika-server.jar')
            if self.tika_service.start_tika_server(tika_jar_path):
                self.tika_available = True
                logger.info("Tika server started successfully")
            else:
                self.tika_available = False
                logger.warning("Failed to start Tika server during initialization - will retry during document processing")
        except Exception as e:
            logger.warning(f"Tika service initialization failed: {str(e)}")
            self.tika_service = None
            self.tika_available = False

        # Supported file types
        self.image_extensions = [] if not self.ocr_available else self.ocr_service.get_supported_formats()
        self.document_extensions = [] if not self.tika_available else self.tika_service.get_supported_formats()

        logger.info(f"Document Ingestion Service initialized - OCR: {self.ocr_available}, Tika: {self.tika_available}")

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document through the ingestion pipeline

        Args:
            file_path: Path to the document file

        Returns:
            Processing results with extracted content and metadata
        """
        try:
            filename = os.path.basename(file_path)
            file_ext = os.path.splitext(filename.lower())[1]

            logger.info(f"Processing document: {filename}")

            # Determine processing method based on file type
            if file_ext in self.image_extensions and self.ocr_available:
                # Use OCR for images
                result = self.ocr_service.extract_text_from_file(file_path)
                result['processing_type'] = 'ocr'
            elif file_ext in ['.txt', '.md'] or (file_ext in self.document_extensions and self.tika_available):
                # For text files, always use plain text processing to avoid Tika issues
                if file_ext in ['.txt', '.md']:
                    result = self._process_as_plain_text(file_path)
                    result['processing_type'] = 'plain_text'
                else:
                    # Use Tika for other document types
                    result = self.tika_service.parse_document(file_path)
                    result['processing_type'] = 'tika'
                    # If Tika returns empty content, fall back to plain text
                    if not result.get('content', '').strip():
                        logger.warning("Tika returned empty content, falling back to plain text processing")
                        result = self._process_as_plain_text(file_path)
                        result['processing_type'] = 'plain_text_fallback'
            else:
                # Fallback: try to read as plain text
                result = self._process_as_plain_text(file_path)
                result['processing_type'] = 'plain_text'

            # Add common metadata
            result.update({
                'processed_at': datetime.now().isoformat(),
                'file_path': str(file_path),
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            })

            # Save processing results
            self._save_processing_result(result)

            logger.info(f"Document processing completed: {filename}")
            return result

        except Exception as e:
            logger.error(f"Document processing failed for {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'filename': os.path.basename(file_path),
                'processing_type': 'error'
            }

    def _process_as_plain_text(self, file_path: str) -> Dict[str, Any]:
        """
        Process file as plain text fallback

        Args:
            file_path: Path to the file

        Returns:
            Processing result
        """
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename.lower())[1]

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            result = {
                'success': True,
                'content': content,
                'metadata': {},
                'filename': filename,
                'file_size': os.path.getsize(file_path),
                'word_count': len(content.split()),
                'processing_method': 'plain_text'
            }
            logger.info(f"Processed as plain text: {filename}")
            return result
        except UnicodeDecodeError:
            # Binary file that can't be processed
            result = {
                'success': False,
                'error': f'Unsupported file type: {file_ext}. No suitable processing service available.',
                'filename': filename,
                'processing_type': 'unsupported'
            }
            return result
        except Exception as e:
            result = {
                'success': False,
                'error': f'Failed to process file: {str(e)}',
                'filename': filename,
                'processing_type': 'error'
            }
            return result

    def process_document_bytes(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Process document from bytes

        Args:
            file_data: Raw file bytes
            filename: Original filename

        Returns:
            Processing results
        """
        try:
            file_ext = os.path.splitext(filename.lower())[1]

            logger.info(f"Processing document from bytes: {filename} (size: {len(file_data)} bytes)")

            # DEBUG: Log first 200 bytes to see what we're getting
            logger.info(f"File data preview: {file_data[:200]}")

            # Save file temporarily for processing
            temp_path = self.upload_dir / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            logger.info(f"Saving to temp path: {temp_path}")
            with open(temp_path, 'wb') as f:
                f.write(file_data)

            # DEBUG: Verify temp file was written correctly
            if temp_path.exists():
                with open(temp_path, 'rb') as f:
                    saved_data = f.read()
                logger.info(f"Temp file saved, size: {len(saved_data)} bytes")
                logger.info(f"Temp file content preview: {saved_data[:200]}")

            try:
                # Process the temporary file
                result = self.process_document(str(temp_path))

                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()

                return result

            except Exception as e:
                # Clean up temp file on error
                if temp_path.exists():
                    temp_path.unlink()
                raise e

        except Exception as e:
            logger.error(f"Document processing failed for {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename,
                'processing_type': 'error'
            }

    def process_document_with_chunking(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Process document with chunking and embeddings

        Args:
            file_data: Raw file bytes
            filename: Original filename

        Returns:
            Processing results with chunks and embeddings
        """
        try:
            # First get basic processing result
            result = self.process_document_bytes(file_data, filename)

            if not result.get('success', False) or 'content' not in result:
                return result

            # Import data processing pipeline here to avoid circular imports
            from .data_processing import DataProcessingPipeline

            # Initialize pipeline and process content
            pipeline = DataProcessingPipeline()
            processed_data = pipeline.process_text(
                result['content'],
                {'filename': filename, 'original_filename': filename}
            )

            # Add chunking and embedding results to the main result
            result.update({
                'chunks': processed_data.get('chunks', []),
                'chunk_embeddings': processed_data.get('chunk_embeddings', []),
                'structured_data': processed_data,
                'vector_processing': True
            })

            # Save enhanced result
            self._save_processing_result(result)

            # Store chunks with embeddings in Neo4j for vector search
            if processed_data.get('chunks'):
                try:
                    import asyncio
                    from neo4j_service import get_neo4j_service
                    neo4j_service = get_neo4j_service()

                    # Create vector index if it doesn't exist
                    asyncio.run(neo4j_service.create_vector_index())

                    # Store chunks with embeddings
                    document_metadata = {'filename': filename}
                    storage_result = asyncio.run(
                        neo4j_service.store_document_chunks_with_embeddings(
                            processed_data['chunks'], document_metadata
                        )
                    )

                    result['neo4j_storage'] = storage_result
                    logger.info(f"Stored {storage_result.get('chunks_stored', 0)} chunks in Neo4j vector store")

                except Exception as e:
                    logger.warning(f"Failed to store chunks in Neo4j: {str(e)}")
                    result['neo4j_storage_error'] = str(e)

            logger.info(f"Document processing with chunking completed: {filename} ({len(processed_data.get('chunks', []))} chunks)")
            return result

        except Exception as e:
            logger.error(f"Document processing with chunking failed for {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename,
                'processing_type': 'error',
                'vector_processing': False
            }

    def _save_processing_result(self, result: Dict[str, Any]) -> None:
        """
        Save processing result to file

        Args:
            result: Processing result dictionary
        """
        try:
            filename = result.get('filename', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Create result filename
            result_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.json"
            result_path = self.processed_dir / result_filename

            # Save result as JSON
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"Processing result saved: {result_path}")

        except Exception as e:
            logger.error(f"Failed to save processing result: {str(e)}")

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get all supported file formats

        Returns:
            Dictionary of supported formats by processing type
        """
        formats = {}

        if self.ocr_available and self.ocr_service:
            formats['ocr'] = self.image_extensions
        else:
            formats['ocr'] = []

        if self.tika_available and self.tika_service:
            formats['tika'] = self.document_extensions
        else:
            formats['tika'] = []

        # Always support plain text files
        formats['plain_text'] = ['.txt', '.md', '.csv', '.json', '.xml']

        formats['all'] = list(set(
            formats.get('ocr', []) +
            formats.get('tika', []) +
            formats.get('plain_text', [])
        ))

        return formats

    def list_processed_documents(self) -> List[Dict[str, Any]]:
        """
        List all processed documents

        Returns:
            List of processed document metadata
        """
        processed_docs = []

        try:
            for json_file in self.processed_dir.glob('*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        doc_data = json.load(f)
                        doc_data['result_file'] = str(json_file)
                        processed_docs.append(doc_data)
                except Exception as e:
                    logger.error(f"Failed to read processed document {json_file}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to list processed documents: {str(e)}")

        return processed_docs

    def get_document_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get processed document by filename

        Args:
            filename: Original filename

        Returns:
            Document data if found, None otherwise
        """
        for doc in self.list_processed_documents():
            if doc.get('filename') == filename:
                return doc
        return None

    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Clean up old processed files

        Args:
            days: Number of days to keep files

        Returns:
            Number of files cleaned up
        """
        import time
        from datetime import datetime, timedelta

        cutoff_time = time.time() - (days * 24 * 60 * 60)
        cleaned_count = 0

        try:
            for file_path in self.processed_dir.glob('*'):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1

            logger.info(f"Cleaned up {cleaned_count} old files")
            return cleaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup old files: {str(e)}")
            return 0