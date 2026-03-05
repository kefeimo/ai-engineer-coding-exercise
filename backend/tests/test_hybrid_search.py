"""
Test hybrid search to verify IDataTableProps retrieval
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../app')

from app.rag.hybrid_retrieval import HybridRetriever
from app.rag.retrieval import Retriever

def test_idatatable_props_retrieval():
    """Test that IDataTableProps is retrieved correctly"""
    
    query = "What is IDataTableProps?"
    print(f"\n{'='*70}")
    print(f"Testing Query: '{query}'")
    print(f"{'='*70}\n")
    
    # Test 1: Semantic-only (baseline)
    print("1. SEMANTIC-ONLY SEARCH")
    print("-" * 70)
    semantic_retriever = Retriever()
    semantic_result = semantic_retriever.retrieve(query, top_k=5)
    
    if semantic_result['documents']:
        for i, doc in enumerate(semantic_result['documents'][:5], 1):
            api_name = doc['metadata'].get('api_name', 'N/A')
            doc_type = doc['metadata'].get('doc_type', 'N/A')
            confidence = doc.get('confidence', 0.0)
            content_preview = doc['content'][:80].replace('\n', ' ')
            print(f"  #{i}: api_name='{api_name}', doc_type='{doc_type}', conf={confidence:.3f}")
            print(f"      {content_preview}...")
    else:
        print("  No documents retrieved")
    
    print(f"\n  Average Confidence: {semantic_result.get('confidence', 0.0):.3f}\n")
    
    # Test 2: Hybrid search
    print("2. HYBRID SEARCH (semantic 0.4 + BM25 0.6)")
    print("-" * 70)
    hybrid_retriever = HybridRetriever(auto_classify=True)
    hybrid_result = hybrid_retriever.search(query, top_k=5)
    
    if hybrid_result['documents']:
        for i, doc in enumerate(hybrid_result['documents'][:5], 1):
            api_name = doc['metadata'].get('api_name', 'N/A')
            doc_type = doc['metadata'].get('doc_type', 'N/A')
            score = doc.get('score', 0.0)
            semantic_score = doc.get('semantic_score', 0.0)
            bm25_score = doc.get('bm25_score', 0.0)
            content_preview = doc['content'][:80].replace('\n', ' ')
            print(f"  #{i}: api_name='{api_name}', doc_type='{doc_type}'")
            print(f"      combined={score:.3f} (semantic={semantic_score:.3f}, bm25={bm25_score:.3f})")
            print(f"      {content_preview}...")
    else:
        print("  No documents retrieved")
    
    print(f"\n  Average Confidence: {hybrid_result.get('confidence', 0.0):.3f}\n")
    
    # Check if IDataTableProps is in results
    print("3. VERIFICATION")
    print("-" * 70)
    
    found_in_semantic = any(
        'idatatable' in doc['metadata'].get('api_name', '').lower() 
        for doc in semantic_result.get('documents', [])[:5]
    )
    found_in_hybrid = any(
        'idatatable' in doc['metadata'].get('api_name', '').lower() 
        for doc in hybrid_result.get('documents', [])[:5]
    )
    
    print(f"  IDataTableProps in top 5 (semantic-only): {' ✅' if found_in_semantic else '❌'}")
    print(f"  IDataTableProps in top 5 (hybrid): {' ✅' if found_in_hybrid else '❌'}")
    
    if found_in_hybrid:
        print("\n✅ SUCCESS: Hybrid search correctly retrieves IDataTableProps!")
    else:
        print("\n❌ FAILURE: IDataTableProps not found in top 5")
        print("\n   Need to investigate:")
        print("   - Check if 'IDataTableProps' text appears in document content")
        print("   - Verify BM25 tokenization is working")
        print("   - Consider adjusting weights or boosting")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    test_idatatable_props_retrieval()
