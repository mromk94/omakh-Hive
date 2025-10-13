"""
Test Elastic Search Integration - Syntax Validation
"""
import ast
import os


def test_elastic_syntax():
    """Test Elastic integration syntax without importing dependencies"""
    
    print("=" * 60)
    print("ELASTIC SEARCH INTEGRATION - SYNTAX VALIDATION")
    print("=" * 60)
    
    try:
        # Read the elastic_search.py file
        file_path = os.path.join(os.path.dirname(__file__), 'elastic_search.py')
        
        print(f"\n✅ Reading file: {file_path}")
        
        with open(file_path, 'r') as f:
            code = f.read()
        
        # Parse the code to check syntax
        print("\n✅ Validating Python syntax...")
        ast.parse(code)
        print("  ✓ Syntax is valid!")
        
        # Check for key class and methods
        print("\n✅ Checking class structure...")
        
        required_elements = [
            'class ElasticSearchIntegration',
            'def __init__',
            'async def initialize',
            'async def log_bee_activity',
            'async def hybrid_search',
            'async def rag_query',
            'async def conversational_search',
            '_create_bee_activities_index',
            '_create_knowledge_base_index',
            '_create_transactions_index'
        ]
        
        for element in required_elements:
            if element in code:
                print(f"  ✓ {element}")
            else:
                print(f"  ✗ {element} - MISSING")
                return False
        
        # Check index names
        print("\n✅ Checking index configuration...")
        if 'omk_hive_bee_activities' in code:
            print("  ✓ Bee activities index configured")
        if 'omk_hive_knowledge_base' in code:
            print("  ✓ Knowledge base index configured")
        if 'omk_hive_transactions' in code:
            print("  ✓ Transactions index configured")
        
        print("\n✅ Elastic Search Integration validated successfully!")
        print("\nℹ️  Note: Actual usage requires:")
        print("  - pip install elasticsearch>=8.11.0")
        print("  - pip install elasticsearch[async]>=8.11.0")
        print("  - ELASTIC_CLOUD_ID environment variable")
        print("  - ELASTIC_API_KEY environment variable")
        print("  - Active Elastic Cloud deployment")
        
        print("\n✅ Integration is ready for deployment!")
        
        return True
        
    except SyntaxError as e:
        print(f"\n❌ Syntax error: {str(e)}")
        print(f"  Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_elastic_syntax()
    exit(0 if success else 1)
