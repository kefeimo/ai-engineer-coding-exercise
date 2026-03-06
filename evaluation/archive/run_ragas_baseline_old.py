"""
RAGAS Evaluation Script for RAG System Baseline

This script runs the 20 baseline test queries through the RAG system
and evaluates the results using RAGAS metrics.

Metrics evaluated:
1. faithfulness: Is the answer grounded in the context?
2. answer_relevancy: Does the answer address the question?

Note: The following metrics require ground_truth reference answers (not evaluated):
- context_precision: How relevant are the retrieved contexts?
- context_recall: How much of the ground truth is captured?
- context_entity_recall: How many entities are recalled?

RAGAS LLM Configuration:
-----------------------
RAGAS requires an LLM to evaluate responses. Two options:

1. OpenAI API (Recommended - Fast & Accurate):
   export OPENAI_API_KEY="your-api-key-here"
   
   RAGAS will automatically use OpenAI's models (gpt-3.5-turbo by default).
   This is the fastest and most reliable option.
   
2. Local LLM via LangChain (Experimental - Slow):
   Can use GPT4All/Ollama through LangChain wrapper, but expect:
   - Much slower evaluation (10-30 seconds per query vs 1-2 seconds with OpenAI)
   - Potential async/threading issues
   - Lower quality metrics
   
   Not recommended for routine evaluation.

Usage:
    # With OpenAI (recommended):
    export OPENAI_API_KEY="sk-..."
    python run_ragas_baseline.py
    
    # Without API key (saves query results only, no RAGAS metrics):
    python run_ragas_baseline.py
"""

import json
import time
from pathlib import Path
import sys
import requests
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy
)
from datasets import Dataset


class RAGEvaluator:
    """Evaluates RAG system using RAGAS metrics."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize the evaluator.
        
        Args:
            api_base_url: Base URL of the RAG API
        """
        self.api_base_url = api_base_url
        self.query_endpoint = f"{api_base_url}/api/v1/query"
        
    def load_test_queries(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load test queries from JSON file.
        
        Args:
            file_path: Path to JSON file with test queries
            
        Returns:
            List of query dictionaries
        """
        with open(file_path, 'r') as f:
            queries = json.load(f)
        print(f"✓ Loaded {len(queries)} test queries")
        return queries
        
    def run_rag_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Run a query through the RAG system.
        
        Args:
            query: Question to ask
            top_k: Number of context chunks to retrieve
            
        Returns:
            RAG response with answer, sources, confidence
        """
        try:
            response = requests.post(
                self.query_endpoint,
                json={"query": query, "top_k": top_k},
                timeout=180  # 3 minutes for LLM generation
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"✗ Error querying RAG system: {e}")
            return None
            
    def prepare_ragas_dataset(
        self, 
        queries: List[Dict[str, Any]]
    ) -> Dataset:
        """
        Run all queries and prepare dataset for RAGAS evaluation.
        
        Args:
            queries: List of test query dictionaries
            
        Returns:
            RAGAS Dataset with questions, answers, contexts, ground_truths
        """
        data = {
            "question": [],
            "answer": [],
            "contexts": [],
            "ground_truths": []  # We'll use expected_aspects as ground truth
        }
        
        print(f"\n{'='*60}")
        print("Running queries through RAG system...")
        print(f"{'='*60}\n")
        
        for i, query_dict in enumerate(queries, 1):
            query = query_dict["query"]
            print(f"[{i}/{len(queries)}] Query: {query}")
            
            # Run RAG query
            start_time = time.time()
            result = self.run_rag_query(query)
            elapsed = time.time() - start_time
            
            if result is None:
                print(f"  ✗ Failed (skipping)\n")
                continue
                
            # Extract data for RAGAS
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            confidence = result.get("confidence", 0.0)
            
            # Contexts are the retrieved chunk contents
            contexts = [source.get("content", "") for source in sources]
            
            # Ground truth from expected aspects
            ground_truth = ", ".join(query_dict["expected_aspects"])
            
            print(f"  ✓ Answer: {answer[:80]}...")
            print(f"  ✓ Confidence: {confidence:.3f}")
            print(f"  ✓ Sources: {len(sources)} chunks")
            print(f"  ✓ Time: {elapsed:.1f}s\n")
            
            # Add to dataset
            data["question"].append(query)
            data["answer"].append(answer)
            data["contexts"].append(contexts)
            data["ground_truths"].append([ground_truth])  # RAGAS expects list
            
        print(f"{'='*60}")
        print(f"Completed {len(data['question'])}/{len(queries)} queries")
        print(f"{'='*60}\n")
        
        return Dataset.from_dict(data)
        
    def run_evaluation(self, dataset: Dataset) -> Dict[str, float]:
        """
        Run RAGAS evaluation on the dataset.
        
        Args:
            dataset: RAGAS Dataset with questions, answers, contexts
            
        Returns:
            Dictionary of metric scores
        """
        print(f"\n{'='*60}")
        print("Running RAGAS evaluation...")
        print(f"{'='*60}\n")
        
        # Configure LLM and embeddings explicitly for metrics
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        embeddings = OpenAIEmbeddings()
        
        # Run evaluation
        # NOTE: Only using metrics that don't require 'reference' (ground truth) answers
        # - Faithfulness: Checks if answer is grounded in retrieved context
        # - AnswerRelevancy: Checks if answer addresses the question
        # 
        # Metrics that require reference answers (skipped):
        # - ContextPrecision: Requires ground truth to assess context relevance
        # - ContextRecall: Requires ground truth to measure coverage
        # - ContextEntityRecall: Requires ground truth for entity comparison
        result = evaluate(
            dataset,
            metrics=[
                Faithfulness(llm=llm),
                AnswerRelevancy(llm=llm, embeddings=embeddings)
            ]
        )
        
        return result
        
    def save_results(
        self, 
        results, 
        output_path: str
    ) -> None:
        """
        Save evaluation results to JSON file.
        
        Args:
            results: RAGAS EvaluationResult object
            output_path: Path to save results JSON
        """
        # RAGAS 0.4.x returns EvaluationResult with .scores attribute
        # scores is a list of dicts, one per query
        # Calculate average scores across all queries
        scores_list = results.scores if hasattr(results, 'scores') else []
        
        # Aggregate scores
        metrics = {}
        if scores_list:
            # Get all metric names from first score
            metric_names = scores_list[0].keys()
            for metric_name in metric_names:
                values = [score[metric_name] for score in scores_list if metric_name in score]
                metrics[metric_name] = sum(values) / len(values) if values else 0.0
        
        # Convert to serializable format
        results_dict = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": metrics,
            "dataset_size": len(scores_list),
            "per_query_scores": scores_list  # Include individual scores too
        }
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(results_dict, f, indent=2)
            
        print(f"✓ Results saved to {output_path}")
    
    def save_query_results(
        self,
        queries: List[Dict[str, Any]],
        dataset: Dataset,
        output_path: str
    ) -> None:
        """
        Save query results without RAGAS metrics.
        
        Args:
            queries: Original query list
            dataset: Dataset with questions, answers, contexts
            output_path: Path to save results JSON
        """
        # Extract data from dataset
        query_results = []
        for i in range(len(dataset)):
            query_results.append({
                "id": queries[i]["id"],
                "query": dataset[i]["question"],
                "difficulty": queries[i]["difficulty"],
                "category": queries[i]["category"],
                "answer": dataset[i]["answer"][:200] + "..." if len(dataset[i]["answer"]) > 200 else dataset[i]["answer"],
                "contexts_count": len(dataset[i]["contexts"]),
                "expected_aspects": queries[i]["expected_aspects"]
            })
        
        results_dict = {
            "test_name": "RAG Query Evaluation (RAGAS metrics skipped)",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "queries_complete_ragas_skipped",
            "note": "RAGAS evaluation requires OpenAI API key",
            "test_results": {
                "total_queries": len(queries),
                "successful_queries": len(dataset),
                "failed_queries": len(queries) - len(dataset)
            },
            "query_results": query_results
        }
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(results_dict, f, indent=2)
            
        print(f"✓ Query results saved to {output_path}")
        
    def print_summary(self, results) -> None:
        """
        Print summary of evaluation results.
        
        Args:
            results: RAGAS EvaluationResult object
        """
        print(f"\n{'='*60}")
        print("RAGAS BASELINE EVALUATION RESULTS")
        print(f"{'='*60}\n")
        
        # Extract scores from EvaluationResult
        scores_list = results.scores if hasattr(results, 'scores') else []
        
        if not scores_list:
            print("No scores available")
            return
        
        # Calculate average scores
        metric_names = scores_list[0].keys()
        
        metric_labels = {
            "context_precision": "Context Precision",
            "faithfulness": "Faithfulness",
            "answer_relevancy": "Answer Relevancy",
            "context_recall": "Context Recall",
            "context_entity_recall": "Context Entity Recall"
        }
        
        for metric_name in metric_names:
            values = [score[metric_name] for score in scores_list if metric_name in score]
            avg_score = sum(values) / len(values) if values else 0.0
            label = metric_labels.get(metric_name, metric_name.replace('_', ' ').title())
            print(f"{label:25s}: {avg_score:.4f}")
            
        print(f"\n{'='*60}\n")


