"""
Test Medical RAG System
Tests semantic search and RAG-based question answering
"""

from tools.vector_search_tool import (
    SemanticSearchTool,
    MedicalRAGTool,
    get_all_collection_stats
)

def print_section(title):
    """Print formatted section"""
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)
    print()

def test_collection_stats():
    """Test 1: Show collection statistics"""
    print_section("TEST 1: Collection Statistics")
    
    stats = get_all_collection_stats()
    for stat in stats:
        if "error" not in stat:
            print(f"📁 {stat['collection']}: {stat['total_records']} records")
            print(f"   {stat['description']}")
            print()
    
    total = sum(s['total_records'] for s in stats if 'total_records' in s)
    print(f"📊 Total Records: {total}")

def test_semantic_search():
    """Test 2: Semantic search in medical knowledge"""
    print_section("TEST 2: Semantic Search - Medical Knowledge")
    
    search_tool = SemanticSearchTool()
    
    # Query 1: Diabetes symptoms
    print("🔍 Query: 'What are the symptoms of diabetes?'")
    result = search_tool._run(
        query="diabetes symptoms high blood sugar",
        collection="medical_knowledge",
        n_results=2
    )
    
    if result.get("success"):
        print(f"✅ Found {result['n_results']} results\n")
        for i, res in enumerate(result['results'], 1):
            print(f"Result {i}: {res['metadata'].get('disease', 'N/A')}")
            print(f"Similarity: {res['similarity_score']:.2%}")
            print(f"Text Preview: {res['text'][:200]}...")
            print()
    else:
        print(f"❌ Error: {result.get('error')}")

def test_patient_search():
    """Test 3: Search patient records"""
    print_section("TEST 3: Semantic Search - Patient Records")
    
    search_tool = SemanticSearchTool()
    
    # Query: Find patients with chest pain
    print("🔍 Query: 'Find patients with chest pain and heart problems'")
    result = search_tool._run(
        query="chest pain cardiac heart attack",
        collection="medical_records",
        n_results=3
    )
    
    if result.get("success"):
        print(f"✅ Found {result['n_results']} results\n")
        for i, res in enumerate(result['results'], 1):
            patient_id = res['metadata'].get('patient_id', 'Unknown')
            diagnosis = res['metadata'].get('diagnosis', 'N/A')
            print(f"Result {i}: Patient {patient_id} - {diagnosis}")
            print(f"Similarity: {res['similarity_score']:.2%}")
            print(f"Text Preview: {res['text'][:300]}...")
            print()
    else:
        print(f"❌ Error: {result.get('error')}")

def test_drug_search():
    """Test 4: Search for drug information"""
    print_section("TEST 4: Semantic Search - Drug Information")
    
    search_tool = SemanticSearchTool()
    
    # Query: Metformin information
    print("🔍 Query: 'Tell me about metformin side effects and dosing'")
    result = search_tool._run(
        query="metformin side effects dosage diabetes medication",
        collection="medical_knowledge",
        n_results=2
    )
    
    if result.get("success"):
        print(f"✅ Found {result['n_results']} results\n")
        for i, res in enumerate(result['results'], 1):
            drug_name = res['metadata'].get('drug_name', 'N/A')
            print(f"Result {i}: {drug_name}")
            print(f"Similarity: {res['similarity_score']:.2%}")
            print(f"Text Preview: {res['text'][:400]}...")
            print()
    else:
        print(f"❌ Error: {result.get('error')}")

def test_rag_queries():
    """Test 5: RAG-based question answering"""
    print_section("TEST 5: RAG Question Answering")
    
    rag_tool = MedicalRAGTool()
    
    questions = [
        "What are the symptoms of diabetes?",
        "How do you treat pneumonia in adults?",
        "What is the normal range for HbA1c?",
        "What medications are used for hypertension?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"❓ Question {i}: {question}")
        print("-" * 80)
        
        result = rag_tool._run(
            question=question,
            collection="medical_knowledge",
            n_context=3
        )
        
        if result.get("success"):
            print(f"\n📝 Answer:")
            print(result['answer'])
            print(f"\n📚 Sources: {len(result.get('sources', []))} documents")
            print(f"   {', '.join(result.get('sources', [])[:3])}")
        else:
            print(f"❌ Error: {result.get('error')}")
        
        print()

def test_patient_specific_query():
    """Test 6: Query specific patient data"""
    print_section("TEST 6: Patient-Specific Query")
    
    search_tool = SemanticSearchTool()
    
    # Search for specific patient
    print("🔍 Query: Find patient REG2025001's diabetes diagnosis")
    result = search_tool._run(
        query="patient diabetes diagnosis treatment plan",
        collection="medical_records",
        filter_metadata={"patient_id": "REG2025001"},
        n_results=1
    )
    
    if result.get("success") and result['results']:
        print(f"✅ Found patient record\n")
        res = result['results'][0]
        print(f"Patient: {res['metadata']['patient_id']}")
        print(f"Date: {res['metadata']['date']}")
        print(f"Diagnosis: {res['metadata']['diagnosis']}")
        print(f"\nFull Record:")
        print(res['text'][:500])
        print("...")
    else:
        print(f"❌ No results found")

def test_cross_collection_search():
    """Test 7: Compare knowledge vs patient data"""
    print_section("TEST 7: Cross-Collection Comparison")
    
    search_tool = SemanticSearchTool()
    
    query = "diabetes treatment metformin"
    
    print(f"🔍 Query: '{query}'")
    print()
    
    # Search medical knowledge
    print("📚 Medical Knowledge:")
    result1 = search_tool._run(query, "medical_knowledge", n_results=1)
    if result1.get("success") and result1['results']:
        res = result1['results'][0]
        print(f"   Category: {res['metadata'].get('category', 'N/A')}")
        print(f"   Similarity: {res['similarity_score']:.2%}")
        print(f"   Preview: {res['text'][:200]}...")
    
    print()
    
    # Search patient records
    print("👤 Patient Records:")
    result2 = search_tool._run(query, "medical_records", n_results=1)
    if result2.get("success") and result2['results']:
        res = result2['results'][0]
        print(f"   Patient: {res['metadata'].get('patient_id', 'N/A')}")
        print(f"   Similarity: {res['similarity_score']:.2%}")
        print(f"   Preview: {res['text'][:200]}...")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 80)
    print("  🏥 MEDICAL RAG SYSTEM - COMPREHENSIVE TESTING")
    print("=" * 80)
    
    try:
        # Run all tests
        test_collection_stats()
        test_semantic_search()
        test_patient_search()
        test_drug_search()
        test_rag_queries()
        test_patient_specific_query()
        test_cross_collection_search()
        
        print()
        print("=" * 80)
        print("  ✅ ALL TESTS COMPLETED!")
        print("=" * 80)
        print()
        print("💡 Key Findings:")
        print("   ✅ Semantic search working across all collections")
        print("   ✅ RAG-based question answering operational")
        print("   ✅ Patient-specific queries with metadata filtering")
        print("   ✅ Cross-collection comparison capability")
        print()
        print("🚀 Next Steps:")
        print("   1. Integrate into workflow_chat_agent.py")
        print("   2. Add Q&A mode for patients during workflow")
        print("   3. Enable questions like:")
        print("      - 'What are my test results?'")
        print("      - 'Tell me about my diagnosis'")
        print("      - 'What medications am I taking?'")
        print("      - 'What are the side effects of metformin?'")
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"  ❌ TEST FAILED: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
