#!/usr/bin/env python3
"""
Stage 1: RAG Query Execution

This script runs test queries through the RAG system and saves the results
(questions, answers, retrieved contexts) to a JSON file for later evaluation.

Usage:
    python run_ragas_stage1_query.py --input ../../data/test_queries/baseline_20.json --output ../../data/results/baseline_20_queries.json
"""

import json
import time
from pathlib import Path
import sys
import requests
from typing import List, Dict, Any

def load_test_queries(file_path: str) -> List[Dict[str, Any]]:
    """Load test queries from JSON file."""
    with open(file_path, 'r') as f:
        queries = json.load(f)
    print(f"✓ Loaded {len(queries)} test queries")
    return queries

def run_rag_query(query: str, api_url: str = "http://localhost:8000/api/v1/query", top_k: int = 5) -> Dict[str, Any]:
    """Run a query through the RAG system."""
    try:
        response = requests.post(
            api_url,
            json={"query": query, "top_k": top_k},
            timeout=180
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error querying RAG system: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Stage 1: Run RAG queries and save results')
    parser.add_argument('--input', type=str, required=True, help='Path to test queries JSON file')
    parser.add_argument('--output', type=str, required=True, help='Path to save query results JSON file')
    parser.add_argument('--api-url', type=str, default='http://localhost:8000/api/v1/query', help='RAG API endpoint URL')
    parser.add_argument('--top-k', type=int, default=5, help='Number of context chunks to retrieve')
    args = parser.parse_args()
    
    # Load queries
    queries = load_test_queries(args.input)
    
    # Run queries
    print(f"\n{'='*60}")
    print("Stage 1: Running RAG Queries")
    print(f"{'='*60}\n")
    
    results = []
    success_count = 0
    fail_count = 0
    
    for idx, query_item in enumerate(queries, 1):
        query = query_item['query']
        difficulty = query_item.get('difficulty', 'unknown')
        
        print(f"[{idx}/{len(queries)}] Query: {query}")
        print(f"  Difficulty: {difficulty}")
        
        start_time = time.time()
        
        try:
            # Run RAG query
            rag_response = run_rag_query(query, args.api_url, args.top_k)
            elapsed = time.time() - start_time
            
            # Extract information
            answer = rag_response.get('answer', '')
            sources = rag_response.get('sources', [])
            confidence = rag_response.get('confidence', 0.0)
            
            # Format contexts for RAGAS
            contexts = [source.get('content', '') for source in sources]
            
            # Store result
            result = {
                "query": query,
                "difficulty": difficulty,
                "answer": answer,
                "contexts": contexts,
                "confidence": confidence,
                "num_sources": len(sources),
                "response_time": round(elapsed, 2)
            }
            results.append(result)
            success_count += 1
            
            print(f"  ✓ Answer: {answer[:80]}...")
            print(f"  ✓ Confidence: {confidence:.3f}")
            print(f"  ✓ Sources: {len(sources)} chunks")
            print(f"  ✓ Time: {elapsed:.1f}s\n")
            
        except Exception as e:
            fail_count += 1
            print(f"  ✗ Error: {e}")
            print(f"  ✗ Failed (skipping)\n")
            continue
    
    # Summary
    print(f"{'='*60}")
    print(f"Completed {success_count}/{len(queries)} queries")
    if fail_count > 0:
        print(f"Failed: {fail_count} queries")
    print(f"{'='*60}\n")
    
    if success_count == 0:
        print("✗ No successful queries to save")
        sys.exit(1)
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_queries": len(queries),
        "successful_queries": success_count,
        "failed_queries": fail_count,
        "results": results
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✓ Query results saved to {output_path}")
    print(f"\nNext step: Run Stage 2 evaluation")
    print(f"  python run_ragas_stage2_eval.py --input {output_path} --output {output_path.with_name(output_path.stem + '_evaluated.json')}")

if __name__ == "__main__":
    main()
