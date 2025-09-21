#!/usr/bin/env python3
"""
Solr Search and Query REST API - Python FastAPI Implementation
===============================================================

This module provides comprehensive Solr search and query functionality
implemented entirely in Python using FastAPI framework.

Features:
- Full-text search over Neo4j graph data
- Advanced filtering and faceting
- Pagination support
- Index management (create, clear, statistics)
- RESTful API endpoints
- Environment-based configuration
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Import the comprehensive Solr service
from solr_service import solr_service

# Create router for Solr endpoints
solr_router = APIRouter(prefix="/solr", tags=["solr"])

@solr_router.post("/index")
async def index_graph_data():
    """
    Index current Neo4j graph data into Solr for search.

    This endpoint:
    1. Fetches current graph data from Neo4j
    2. Indexes all nodes and relationships into Solr
    3. Returns indexing statistics

    Returns:
        Dict containing indexing results and statistics
    """
    try:
        logger.info("Starting Solr indexing process")

        # Import here to avoid circular imports
        from neo4j_service import get_neo4j_service
        neo4j_service = get_neo4j_service()

        # Get current graph data from Neo4j
        graph_data = await neo4j_service.get_graph_data()

        # Index the data into Solr
        result = await solr_service.index_graph_data(graph_data)

        return {
            "message": "Successfully indexed graph data into Solr",
            "result": result,
            "status": "completed"
        }

    except Exception as error:
        logger.error(f"Error indexing to Solr: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to index data to Solr",
                "details": str(error)
            }
        )

@solr_router.get("/search")
async def search_solr(
    q: str = Query(..., description="Search query string"),
    type: Optional[str] = Query(None, description="Filter by type (node/relationship)"),
    group: Optional[str] = Query(None, description="Filter by node group"),
    limit: int = Query(20, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination")
):
    """
    Search indexed data in Solr with advanced filtering.

    Query Parameters:
    - q: Search query (required)
    - type: Filter by document type (node/relationship)
    - group: Filter by node group
    - limit: Maximum results to return
    - offset: Pagination offset

    Returns:
        Dict containing search results and metadata
    """
    try:
        logger.info(f"Solr search query: {q}, filters: type={type}, group={group}")

        # Build filters dictionary
        filters = {}
        if type:
            filters["type"] = type
        if group:
            filters["group"] = group

        # Perform search using the Python Solr service
        result = await solr_service.search(q, filters, limit, offset)

        return {
            "query": q,
            "filters": filters,
            "total": result.get("total", 0),
            "results": result.get("docs", []),
            "limit": limit,
            "offset": offset,
            "search_engine": "solr",
            "implementation": "python-fastapi"
        }

    except Exception as error:
        logger.error(f"Error searching Solr: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to search Solr",
                "details": str(error)
            }
        )

@solr_router.post("/clear")
async def clear_solr_index():
    """
    Clear all documents from the Solr search index.

    This endpoint removes all indexed data from Solr,
    effectively resetting the search index.

    Returns:
        Dict confirming the operation status
    """
    try:
        logger.info("Clearing Solr index")

        success = await solr_service.clear_index()

        if success:
            return {
                "message": "Successfully cleared Solr index",
                "status": "completed",
                "implementation": "python-fastapi"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear Solr index")

    except Exception as error:
        logger.error(f"Error clearing Solr index: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to clear Solr index",
                "details": str(error)
            }
        )

@solr_router.get("/stats")
async def get_solr_statistics():
    """
    Get comprehensive statistics about the Solr index and collection.

    Returns information about:
    - Collection status and configuration
    - Index statistics
    - Shard and replica information

    Returns:
        Dict containing Solr statistics and metadata
    """
    try:
        stats = await solr_service.get_index_stats()
        return {
            "solr_stats": stats,
            "collection": solr_service.collection,
            "solr_url": solr_service.solr_url,
            "implementation": "python-fastapi",
            "service": "solr-search-api"
        }

    except Exception as error:
        logger.error(f"Error getting Solr stats: {error}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get Solr statistics",
                "details": str(error)
            }
        )

@solr_router.get("/health")
async def check_solr_health():
    """
    Check the health status of the Solr service.

    Tests connectivity to Solr and verifies the collection exists.

    Returns:
        Dict containing health status information
    """
    try:
        # Get basic stats to test connectivity
        stats = await solr_service.get_index_stats()

        return {
            "status": "healthy" if stats.get("status") != "error" else "unhealthy",
            "service": "solr-search-api",
            "implementation": "python-fastapi",
            "collection": solr_service.collection,
            "solr_url": solr_service.solr_url,
            "details": stats
        }

    except Exception as error:
        logger.error(f"Solr health check failed: {error}")
        return {
            "status": "unhealthy",
            "service": "solr-search-api",
            "implementation": "python-fastapi",
            "error": str(error)
        }

# Export the router for inclusion in main FastAPI app
__all__ = ["solr_router"]