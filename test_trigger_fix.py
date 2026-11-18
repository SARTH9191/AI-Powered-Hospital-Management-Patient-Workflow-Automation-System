#!/usr/bin/env python3
"""
Test the fixed document upload triggers
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_trigger_detection():
    """Test that new triggers are detected"""
    
    # Test phrases that should trigger document check
    test_phrases = [
        "I again upload the document can you check it?",
        "Again upload done",
        "I have re-uploaded the documents", 
        "Can you check it now?",
        "Please verify it"
    ]
    
    triggers = [
        "yes", "ready", "done", "uploaded", "finished", "complete",
        "ok i have uploaded the document", "ok i have uploaded the documents", 
        "i have uploaded", "uploaded documents", "documents uploaded",
        "i uploaded", "finished uploading", "upload complete", "all done",
        "documents are uploaded", "files uploaded", "documents ready",
        "i again upload", "again upload", "re-upload", "reupload", 
        "check it", "can you check", "please check", "verify it"
    ]
    
    print("🧪 Testing Updated Trigger Detection")
    print("=" * 50)
    
    for phrase in test_phrases:
        message_lower = phrase.lower().strip()
        upload_indicated = any(trigger in message_lower for trigger in triggers)
        
        print(f"📝 '{phrase}'")
        print(f"   Trigger detected: {'✅' if upload_indicated else '❌'} {upload_indicated}")
        
        if upload_indicated:
            matching_triggers = [trigger for trigger in triggers if trigger in message_lower]
            print(f"   Matched: {matching_triggers}")
        print()

if __name__ == "__main__":
    test_trigger_detection()