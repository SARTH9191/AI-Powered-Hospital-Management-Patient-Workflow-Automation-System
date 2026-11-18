"""
Medical Vector Search & RAG Tools
Uses ChromaDB for semantic search of medical records, patient history, diagnoses, treatments
Enables AI-powered medical knowledge retrieval
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from datetime import datetime

# ChromaDB imports
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️ ChromaDB not installed. Run: pip install chromadb sentence-transformers")


# ==================== CHROMADB SETUP ====================

# Initialize ChromaDB client
CHROMA_DB_PATH = "data/vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, lightweight model (384 dimensions)

def get_chroma_client():
    """Get or create ChromaDB client"""
    if not CHROMA_AVAILABLE:
        return None
    
    try:
        # Create persistent client
        client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        return client
    except Exception as e:
        print(f"❌ Failed to initialize ChromaDB: {e}")
        return None


def get_embedding_model():
    """Get sentence transformer model for embeddings"""
    if not CHROMA_AVAILABLE:
        return None
    
    try:
        model = SentenceTransformer(EMBEDDING_MODEL)
        return model
    except Exception as e:
        print(f"❌ Failed to load embedding model: {e}")
        return None


# ==================== COLLECTIONS ====================

COLLECTIONS = {
    "medical_records": "Patient medical history, diagnoses, symptoms, treatments",
    "lab_results": "Laboratory test results, values, interpretations",
    "diagnoses": "Disease diagnoses, symptoms, differential diagnoses",
    "treatments": "Treatment plans, medications, procedures, protocols",
    "patient_cases": "Complete patient case histories for similarity matching",
    "medical_knowledge": "General medical knowledge, disease information, treatment protocols, drug interactions, medical guidelines"
}


def get_or_create_collection(collection_name: str):
    """Get or create a ChromaDB collection"""
    client = get_chroma_client()
    if not client:
        return None
    
    try:
        # Get or create collection
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"description": COLLECTIONS.get(collection_name, "Medical data collection")}
        )
        return collection
    except Exception as e:
        print(f"❌ Failed to get collection '{collection_name}': {e}")
        return None


# ==================== INPUT SCHEMAS ====================

class IndexMedicalRecordInput(BaseModel):
    """Input for indexing medical records into vector database."""
    collection: str = Field(description="Collection name: medical_records, lab_results, diagnoses, treatments, patient_cases")
    text: str = Field(description="Medical record text to index (symptoms, diagnosis, treatment, etc.)")
    metadata: Dict[str, Any] = Field(description="Metadata: patient_id, date, doctor_id, record_type, etc.")
    record_id: Optional[str] = Field(default=None, description="Unique record ID (auto-generated if not provided)")


class SemanticSearchInput(BaseModel):
    """Input for semantic search in medical records."""
    query: str = Field(description="Search query (symptoms, diagnosis, treatment, medical condition)")
    collection: str = Field(default="medical_records", description="Collection to search in")
    n_results: int = Field(default=5, description="Number of similar results to return")
    filter_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Filter by metadata (e.g., {'patient_id': 'PAT001'})")


class MedicalRAGInput(BaseModel):
    """Input for RAG-based medical query answering."""
    question: str = Field(description="Medical question or query")
    collection: str = Field(default="medical_records", description="Collection to search for context")
    n_context: int = Field(default=3, description="Number of context documents to retrieve")


# ==================== INDEX TOOL ====================

class IndexMedicalRecordTool(BaseTool):
    name: str = "index_medical_record"
    description: str = """Index medical records into vector database for semantic search.
    Use this to store: patient symptoms, diagnoses, lab results, treatments, medical history.
    Enables AI-powered similarity search across all medical records.
    
    Parameters:
    - collection: Which collection to store in (medical_records, lab_results, diagnoses, treatments, patient_cases)
    - text: The medical text to index (detailed description)
    - metadata: Dict with patient_id, date, doctor_id, record_type, etc.
    - record_id: Optional unique ID (auto-generated if not provided)
    
    Returns: Success status, record ID, embedding dimensions
    """
    args_schema: type[BaseModel] = IndexMedicalRecordInput
    
    def _run(self, collection: str, text: str, metadata: Dict[str, Any], record_id: Optional[str] = None) -> dict:
        """Index a medical record into ChromaDB"""
        
        try:
            # Validate collection
            if collection not in COLLECTIONS:
                return {
                    "success": False,
                    "error": f"Invalid collection '{collection}'. Must be one of: {list(COLLECTIONS.keys())}"
                }
            
            # Get collection
            coll = get_or_create_collection(collection)
            if not coll:
                return {
                    "success": False,
                    "error": "Failed to access ChromaDB collection"
                }
            
            # Get embedding model
            model = get_embedding_model()
            if not model:
                return {
                    "success": False,
                    "error": "Failed to load embedding model"
                }
            
            # Generate embedding
            print(f"📊 Generating embedding for medical record...")
            embedding = model.encode(text).tolist()
            
            # Generate record ID if not provided
            if not record_id:
                record_id = f"{collection}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            # Add metadata
            metadata["indexed_at"] = datetime.now().isoformat()
            metadata["text_length"] = len(text)
            metadata["embedding_model"] = EMBEDDING_MODEL
            
            # Add to collection
            coll.add(
                ids=[record_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata]
            )
            
            print(f"✅ Indexed record: {record_id}")
            
            return {
                "success": True,
                "record_id": record_id,
                "collection": collection,
                "embedding_dimensions": len(embedding),
                "text_length": len(text),
                "metadata": metadata
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Indexing error: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }


# ==================== SEMANTIC SEARCH TOOL ====================

class SemanticSearchTool(BaseTool):
    name: str = "semantic_search_medical_records"
    description: str = """Search medical records by semantic similarity.
    Finds similar symptoms, diagnoses, treatments, patient cases using AI embeddings.
    Much smarter than keyword search - understands medical context.
    
    Use cases:
    - Find patients with similar symptoms
    - Find similar diagnoses for differential diagnosis
    - Find treatment protocols for similar conditions
    - Find historical cases matching current patient
    
    Parameters:
    - query: Natural language query (e.g., "fever and cough for 3 days")
    - collection: Which collection to search (medical_records, lab_results, diagnoses, treatments, patient_cases)
    - n_results: Number of similar results to return (default: 5)
    - filter_metadata: Optional filter (e.g., {'patient_id': 'PAT001'})
    
    Returns: List of similar records with similarity scores
    """
    args_schema: type[BaseModel] = SemanticSearchInput
    
    def _run(self, query: str, collection: str = "medical_records", n_results: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> dict:
        """Search for semantically similar medical records"""
        
        try:
            # Validate collection
            if collection not in COLLECTIONS:
                return {
                    "success": False,
                    "error": f"Invalid collection '{collection}'. Must be one of: {list(COLLECTIONS.keys())}"
                }
            
            # Get collection
            coll = get_or_create_collection(collection)
            if not coll:
                return {
                    "success": False,
                    "error": "Failed to access ChromaDB collection"
                }
            
            # Get embedding model
            model = get_embedding_model()
            if not model:
                return {
                    "success": False,
                    "error": "Failed to load embedding model"
                }
            
            # Generate query embedding
            print(f"🔍 Searching for: '{query}' in {collection}")
            query_embedding = model.encode(query).tolist()
            
            # Search collection
            results = coll.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata if filter_metadata else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results and results['ids'] and len(results['ids']) > 0:
                for i, record_id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        "record_id": record_id,
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "similarity_score": 1 - results['distances'][0][i],  # Convert distance to similarity
                        "distance": results['distances'][0][i]
                    })
            
            print(f"✅ Found {len(formatted_results)} similar records")
            
            return {
                "success": True,
                "query": query,
                "collection": collection,
                "n_results": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Search error: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }


# ==================== RAG TOOL ====================

class MedicalRAGTool(BaseTool):
    name: str = "medical_rag_query"
    description: str = """Answer medical questions using Retrieval-Augmented Generation (RAG).
    Retrieves relevant medical records and generates intelligent answers.
    
    Use cases:
    - "What are common treatments for pneumonia based on our records?"
    - "What were the symptoms of similar cases?"
    - "What lab results indicate diabetes?"
    - "Recommend treatment based on patient history"
    
    Parameters:
    - question: Medical question to answer
    - collection: Collection to search for context (default: medical_records)
    - n_context: Number of context documents to retrieve (default: 3)
    
    Returns: Answer with source references and context documents
    """
    args_schema: type[BaseModel] = MedicalRAGInput
    
    def _run(self, question: str, collection: str = "medical_records", n_context: int = 3) -> dict:
        """Answer medical question using RAG with LLM"""
        
        try:
            # First, do semantic search to get relevant context
            search_tool = SemanticSearchTool()
            search_result = search_tool._run(
                query=question,
                collection=collection,
                n_results=n_context
            )
            
            if not search_result.get("success"):
                return search_result
            
            # Extract context documents
            context_docs = search_result.get("results", [])
            
            if not context_docs:
                return {
                    "success": True,
                    "question": question,
                    "answer": "No relevant medical records found to answer this question.",
                    "context": [],
                    "sources": []
                }
            
            # Build context string
            context_text = "\n\n".join([
                f"Record {i+1} (Similarity: {doc['similarity_score']:.2f}):\n{doc['text']}"
                for i, doc in enumerate(context_docs)
            ])
            
            # Create RAG prompt
            rag_prompt = f"""Based on the following medical records, answer this question:

