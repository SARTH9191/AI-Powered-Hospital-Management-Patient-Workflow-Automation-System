#!/usr/bin/env python3
"""
Redis Session Cache Clearer
Clears cached session data to force reload from PostgreSQL database
"""

import redis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None) or None

def clear_all_sessions():
    """Clear all session data from Redis"""
    try:
        # Connect to Redis
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Ping to check connection
        r.ping()
        print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        
        # Get all session keys
        session_keys = r.keys('session:*')
        
        if not session_keys:
            print("ℹ️  No sessions found in Redis cache")
            return
        
        print(f"\n🔍 Found {len(session_keys)} session(s) in cache:")
        for key in session_keys:
            print(f"   • {key}")
        
        # Ask for confirmation
        response = input("\n⚠️  Delete all sessions? (yes/no): ").strip().lower()
        
        if response == 'yes':
            # Delete all session keys
            deleted = r.delete(*session_keys)
            print(f"\n✅ Successfully deleted {deleted} session(s) from Redis cache")
            print("✅ Next login will load fresh state from PostgreSQL database")
        else:
            print("\n❌ Cancelled. No sessions deleted.")
    
    except redis.ConnectionError as e:
        print(f"❌ Could not connect to Redis: {e}")
        print(f"   Make sure Redis is running on {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        print(f"❌ Error: {e}")

def clear_specific_session(email):
    """Clear session for a specific email"""
    try:
        # Connect to Redis
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        
        r.ping()
        print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        
        # Search for sessions containing this email
        all_keys = r.keys('session:*')
        matching_keys = []
        
        for key in all_keys:
            try:
                session_data = r.get(key)
                if session_data and email.lower() in session_data.lower():
                    matching_keys.append(key)
            except:
                pass
        
        if not matching_keys:
            print(f"\nℹ️  No cached sessions found for email: {email}")
            return
        
        print(f"\n🔍 Found {len(matching_keys)} session(s) for {email}:")
        for key in matching_keys:
            print(f"   • {key}")
        
        # Delete matching sessions
        deleted = r.delete(*matching_keys)
        print(f"\n✅ Successfully deleted {deleted} session(s) from Redis cache")
        print(f"✅ Next login for {email} will load fresh state from PostgreSQL")
    
    except redis.ConnectionError as e:
        print(f"❌ Could not connect to Redis: {e}")
        print(f"   Make sure Redis is running on {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        print(f"❌ Error: {e}")

def view_sessions():
    """View all cached sessions without deleting"""
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        
        r.ping()
        print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        
        session_keys = r.keys('session:*')
        
        if not session_keys:
            print("\nℹ️  No sessions found in Redis cache")
            return
        
        print(f"\n📋 Found {len(session_keys)} session(s):\n")
        
        for key in session_keys:
            session_data = r.get(key)
            ttl = r.ttl(key)
            
            # Try to extract email from session data
            email = "Unknown"
            stage = "Unknown"
            try:
                if '"email"' in session_data:
                    import json
                    data = json.loads(session_data)
                    email = data.get('email', 'Unknown')
                    stage = data.get('current_stage', 'Unknown')
            except:
                pass
            
            print(f"🔑 Session: {key}")
            print(f"   📧 Email: {email}")
            print(f"   📍 Stage: {stage}")
            print(f"   ⏱️  TTL: {ttl} seconds ({ttl//60} minutes)" if ttl > 0 else "   ⏱️  TTL: No expiration")
            print()
    
    except redis.ConnectionError as e:
        print(f"❌ Could not connect to Redis: {e}")
        print(f"   Make sure Redis is running on {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 REDIS SESSION CACHE MANAGER")
    print("=" * 60)
    
    print("\nOptions:")
    print("1. View all cached sessions")
    print("2. Clear all cached sessions")
    print("3. Clear session for specific email")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        view_sessions()
    elif choice == "2":
        clear_all_sessions()
    elif choice == "3":
        email = input("\nEnter email address: ").strip()
        if email:
            clear_specific_session(email)
        else:
            print("❌ No email provided")
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")
