#!/usr/bin/env python3
"""
RAGAS Evaluation - Stage 1B: Generate Reference Answers

This script generates reference (ground truth) answers for evaluation queries
using an LLM. These references are needed for metrics like ContextPrecision,
ContextRecall, and ContextEntityRecall.

Usage:
    python run_ragas_stage1b_generate_references.py \
        --input ../../data/results/baseline_20_stage1.json \
        --output ../../data/results/baseline_20_stage1_with_references.json

Requirements:
    - OpenAI API key set in environment
    - Stage 1 results file (from run_ragas_stage1_query.py)
"""

import json
import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def generate_reference_answer(query: str, contexts: List[str], llm: ChatOpenAI) -> str:
    """
    Generate a reference (ground truth) answer for a query based on retrieved contexts.
    
    Args:
        query: The question to answer
        contexts: List of relevant context chunks
        llm: LangChain LLM instance
        
    Returns:
        Generated reference answer
    """
    # Create a prompt for generating comprehensive reference answers
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert technical writer creating reference answers for RAG evaluation.
Your task is to write a comprehensive, accurate answer based ONLY on the provided context.

Guidelines:
- Use ONLY information from the provided context
- Be comprehensive but concise
- Include specific details, code examples if present
- Maintain technical accuracy
- Structure the answer clearly
- Do not add information not in the context"""),
        ("user", """Context chunks:
{contexts}

Question: {query}

Generate a comprehensive reference answer based on the context above:""")
    ])
    
    # Format contexts
    contexts_text = "\n\n".join([f"[Context {i+1}]\n{ctx}" for i, ctx in enumerate(contexts)])
    
    # Generate answer
    messages = prompt.format_messages(contexts=contexts_text, query=query)
    response = llm.invoke(messages)
    
    return response.content.strip()


def add_references_to_results(
    input_file: str,
    output_file: str,
    model: str = "gpt-3.5-turbo",
    skip_existing: bool = True
) -> None:
    """
    Add reference answers to Stage 1 results.
    
    Args:
        input_file: Path to Stage 1 results JSON
        output_file: Path to save results with references
        model: OpenAI model to use for generation
        skip_existing: Skip queries that already have references
    """
    # Check API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("✗ Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Load Stage 1 results
    print(f"Loading Stage 1 results from: {input_file}")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Handle both formats:
    # 1. Stage 1 results: {"results": [...], "timestamp": ...} or {"queries": [...], "summary": {...}}
    # 2. Baseline queries: [{"id": 1, "query": "...", ...}, ...]
    if isinstance(data, dict):
        queries = data.get('results', data.get('queries', []))
    else:
        # It's a list of baseline queries - convert to expected format
        queries = [{"query": q["query"]} for q in data]
    
    print(f"✓ Loaded {len(queries)} queries\n")
    
    # Initialize LLM
    print(f"Initializing LLM: {model}")
    llm = ChatOpenAI(model=model, temperature=0)
    print("✓ LLM ready\n")
    
    # Generate references
    print("=" * 60)
    print("Generating Reference Answers")
    print("=" * 60 + "\n")
    
    generated = 0
    skipped = 0
    failed = 0
    
    for i, query_result in enumerate(queries, 1):
        query = query_result.get('query', '')
        print(f"[{i}/{len(queries)}] Query: {query[:60]}...")
        
        # Skip if already has reference and skip_existing is True
        if skip_existing and query_result.get('reference'):
            print(f"  ⊙ Already has reference (skipping)\n")
            skipped += 1
            continue
        
        # Skip failed queries (check if has answer or if explicitly marked as failed)
        has_answer = query_result.get('answer') or query_result.get('response')
        explicitly_failed = query_result.get('error') or query_result.get('success') == False
        
        if explicitly_failed or not has_answer:
            print(f"  ⊙ Query failed in Stage 1 (skipping)\n")
            skipped += 1
            continue
        
        # Get contexts (try both field names)
        contexts = query_result.get('contexts', query_result.get('retrieved_contexts', []))
        if not contexts:
            print(f"  ⊙ No contexts available (skipping)\n")
            skipped += 1
            continue
        
        try:
            # Generate reference
            reference = generate_reference_answer(query, contexts, llm)
            query_result['reference'] = reference
            
            print(f"  ✓ Generated reference ({len(reference)} chars)")
            print(f"    Preview: {reference[:80]}...\n")
            generated += 1
            
        except Exception as e:
            print(f"  ✗ Error generating reference: {e}\n")
            failed += 1
    
    # Summary
    print("=" * 60)
    print(f"Generated: {generated}")
    print(f"Skipped:   {skipped}")
    print(f"Failed:    {failed}")
    print("=" * 60 + "\n")
    
    # Save results - keep original format if it was a dict, else create new structure
    if isinstance(data, dict):
        output_data = data
    else:
        # Convert back to list format with references added
        output_data = queries
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✓ Results with references saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate reference answers for RAGAS evaluation'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to Stage 1 results JSON file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path to save results with references'
    )
    parser.add_argument(
        '--model',
        default='gpt-3.5-turbo',
        help='OpenAI model to use (default: gpt-3.5-turbo)'
    )
    parser.add_argument(
        '--regenerate',
        action='store_true',
        help='Regenerate references even if they exist'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("RAGAS Evaluation - Stage 1B: Generate References")
    print("=" * 60 + "\n")
    
    add_references_to_results(
        input_file=args.input,
        output_file=args.output,
        model=args.model,
        skip_existing=not args.regenerate
    )
    
    print("\n✓ Stage 1B complete!")
    print("\nNext step:")
    print(f"  python run_ragas_stage2_eval.py \\")
    print(f"    --input {args.output} \\")
    print(f"    --output <evaluation_results.json>\n")


if __name__ == "__main__":
    main()
