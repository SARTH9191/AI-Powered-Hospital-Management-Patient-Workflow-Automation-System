"""
Medical Knowledge ChromaDB Tool
- Indexes `more.json` (doctor specialties, symptoms, required tests)
- Provides semantic/keyword matching to suggest tests and doctor specialty
"""

import os
import json
import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

# Reuse vector search tools
from tools.vector_search_tool import IndexMedicalRecordTool, SemanticSearchTool, get_or_create_collection, COLLECTIONS

MORE_JSON = os.path.join(os.path.dirname(__file__), '..', 'more.json')
MED_KNOWLEDGE_COLLECTION = 'medical_knowledge'


class SuggestTestsInput(BaseModel):
    history_text: str = Field(description="Combined past + current medical history text")
    n_results: int = Field(default=3, description="Max number of suggestions to return")


class SuggestTestsFromHistoryTool(BaseTool):
    name: str = "suggest_tests_from_history"
    description: str = "Suggest lab tests and doctor specialty based on patient's combined medical history. Uses ChromaDB if available, otherwise falls back to keyword matching."
    args_schema: type[BaseModel] = SuggestTestsInput

    def __init__(self):
        BaseTool.__init__(self)
        # Ensure collection exists and index `more.json` if not present
        try:
            coll = get_or_create_collection(MED_KNOWLEDGE_COLLECTION)
            # If collection was created, index entries from more.json
            # Note: get_or_create_collection does not expose item count reliably here, so we index idempotently
            self._ensure_indexed()
        except Exception:
            pass

    def _ensure_indexed(self):
        """Index entries from more.json into ChromaDB using IndexMedicalRecordTool"""
        try:
            if not os.path.exists(MORE_JSON):
                return

            with open(MORE_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)

            index_tool = IndexMedicalRecordTool()

            for entry in data:
                doc_text = f"Symptom/Disease: {entry.get('symptom_or_disease')}\nNotes: {entry.get('notes')}\nTags: {','.join(entry.get('tags', []))}\nRequired Tests: {', '.join(entry.get('required_tests', []))}"
                metadata = {
                    'doctor': entry.get('doctor'),
                    'symptom': entry.get('symptom_or_disease'),
                    'tags': ','.join(entry.get('tags', [])),  # Convert list to comma-separated string
                    'required_tests': ', '.join(entry.get('required_tests', []))  # Convert list to comma-separated string
                }
                # Use deterministic id to avoid duplicate indexing
                record_id = f"medknow_{re.sub(r'[^a-zA-Z0-9]', '_', entry.get('symptom_or_disease').lower())}"
                try:
                    index_tool._run(collection=MED_KNOWLEDGE_COLLECTION, text=doc_text, metadata=metadata, record_id=record_id)
                except Exception:
                    # If indexing fails (e.g., Chroma unavailable), ignore and continue
                    pass
        except Exception:
            pass

    def _run(self, history_text: str, n_results: int = 3) -> Dict[str, Any]:
        """Return suggested tests and recommended doctor specialty based on history_text"""
        try:
            # First try semantic search via existing SemanticSearchTool
            search_tool = SemanticSearchTool()
            search_res = search_tool._run(query=history_text, collection=MED_KNOWLEDGE_COLLECTION, n_results=n_results*2)  # Get more results to filter

            suggestions = []
            suggested_doctor = None

            if search_res.get('success') and search_res.get('results'):
                for r in search_res.get('results', []):
                    meta = r.get('metadata', {})
                    # Parse required_tests from comma-separated string
                    tests_str = meta.get('required_tests', '')
                    tests = [t.strip() for t in tests_str.split(',') if t.strip()] if isinstance(tests_str, str) else []
                    doctor = meta.get('doctor') or meta.get('doctor', None)
                    similarity = r.get('similarity_score', 0)
                    # Skip results with None doctor and no tests
                    if doctor and tests:
                        suggestions.append({
                            'doctor': doctor,
                            'tests': tests,
                            'notes': meta.get('symptom', ''),
                            'score': similarity
                        })
                # Pick top doctor by frequency/score
                if suggestions:
                    suggested_doctor = suggestions[0].get('doctor')
                    suggestions = suggestions[:n_results]  # Limit to requested count

                if suggested_doctor:
                    return {
                        'success': True,
                        'suggested_tests': suggestions,
                        'suggested_doctor': suggested_doctor
                    }

            # Fallback: keyword matching using more.json
            if os.path.exists(MORE_JSON):
                with open(MORE_JSON, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                history_lower = history_text.lower()
                matches = []
                for entry in data:
                    symptom = entry.get('symptom_or_disease', '').lower()
                    tags = [t.lower() for t in entry.get('tags', [])]
                    if symptom and (symptom in history_lower or any(tag in history_lower for tag in tags)):
                        matches.append(entry)

                # If no exact matches, try token overlap
                if not matches:
                    tokens = set(re.findall(r"\\w+", history_lower))
                    for entry in data:
                        entry_tokens = set(re.findall(r"\\w+", (entry.get('symptom_or_disease','') + ' ' + ' '.join(entry.get('tags',[]))).lower()))
                        if tokens.intersection(entry_tokens):
                            matches.append(entry)

                # Build suggestions
                for m in matches[:n_results]:
                    suggestions.append({
                        'doctor': m.get('doctor'),
                        'tests': m.get('required_tests', []),
                        'notes': m.get('notes', ''),
                        'score': 1.0
                    })

                if suggestions:
                    suggested_doctor = suggestions[0].get('doctor')

                return {
                    'success': True,
                    'suggested_tests': suggestions,
                    'suggested_doctor': suggested_doctor
                }

            return {'success': False, 'error': 'No suggestions found'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported")
