"""
Query Classification Module
Classify queries to optimize retrieval strategy
"""

from typing import Literal

QueryType = Literal['api', 'how_to', 'troubleshooting', 'general']


def classify_query(query: str) -> QueryType:
    """
    Classify query type for optimized retrieval
    
    - API: Looking for interface/function/class definitions
    - How-to: Looking for usage examples, guides
    - Troubleshooting: Looking for issue solutions
    - General: General questions about concepts
    
    Args:
        query: User query string
        
    Returns:
        QueryType: One of 'api', 'how_to', 'troubleshooting', 'general'
    """
    query_lower = query.lower()
    
    # API keywords
    api_keywords = [
        'interface', 'function', 'class', 'props', 'api', 'type',
        'what is', 'definition', 'idatatable', 'iaccessibility',
        'idata', 'i_', 'enum', 'const', 'export'
    ]
    
    # How-to keywords
    howto_keywords = [
        'how', 'create', 'use', 'implement', 'setup', 'configure',
        'example', 'tutorial', 'guide', 'get started', 'build',
        'integrate', 'add', 'customize'
    ]
    
    # Troubleshooting keywords
    trouble_keywords = [
        'error', 'issue', 'problem', 'fix', 'not working', 'broken',
        'bug', 'fail', 'crash', 'wrong', 'incorrect', 'missing'
    ]
    
    # Count matches
    api_score = sum(1 for kw in api_keywords if kw in query_lower)
    howto_score = sum(1 for kw in howto_keywords if kw in query_lower)
    trouble_score = sum(1 for kw in trouble_keywords if kw in query_lower)
    
    # Classify based on highest score
    if api_score > max(howto_score, trouble_score):
        return 'api'
    elif howto_score > trouble_score:
        return 'how_to'
    elif trouble_score > 0:
        return 'troubleshooting'
    else:
        return 'general'


def get_search_weights(query_type: QueryType) -> dict:
    """
    Get optimal search weights based on query type
    
    Args:
        query_type: Classified query type
        
    Returns:
        Dict with semantic_weight, bm25_weight, and boost_config
    """
    if query_type == 'api':
        # API queries: prioritize keyword matching for exact names
        return {
            'semantic_weight': 0.4,
            'bm25_weight': 0.6,
            'boost_config': {'doc_type': {'api': 1.5}}
        }
    elif query_type == 'how_to':
        # How-to queries: prioritize semantic understanding
        return {
            'semantic_weight': 0.7,
            'bm25_weight': 0.3,
            'boost_config': {'doc_type': {'readme': 1.3, 'documentation': 1.2}}
        }
    elif query_type == 'troubleshooting':
        # Troubleshooting: balance semantic and keyword
        return {
            'semantic_weight': 0.5,
            'bm25_weight': 0.5,
            'boost_config': {'doc_type': {'issue_qa': 1.5}}
        }
    else:  # general
        # General queries: default balanced approach
        return {
            'semantic_weight': 0.6,
            'bm25_weight': 0.4,
            'boost_config': {}
        }
