#!/usr/bin/env python3
"""
Quick test to verify OpenAI API key is working before running full evaluation.
"""

import os
import sys

def test_openai_key():
    """Test if OpenAI API key is set and working."""
    
    print("=" * 60)
    print("Testing OpenAI API Key")
    print("=" * 60)
    
    # Check if key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("✗ OPENAI_API_KEY environment variable not set!")
        print("\nPlease set it with:")
        print("  export OPENAI_API_KEY='sk-proj-your-key-here'")
        return False
    
    print(f"✓ OPENAI_API_KEY is set (length: {len(api_key)})")
    print(f"  Starts with: {api_key[:10]}...")
    
    # Try to import OpenAI
    try:
        from openai import OpenAI
        print("✓ OpenAI library imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import OpenAI: {e}")
        print("\nTry: pip install openai")
        return False
    
    # Try to create client and make a simple API call
    try:
        print("\nTesting API connection...")
        client = OpenAI(api_key=api_key)
        
        # Make a minimal API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello' in one word"}
            ],
            max_tokens=10
        )
        
        answer = response.choices[0].message.content
        print(f"✓ API call successful!")
        print(f"  Response: {answer}")
        print(f"  Model: {response.model}")
        print(f"  Tokens used: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"✗ API call failed: {e}")
        print("\nPossible issues:")
        print("  - Invalid API key")
        print("  - Network connection problem")
        print("  - API quota exceeded")
        return False

def test_ragas_with_openai():
    """Test if RAGAS can use OpenAI."""
    
    print("\n" + "=" * 60)
    print("Testing RAGAS with OpenAI")
    print("=" * 60)
    
    try:
        from ragas.metrics import Faithfulness
        print("✓ RAGAS metrics imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import RAGAS: {e}")
        print("\nTry: pip install ragas")
        return False
    
    try:
        from datasets import Dataset
        print("✓ Datasets library imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import datasets: {e}")
        print("\nTry: pip install datasets")
        return False
    
    # Try a minimal RAGAS evaluation
    try:
        print("\nTesting minimal RAGAS evaluation...")
        
        # Create minimal test dataset
        test_data = {
            "user_input": ["What is 2+2?"],
            "response": ["2+2 equals 4"],
            "retrieved_contexts": [["The sum of 2 and 2 is 4. Basic arithmetic."]]
        }
        
        dataset = Dataset.from_dict(test_data)
        print("✓ Test dataset created")
        
        # Try to evaluate (this will use OpenAI)
        from ragas import evaluate
        result = evaluate(dataset, metrics=[Faithfulness()])
        
        print("✓ RAGAS evaluation successful!")
        print(f"  Result type: {type(result)}")
        
        # RAGAS 0.4.x returns EvaluationResult object with .scores attribute
        if hasattr(result, 'scores'):
            scores = result.scores
            print(f"  Scores: {scores}")
            if 'faithfulness' in scores:
                print(f"  Faithfulness score: {scores['faithfulness']:.4f}")
        elif hasattr(result, 'to_pandas'):
            df = result.to_pandas()
            print(f"  DataFrame shape: {df.shape}")
            print(f"  Columns: {df.columns.tolist()}")
            if 'faithfulness' in df.columns:
                print(f"  Faithfulness score: {df['faithfulness'].mean():.4f}")
        else:
            print(f"  Result attributes: {dir(result)}")
            print(f"  Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"✗ RAGAS evaluation failed: {e}")
        return False

if __name__ == "__main__":
    print("\n🔑 OpenAI API Key Test\n")
    
    # Test 1: OpenAI key
    openai_ok = test_openai_key()
    
    if not openai_ok:
        print("\n" + "=" * 60)
        print("❌ OpenAI test failed - fix issues before running evaluation")
        print("=" * 60)
        sys.exit(1)
    
    # Test 2: RAGAS with OpenAI
    ragas_ok = test_ragas_with_openai()
    
    print("\n" + "=" * 60)
    if openai_ok and ragas_ok:
        print("✅ All tests passed! Ready to run full evaluation")
        print("\nNext step:")
        print("  python run_ragas_baseline.py")
    else:
        print("⚠️  Some tests failed - check errors above")
    print("=" * 60)
    print()
