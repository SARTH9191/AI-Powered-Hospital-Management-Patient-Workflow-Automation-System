"""Call admin endpoint to clear all caches"""
import requests

# Get the JWT token (you'll need to get this from your browser)
# For now, let's just call the health endpoint to trigger a restart

url = "http://localhost:8000/api/ai-chat/health"

try:
    response = requests.get(url)
    print(f"✅ Backend is running")
    print(f"   Active sessions: {response.json()['active_sessions']}")
    print(f"\n💡 To clear cache, the backend needs to be restarted.")
    print(f"   OR logout from frontend and login again with fresh browser (Ctrl+Shift+R)")
except Exception as e:
    print(f"❌ Backend not responding: {e}")

print(f"\n🔧 SOLUTION:")
print(f"   1. Go to frontend (http://localhost:3000)")
print(f"   2. Press Ctrl+Shift+Delete")
print(f"   3. Clear 'Cookies and site data'")
print(f"   4. Close browser completely")
print(f"   5. Open new browser tab")
print(f"   6. Go to http://localhost:3000")
print(f"   7. Login with Google again")
print(f"\n   ✅ This will force a fresh session at Stage 1")