Question: {question}

Relevant Medical Records:
{context_text}

Instructions:
- Provide a clear, evidence-based answer
- Reference specific records when applicable
- If records don't contain enough information, state that clearly
- Use medical terminology appropriately

Answer:"""
            
            # Call LLM to generate answer with RAG context
            try:
                # Import existing Gemini LLM from project
                from src.llm import llm
                
                # Get LLM answer using Gemini
                llm_response = llm.invoke(rag_prompt)
                llm_answer = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
                
                return {
                    "success": True,
                    "question": question,
                    "answer": llm_answer,
                    "context_documents": context_docs,
                    "sources": [doc["record_id"] for doc in context_docs],
                    "num_context_docs": len(context_docs),
                    "llm_model": "gemini-2.5-flash"
                }
                
            except ImportError as e:
                # Fallback if LLM not available
                return {
                    "success": True,
                    "question": question,
                    "answer": f"[LLM unavailable - {str(e)}]",
                    "rag_prompt": rag_prompt,
                    "context_documents": context_docs,
                    "sources": [doc["record_id"] for doc in context_docs],
                    "note": "RAG context retrieved successfully. LLM import failed."
                }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ RAG error: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }


# ==================== UTILITY FUNCTIONS ====================

def get_collection_stats(collection_name: str) -> dict:
    """Get statistics about a collection"""
    try:
        coll = get_or_create_collection(collection_name)
        if not coll:
            return {"error": "Collection not accessible"}
        
        count = coll.count()
        return {
            "collection": collection_name,
            "total_records": count,
            "description": COLLECTIONS.get(collection_name, "Unknown collection")
        }
    except Exception as e:
        return {"error": str(e)}


def get_all_collection_stats() -> List[dict]:
    """Get stats for all collections"""
    return [get_collection_stats(name) for name in COLLECTIONS.keys()]


# ==================== EXPORT ALL TOOLS ====================

def get_all_vector_search_tools():
    """Get all vector search tools as a list"""
    return [
        IndexMedicalRecordTool(),
        SemanticSearchTool(),
        MedicalRAGTool()
    ]


# ==================== TESTING ====================

if __name__ == "__main__":
    print("="*70)
    print("🧪 VECTOR SEARCH TOOL TEST")
    print("="*70)
    
    # Test 1: Check ChromaDB availability
    print("\n1️⃣ Testing ChromaDB setup...")
    client = get_chroma_client()
    if client:
        print(f"✅ ChromaDB client initialized")
        print(f"   Database path: {CHROMA_DB_PATH}")
    else:
        print("❌ ChromaDB not available")
    
    # Test 2: Check embedding model
    print("\n2️⃣ Testing embedding model...")
    model = get_embedding_model()
    if model:
        print(f"✅ Embedding model loaded: {EMBEDDING_MODEL}")
        test_text = "Patient has fever and cough"
        embedding = model.encode(test_text)
        print(f"   Embedding dimensions: {len(embedding)}")
        print(f"   Sample embedding (first 5): {embedding[:5]}")
    else:
        print("❌ Embedding model not available")
    
    # Test 3: Test tools
    print("\n3️⃣ Testing tools...")
    index_tool = IndexMedicalRecordTool()
    search_tool = SemanticSearchTool()
    rag_tool = MedicalRAGTool()
    
    print(f"✅ Index Tool: {index_tool.name}")
    print(f"✅ Search Tool: {search_tool.name}")
    print(f"✅ RAG Tool: {rag_tool.name}")
    
    # Test 4: Collection stats
    print("\n4️⃣ Collection Statistics...")
    stats = get_all_collection_stats()
    for stat in stats:
        if "error" not in stat:
            print(f"   📊 {stat['collection']}: {stat['total_records']} records")
    
    print("\n" + "="*70)
    print("✅ VECTOR SEARCH TOOLS READY!")
    print("="*70)
    print("\n📚 Available Collections:")
    for name, desc in COLLECTIONS.items():
        print(f"   - {name}: {desc}")
    
    print("\n🔧 Next Steps:")
    print("   1. Index medical records using IndexMedicalRecordTool")
    print("   2. Search records using SemanticSearchTool")
    print("   3. Ask questions using MedicalRAGTool")
