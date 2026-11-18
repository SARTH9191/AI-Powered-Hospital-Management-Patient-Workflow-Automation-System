#!/usr/bin/env python3
"""
Generate Google Docs API Token
Creates docs_token.pickle with proper scopes for document creation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

def generate_docs_token():
    """Generate new Google Docs API token with proper scopes"""
    
    print("🔧 Generating Google Docs API Token")
    print("=" * 50)
    
    try:
        from tools.google_docs_tool import authenticate_docs
        
        print("📋 Required scopes:")
        print("   • https://www.googleapis.com/auth/documents")
        print("   • https://www.googleapis.com/auth/drive.file") 
        print("   • https://www.googleapis.com/auth/drive")
        
        print("\n🔓 Starting OAuth flow...")
        print("   A browser window will open for authentication")
        
        # This will create docs_token.pickle automatically
        creds = authenticate_docs()
        
        if creds and creds.valid:
            print("\n✅ Google Docs token generated successfully!")
            print("📁 Token saved as: docs_token.pickle")
            
            # Test the token by creating a simple service
            from googleapiclient.discovery import build
            service = build('docs', 'v1', credentials=creds)
            
            print("🧪 Testing API access...")
            
            # Try to create a test document
            document = {
                'title': 'Test Document - Please Delete'
            }
            
            doc = service.documents().create(body=document).execute()
            doc_id = doc.get('documentId')
            
            print(f"✅ Test document created successfully!")
            print(f"📄 Document ID: {doc_id}")
            
            # Clean up - delete the test document
            try:
                from googleapiclient.discovery import build as build_drive
                drive_service = build_drive('drive', 'v3', credentials=creds)
                drive_service.files().delete(fileId=doc_id).execute()
                print("🗑️ Test document deleted")
            except:
                print("⚠️ Test document created but couldn't delete (manual cleanup needed)")
            
            print("\n🎉 Google Docs API is ready for use!")
            
        else:
            print("❌ Failed to generate valid credentials")
            
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_docs_token()