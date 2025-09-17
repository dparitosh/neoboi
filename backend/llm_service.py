import logging
import re
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

def generate_mock_cypher(query: str) -> str:
    """Generate basic Cypher queries from natural language using pattern matching"""
    query_lower = query.lower().strip()

    # Simple pattern matching for common queries
    if re.search(r'\b(all|show|list|get)\b.*\b(person|people|user|node)\b', query_lower):
        return "MATCH (p:Person) RETURN p"

    elif re.search(r'\b(find|show|get)\b.*\b(friend|friends)\b.*\b(of|for)\b', query_lower):
        # Extract name if present
        name_match = re.search(r'\b(of|for)\s+(\w+)', query_lower)
        if name_match:
            name = name_match.group(2).capitalize()
            return f"MATCH (p:Person {{name: '{name}'}})-[:FRIENDS_WITH]->(friend) RETURN friend"
        return "MATCH (p:Person)-[:FRIENDS_WITH]->(friend) RETURN friend"

    elif re.search(r'\b(movie|movies|film|films)\b.*\b(star|acted|actor|actress)\b', query_lower):
        # Extract name if present
        name_match = re.search(r'\b(by|with|star|acted)\s+(\w+\s*\w*)', query_lower)
        if name_match:
            name = name_match.group(2).strip().title()
            return f"MATCH (p:Person {{name: '{name}'}})-[:ACTED_IN]->(m:Movie) RETURN m.title"
        return "MATCH (p:Person)-[:ACTED_IN]->(m:Movie) RETURN m.title"

    elif re.search(r'\b(relationship|relation|connect|link)\b', query_lower):
        return "MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 10"

    elif re.search(r'\b(count|number|how many)\b', query_lower):
        if 'person' in query_lower or 'people' in query_lower:
            return "MATCH (p:Person) RETURN count(p) as person_count"
        elif 'movie' in query_lower or 'film' in query_lower:
            return "MATCH (m:Movie) RETURN count(m) as movie_count"
        else:
            return "MATCH (n) RETURN count(n) as node_count"

    else:
        # Default fallback
        return "MATCH (n) RETURN n LIMIT 10"

def process_query(user_query: str) -> dict:
    """Process a user query and return the result"""
    try:
        logger.info(f"Processing query: {user_query}")

        # Generate Cypher query
        cypher_query = generate_mock_cypher(user_query)
        explanation = f"Generated Cypher query for: '{user_query}' (Mock Mode)"
        confidence = 0.7

        return {
            "cypher": cypher_query,
            "explanation": explanation,
            "confidence": confidence,
            "source": "python-llm"
        }

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {
            "cypher": "MATCH (n) RETURN n LIMIT 10",
            "explanation": f"Error processing query: {str(e)}",
            "confidence": 0.0,
            "source": "error"
        }