def main():
    """Main execution function."""
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Run RAGAS baseline evaluation')
    parser.add_argument('--input', type=str, help='Path to test queries JSON file')
    parser.add_argument('--output', type=str, help='Path to save results JSON file')
    args = parser.parse_args()
    
    # Paths - go up two levels from evaluation/ to reach project root
    project_root = Path(__file__).parent.parent.parent
    
    if args.input:
        queries_file = Path(args.input)
    else:
        queries_file = project_root / "data" / "test_queries" / "baseline_20.json"
    
    if args.output:
        results_file = Path(args.output)
    else:
        results_file = project_root / "data" / "results" / "baseline_ragas_results.json"
    
    # Create results directory if it doesn't exist
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize evaluator
    evaluator = RAGEvaluator()
    
    # Load test queries
    queries = evaluator.load_test_queries(str(queries_file))
    
    # Run queries and prepare dataset
    dataset = evaluator.prepare_ragas_dataset(queries)
    
    if len(dataset) == 0:
        print("✗ No successful queries to evaluate")
        sys.exit(1)
        
    # Try RAGAS evaluation (requires OpenAI API key)
    try:
        results = evaluator.run_evaluation(dataset)
        
        # Print summary
        evaluator.print_summary(results)
        
        # Save results
        evaluator.save_results(results, str(results_file))
        
        print("✓ Baseline evaluation complete!")
    except Exception as e:
        print(f"\n⚠ RAGAS evaluation skipped: {str(e)}")
        print("Note: RAGAS requires OpenAI API key. Saving query results only.\n")
        
        # Save query results without RAGAS metrics
        evaluator.save_query_results(queries, dataset, str(results_file))


if __name__ == "__main__":
    main()
