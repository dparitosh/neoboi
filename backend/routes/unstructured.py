"""
API Routes for Unstructured Data Pipeline
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import os
import logging
from datetime import datetime
import json

from ..unstructured_pipeline.document_ingestion import DocumentIngestionService
from ..unstructured_pipeline.data_processing import DataProcessingPipeline
from ..unstructured_pipeline.llm_service import OfflineLLMService
from ..unstructured_pipeline.tika_service import TikaService
from ..neo4j_service import get_neo4j_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/unstructured", tags=["unstructured-data"])

# Initialize services
ingestion_service = DocumentIngestionService()
processing_pipeline = DataProcessingPipeline()
llm_service = OfflineLLMService()
tika_service = TikaService()
neo4j_service = get_neo4j_service()

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    process_immediately: bool = True
) -> Dict[str, Any]:
    """
    Upload and process a document

    Args:
        file: Document file to upload
        process_immediately: Whether to process immediately or queue for background processing

    Returns:
        Upload confirmation and processing status
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Read file content
        file_content = await file.read()

        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")

        # Check file size (limit to 50MB)
        max_size = 50 * 1024 * 1024
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{file.filename}"

        logger.info(f"Processing upload: {unique_filename} ({len(file_content)} bytes)")

        if process_immediately:
            # Process immediately with Neo4j context and chunking
            result = ingestion_service.process_document_with_chunking(file_content, unique_filename)

            if result['success']:
                # Get document content for Neo4j processing
                document_content = result.get('content', '')
                document_metadata = {
                    'filename': unique_filename,
                    'original_filename': file.filename,
                    'file_size': len(file_content),
                    'upload_timestamp': datetime.now().isoformat(),
                    'chunks_count': len(result.get('chunks', [])),
                    'has_embeddings': len(result.get('chunk_embeddings', [])) > 0
                }

                # Process with Neo4j context enrichment
                neo4j_result = await neo4j_service.process_document_with_context(
                    document_content, document_metadata
                )

                # Also run data processing pipeline
                if document_content:
                    processed_data = processing_pipeline.process_text(
                        document_content,
                        {'filename': unique_filename, 'original_filename': file.filename}
                    )
                    result['structured_data'] = processed_data

                # Combine results
                result['neo4j_context'] = neo4j_result

                return {
                    'success': True,
                    'message': 'Document processed successfully with chunking and Neo4j context',
                    'filename': unique_filename,
                    'chunks_count': len(result.get('chunks', [])),
                    'embeddings_count': len(result.get('chunk_embeddings', [])),
                    'result': result
                }
            else:
                raise HTTPException(status_code=500, detail=f"Processing failed: {result.get('error', 'Unknown error')}")
        else:
            # Queue for background processing
            background_tasks.add_task(process_document_background, file_content, unique_filename, file.filename)

            return {
                'success': True,
                'message': 'Document queued for processing',
                'filename': unique_filename,
                'status': 'queued'
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_document_background(file_content: bytes, unique_filename: str, original_filename: str):
    """Background task to process document with Neo4j context"""
    try:
        logger.info(f"Starting background processing for {unique_filename}")

        # Process document
        result = ingestion_service.process_document_bytes(file_content, unique_filename)

        if result['success'] and 'content' in result and result['content']:
            # Get document content for Neo4j processing
            document_content = result['content']
            document_metadata = {
                'filename': unique_filename,
                'original_filename': original_filename,
                'file_size': len(file_content),
                'processing_timestamp': datetime.now().isoformat()
            }

            # Process with Neo4j context enrichment
            neo4j_result = await neo4j_service.process_document_with_context(
                document_content, document_metadata
            )

            # Run data processing pipeline
            processed_data = processing_pipeline.process_text(
                document_content,
                {'filename': unique_filename, 'original_filename': original_filename}
            )
            result['structured_data'] = processed_data
            result['neo4j_context'] = neo4j_result

            # Save final result
            ingestion_service._save_processing_result(result)

        logger.info(f"Background processing completed for {unique_filename}")

    except Exception as e:
        logger.error(f"Background processing failed for {unique_filename}: {str(e)}")

@router.get("/documents")
async def list_documents() -> Dict[str, Any]:
    """List all processed documents"""
    try:
        documents = ingestion_service.list_processed_documents()

        return {
            'success': True,
            'count': len(documents),
            'documents': documents
        }

    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/documents/{filename}")
async def get_document(filename: str) -> Dict[str, Any]:
    """Get specific document by filename"""
    try:
        document = ingestion_service.get_document_by_filename(filename)

        if document:
            return {
                'success': True,
                'document': document
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@router.post("/analyze/{filename}")
async def analyze_document(filename: str) -> Dict[str, Any]:
    """Analyze document using LLM with Neo4j context"""
    try:
        # Get document
        document = ingestion_service.get_document_by_filename(filename)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if not document.get('success') or 'content' not in document:
            raise HTTPException(status_code=400, detail="Document has no content to analyze")

        # Get Neo4j context for the document
        document_metadata = {
            'filename': filename,
            'original_filename': document.get('original_filename', filename),
            'processing_type': document.get('processing_type', 'general')
        }

        neo4j_context = await neo4j_service.process_document_with_context(
            document['content'], document_metadata
        )

        # Analyze with LLM using Neo4j context
        analysis_prompt = f"""
        Document: {document['content']}

        Neo4j Context: {json.dumps(neo4j_context.get('graph_context', {}), indent=2)}

        Please provide a comprehensive analysis including:
        1. Document summary
        2. Key entities and relationships
        3. Connections to existing knowledge graph
        4. Insights and patterns
        """

        analysis = llm_service.analyze_document(analysis_prompt, "document_with_context")

        return {
            'success': True,
            'filename': filename,
            'analysis': analysis,
            'neo4j_context': neo4j_context,
            'insights': neo4j_context.get('document_analysis', {}).get('insights', [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document analysis failed for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/search")
async def search_documents(query: str, use_llm: bool = True, search_type: str = "all") -> Dict[str, Any]:
    """
    Search documents using integrated Neo4j + Solr search

    Args:
        query: Natural language search query
        use_llm: Whether to use LLM for query understanding
        search_type: Type of search ("structured", "unstructured", "all")

    Returns:
        Integrated search results
    """
    try:
        # Use Neo4j integrated search
        integrated_results = await neo4j_service.integrated_search(query, search_type)

        # Enhance with LLM if requested
        if use_llm and integrated_results.get("solr_results"):
            # Get LLM analysis of search results
            search_context = f"Search query: {query}\n\nResults found: {len(integrated_results.get('solr_results', []))} documents"
            llm_analysis = llm_service.analyze_document(search_context, "search_results")

            integrated_results["llm_search_analysis"] = llm_analysis

        return {
            'success': True,
            'query': query,
            'search_type': search_type,
            'results': integrated_results
        }

    except Exception as e:
        logger.error(f"Integrated search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/qa")
async def question_answer(question: str, context_filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Answer questions about documents

    Args:
        question: Question to answer
        context_filename: Specific document filename (optional)

    Returns:
        Answer with supporting information
    """
    try:
        if context_filename:
            # Answer about specific document
            document = ingestion_service.get_document_by_filename(context_filename)

            if not document or 'content' not in document:
                raise HTTPException(status_code=404, detail="Document not found or has no content")

            context = document['content']
        else:
            # Answer about all documents (combine content)
            documents = ingestion_service.list_processed_documents()
            context_parts = []

            for doc in documents:
                if doc.get('success') and 'content' in doc:
                    context_parts.append(f"Document: {doc.get('filename', 'Unknown')}\n{doc['content'][:1000]}")

            context = "\n\n".join(context_parts)

            if not context:
                raise HTTPException(status_code=400, detail="No documents available for Q&A")

        # Get answer from LLM
        answer = llm_service.answer_question(question, context)

        return {
            'success': True,
            'question': question,
            'answer': answer,
            'context_filename': context_filename
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Q&A failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Q&A failed: {str(e)}")

@router.get("/graph")
async def get_graph_data() -> Dict[str, Any]:
    """Get Neo4j graph data for visualization"""
    try:
        graph_data = await neo4j_service.get_graph_data()

        return {
            'success': True,
            'graph': graph_data,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get graph data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get graph data: {str(e)}")

@router.post("/graph/search")
async def search_graph(query: str, limit: int = 50) -> Dict[str, Any]:
    """Search Neo4j graph data"""
    try:
        # Use integrated search but focus on graph data
        search_results = await neo4j_service.integrated_search(query, "structured", limit)

        return {
            'success': True,
            'query': query,
            'graph_results': search_results.get('neo4j_results', []),
            'total_found': len(search_results.get('neo4j_results', []))
        }

    except Exception as e:
        logger.error(f"Graph search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Graph search failed: {str(e)}")

@router.get("/status")
async def get_service_status() -> Dict[str, Any]:
    """Get status of all unstructured data services"""
    try:
        services_status = {
            'tika_server': tika_service._is_server_running(),
            'llm_service': llm_service.is_service_available(),
            'available_models': llm_service.list_available_models() if llm_service.is_service_available() else [],
            'supported_formats': ingestion_service.get_supported_formats(),
            'processed_documents_count': len(ingestion_service.list_processed_documents()),
            'neo4j_connection': neo4j_service._is_connected() if hasattr(neo4j_service, '_is_connected') else True
        }

        return {
            'success': True,
            'services': services_status,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.delete("/documents/{filename}")
async def delete_document(filename: str) -> Dict[str, Any]:
    """Delete a processed document"""
    try:
        # Find and delete the document file
        documents = ingestion_service.list_processed_documents()

        for doc in documents:
            if doc.get('filename') == filename:
                result_file = doc.get('result_file')
                if result_file and os.path.exists(result_file):
                    os.remove(result_file)

                return {
                    'success': True,
                    'message': f'Document {filename} deleted successfully'
                }

        raise HTTPException(status_code=404, detail="Document not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.post("/batch-process")
async def batch_process_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
) -> Dict[str, Any]:
    """
    Upload and process multiple documents

    Args:
        files: List of document files to process

    Returns:
        Batch processing status
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")

        if len(files) > 10:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 10 files per batch")

        processed_files = []

        for file in files:
            file_content = await file.read()

            if len(file_content) == 0:
                continue

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{file.filename}"

            # Queue for background processing
            background_tasks.add_task(
                process_document_background,
                file_content,
                unique_filename,
                file.filename
            )

            processed_files.append(unique_filename)

        return {
            'success': True,
            'message': f'Queued {len(processed_files)} documents for processing',
            'files': processed_files
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")