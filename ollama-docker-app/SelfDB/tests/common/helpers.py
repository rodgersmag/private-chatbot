"""
Helper functions for SelfDB test suite.
"""

import os
import json
import time
import asyncio
import requests
import websockets
import threading
import queue
from typing import Optional, Dict, Any
from datetime import datetime

from . import config, state

# ----------------------- File/Logging Helpers ----------------------------

def get_next_results_filename():
    """Return the next free test_results_X.txt filename."""
    base, ext, idx = "test_results", ".txt", 1
    while os.path.exists(f"{base}_{idx}{ext}"):
        idx += 1
    return f"{base}_{idx}{ext}"

def write_to_file(content: str):
    """Print to stdout and append to results_file (if open)."""
    print(content)
    if state.results_file:
        state.results_file.write(content + "\n")
        state.results_file.flush()

def init_results_file(filename: Optional[str] = None):
    """Initialize the results file for logging."""
    if filename is None:
        filename = get_next_results_filename()
    state.results_filename = filename
    state.results_file = open(filename, "w", encoding="utf-8")
    
    # Write header
    write_to_file(f"SelfDB API Test Results")
    write_to_file(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    write_to_file(f"Results File: {filename}")
    write_to_file("=" * 80)
    
    write_to_file("🚀 Starting SelfDB API Tests")
    write_to_file(f"Backend URL: {config.BACKEND_URL}")
    write_to_file(f"Storage URL: {config.STORAGE_URL}")
    write_to_file(f"API Key: {config.API_KEY[:20]}...")
    write_to_file("\n📝 Note: This file includes curl examples for documentation purposes")
    write_to_file("=" * 80)
    
    return filename

def close_results_file():
    """Close the results file."""
    if state.results_file:
        state.results_file.close()
        state.results_file = None

# ----------------------- Request Helpers ----------------------------

def get_headers(auth: bool = False, admin: bool = False) -> Dict[str, str]:
    """Get request headers, using admin or user token if specified."""
    hdr = {"apikey": config.API_KEY}
    token_to_use = None
    if admin:
        token_to_use = state.admin_access_token
    elif auth:
        token_to_use = state.access_token
    
    if token_to_use:
        hdr["Authorization"] = f"Bearer {token_to_use}"
    return hdr

def print_test_header(test_name: str):
    """Print a formatted test header."""
    write_to_file(f"\n{'='*60}\nTesting: {test_name}\n{'='*60}")

def print_response(resp: requests.Response,
                   description: str = "", expected_status: int | None = None):
    """Print formatted response information (and log to file)"""
    req = resp.request
    # Request info
    if req is not None:
        req_line = f"Request: {req.method} {req.url}"
        print(req_line)
        if state.results_file:
            state.results_file.write(req_line + "\n")
            
            # Generate curl example for documentation
            state.results_file.write("\nCurl example:\n")
            curl_cmd = f"curl -X {req.method} \"{req.url}\""
            
            # Add headers to curl command
            for key, value in req.headers.items():
                if key.lower() not in ['user-agent', 'accept-encoding', 'connection', 'content-length']:
                    if key.lower() == 'authorization' and value.startswith('Bearer '):
                        curl_cmd += f" \\\n  -H \"{key}: Bearer your_access_token\""
                    elif key.lower() in ['apikey', 'anon-key']:
                        curl_cmd += f" \\\n  -H \"{key}: your_anon_key\""
                    else:
                        curl_cmd += f" \\\n  -H \"{key}: {value}\""
            
            # Add body if present
            if req.body:
                try:
                    body_txt = req.body.decode() if isinstance(req.body, (bytes, bytearray)) else str(req.body)
                    if req.headers.get('Content-Type') == 'application/json':
                        # Pretty print JSON for documentation
                        body_json = json.loads(body_txt)
                        body_formatted = json.dumps(body_json, indent=2)
                        curl_cmd += f" \\\n  -d '{body_formatted}'"
                    elif req.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                        curl_cmd += f" \\\n  -d \"{body_txt}\""
                    else:
                        if len(body_txt) < 500:
                            curl_cmd += f" \\\n  --data-binary '{body_txt}'"
                except Exception:
                    pass
            
            state.results_file.write(curl_cmd + "\n\n")
            state.results_file.flush()
    
    # Determine success
    if expected_status is not None:
        is_success = resp.status_code == expected_status
        status_color = '\033[92m' if is_success else '\033[91m'
    else:
        is_success = 200 <= resp.status_code < 300
        status_color = '\033[92m' if is_success else '\033[91m'
    
    reset_color = '\033[0m'
    
    # Console output with colors
    print(f"Status: {status_color}{resp.status_code}{reset_color}")
    # File output without colors
    if state.results_file:
        state.results_file.write(f"Status: {resp.status_code}\n")
        state.results_file.flush()
    
    if description:
        write_to_file(f"Description: {description}")
    
    # Track test results
    state.test_summary["total"] += 1
    if is_success:
        state.test_summary["passed"] += 1
        if description:
            state.test_summary["passed_tests"].append(description)
    else:
        state.test_summary["failed"] += 1
        state.test_summary["errors"].append({
            "description": description,
            "status_code": resp.status_code,
            "url": resp.url
        })
    
    try:
        # Format response for documentation
        response_json = resp.json()
        write_to_file(f"Response: {json.dumps(response_json, indent=2)}")
        
        # Add example response format for successful requests
        if is_success and state.results_file:
            state.results_file.write(f"\nExample Response ({resp.status_code}):\n")
            state.results_file.write(f"```json\n{json.dumps(response_json, indent=2)}\n```\n")
    except json.JSONDecodeError:
        write_to_file(f"Response: {resp.text}")
        if state.results_file and resp.text:
            state.results_file.write(f"\nExample Response ({resp.status_code}):\n")
            state.results_file.write(f"```\n{resp.text}\n```\n")
    
    write_to_file("-" * 50)

# ----------------------- Admin Token Helper ----------------------------

def get_admin_token() -> Optional[str]:
    """Get admin token for superuser operations."""
    if state.admin_access_token:
        return state.admin_access_token
    try:
        resp = requests.post(
            f"{config.BACKEND_URL}/auth/login",
            headers={"apikey": config.API_KEY,
                     "Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={config.ADMIN_EMAIL}&password={config.ADMIN_PASSWORD}"
        )
        if resp.status_code == 200:
            state.admin_access_token = resp.json().get("access_token")
            return state.admin_access_token
        write_to_file(f"⚠️  Failed to get admin token: {resp.status_code}")
    except Exception as e:
        write_to_file(f"⚠️  Error getting admin token: {e}")
    return None

# ----------------------- WebSocket Helpers ----------------------------

def _ws_is_closed(conn) -> bool:
    """Check if WebSocket connection is closed."""
    if conn is None:
        return True
    closed = getattr(conn, "closed", None)
    if closed is None:
        return False
    return bool(closed) if isinstance(closed, bool) else closed.done()

async def setup_websocket_connection(token_to_use: Optional[str] = None):
    """Connect & authenticate the WS using the provided token."""
    auth_token = token_to_use or state.access_token
    if not auth_token:
        write_to_file("❌ Cannot setup WebSocket – no token")
        return False

    try:
        ws_url = config.BACKEND_URL.replace("http://", "ws://").replace("https://", "wss://") \
                 + f"/realtime/ws?apikey={config.API_KEY}"

        write_to_file(f"Request: WS CONNECT {ws_url}")
        state.websocket_connection = await websockets.connect(ws_url)

        # Send auth
        await state.websocket_connection.send(json.dumps({"type": "authenticate",
                                                    "token": auth_token}))
        write_to_file("Request: WS SEND authenticate {'token': '***'}")

        resp = json.loads(await state.websocket_connection.recv())
        write_to_file(f"Response: {json.dumps(resp, indent=2)}")
        write_to_file("-" * 50)

        if resp.get("type") == "connected":
            write_to_file(f"✅ WebSocket authenticated: {resp.get('user_id')}")
            return True
        write_to_file(f"❌ WS auth failed: {resp}")
    except Exception as e:
        write_to_file(f"❌ WebSocket error: {e}")
    return False

async def subscribe_to_changes():
    """Subscribe to all relevant change notifications"""
    if not state.websocket_connection:
        return

    subscriptions = [
        {"subscription_id": "tables_changes"},
        {"subscription_id": "buckets_changes"}, 
        {"subscription_id": "functions_changes"},
        {"subscription_id": "files_changes"},
        {"subscription_id": "users_changes"}
    ]

    for sub in subscriptions:
        try:
            write_to_file(f"Request: WS SEND subscribe {sub['subscription_id']}")
            await state.websocket_connection.send(json.dumps({
                "type": "subscribe",
                **sub
            }))
            sub_response = json.loads(await state.websocket_connection.recv())
            write_to_file(f"Response: {json.dumps(sub_response, indent=2)}")
            write_to_file("-" * 50)
            if sub_response.get("type") == "subscribed":
                write_to_file(f"✅ Subscribed to {sub['subscription_id']}")
            else:
                write_to_file(f"❌ Failed to subscribe to {sub['subscription_id']}: {sub_response}")
        except Exception as e:
            write_to_file(f"❌ Subscription error for {sub['subscription_id']}: {str(e)}")

async def websocket_listener():
    """Listen for WebSocket notifications"""
    notification_queue = queue.Queue()
    
    try:
        while state.websocket_connection and not _ws_is_closed(state.websocket_connection):
            try:
                message = await asyncio.wait_for(
                    state.websocket_connection.recv(), timeout=1.0
                )
                notification = json.loads(message)
                
                # Store notification with timestamp
                timestamped_notification = {
                    "timestamp": datetime.now().isoformat(),
                    "notification": notification
                }
                state.websocket_notifications.append(timestamped_notification)
                notification_queue.put(timestamped_notification)
                
                # Log real-time notifications
                if notification.get("type") == "database_change":
                    sub_id = notification.get("subscription_id")
                    data = notification.get("data", {})
                    write_to_file(f"🔔 Real-time notification: {sub_id} - {data}")
                    
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                write_to_file("📡 WebSocket connection closed")
                break
            except Exception as e:
                write_to_file(f"❌ WebSocket listener error: {str(e)}")
                break
                
    except Exception as e:
        write_to_file(f"❌ WebSocket listener setup error: {str(e)}")

def start_websocket_monitoring(token_override: Optional[str] = None):
    """Spawn background thread running authenticated listener."""
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        state.websocket_loop = loop

        async def main():
            if await setup_websocket_connection(token_override):
                await subscribe_to_changes()
                await websocket_listener()
        loop.run_until_complete(main())

    state.websocket_thread = threading.Thread(target=run, daemon=True)
    state.websocket_thread.start()
    time.sleep(2)  # Allow connection to establish

def cleanup_websocket():
    """Clean up WebSocket connection"""
    try:
        if state.websocket_connection and not _ws_is_closed(state.websocket_connection):
            if state.websocket_loop and state.websocket_loop.is_running():
                fut = asyncio.run_coroutine_threadsafe(
                    state.websocket_connection.close(), state.websocket_loop
                )
                fut.result(timeout=2)
            else:
                asyncio.run(state.websocket_connection.close())
            write_to_file("✅ WebSocket connection closed")
    except Exception as e:
        err = str(e).strip()
        if err:
            write_to_file(f"⚠️ Error closing WebSocket: {err}")
    
    if state.websocket_thread and state.websocket_thread.is_alive():
        state.websocket_thread.join(timeout=2)

def generate_websocket_summary():
    """Generate comprehensive WebSocket notification summary"""
    write_to_file(f"\n{'=' * 60}")
    write_to_file("📡 WEBSOCKET REAL-TIME NOTIFICATIONS SUMMARY")
    write_to_file('=' * 60)
    
    if not state.websocket_notifications:
        write_to_file("❌ No WebSocket notifications received")
        write_to_file("⚠️  This could indicate:")
        write_to_file("   - WebSocket service is not running")
        write_to_file("   - Database triggers are not configured")  
        write_to_file("   - Notification channels are not set up")
        return
    
    # Group notifications by type
    notification_groups = {}
    for notif in state.websocket_notifications:
        notification = notif["notification"]
        notif_type = notification.get("type", "unknown")
        subscription_id = notification.get("subscription_id", "unknown")
        
        key = f"{notif_type}:{subscription_id}"
        if key not in notification_groups:
            notification_groups[key] = []
        notification_groups[key].append(notif)
    
    write_to_file(f"📊 Total notifications received: {len(state.websocket_notifications)}")
    write_to_file(f"📊 Notification types: {len(notification_groups)}")
    
    # Detailed breakdown
    for group_key, notifications in notification_groups.items():
        notif_type, sub_id = group_key.split(":", 1)
        write_to_file(f"\n🔔 {sub_id} ({notif_type}): {len(notifications)} notifications")
        
        # Show first few notifications as examples
        for i, notif in enumerate(notifications[:3]):
            timestamp = notif["timestamp"]
            data = notif["notification"].get("data", {})
            write_to_file(f"   [{timestamp}] {data}")
        
        if len(notifications) > 3:
            write_to_file(f"   ... and {len(notifications) - 3} more")

# ----------------------- Cleanup Helpers ----------------------------

def dump_storage_state(tag: str = "") -> None:
    """Print all buckets in the storage service and list their files."""
    try:
        write_to_file(f"\n📂 STORAGE STATE DUMP {tag}".strip())
        resp = requests.get(f"{config.STORAGE_URL}/buckets", headers=get_headers())
        write_to_file(f"Buckets status: {resp.status_code}")
        if resp.status_code != 200:
            write_to_file("Failed to list storage buckets.")
            return
        buckets = resp.json()
        if not buckets:
            write_to_file("No buckets found in storage.")
            return

        for b in buckets:
            name = b.get("name")
            owner = b.get("owner_id")
            public = b.get("is_public")
            write_to_file(f"  • {name}  (public={public}, owner={owner})")
            # List files
            files_resp = requests.get(f"{config.STORAGE_URL}/files/list/{name}", headers=get_headers())
            if files_resp.status_code == 200:
                files = files_resp.json()
                if files:
                    for f in files:
                        write_to_file(f"      - {f.get('object_name')}  ({f.get('size')} bytes)")
                else:
                    write_to_file("      (empty)")
            else:
                write_to_file(f"      (failed to list files: {files_resp.status_code})")
    except Exception as e:
        write_to_file(f"⚠️  Error dumping storage state: {str(e)}")

def cleanup_test_resources():
    """Clean up all test resources created during testing"""
    print_test_header("Cleanup Test Resources")
    
    if not state.access_token:
        print("⚠️ Skipping cleanup - no authentication token")
        return
    
    # -----------------------------------------------------------------
    # Ensure optional attributes exist to avoid AttributeError when a
    # specific test (like test_03_users.py) is run standalone.
    # -----------------------------------------------------------------
    for attr, default in [
        ("created_file_ids", []),
        ("created_function_ids", []),
        ("created_user_ids", []),
        ("test_bucket_id", None),
        ("test_storage_bucket_id", None),
        ("test_storage_bucket_name", None),
    ]:
        if not hasattr(state, attr):
            setattr(state, attr, default)
    
    # Get admin token for bucket deletion
    admin_token = get_admin_token()
    
    cleanup_results = []
    
    try:
        # Clean up created files first (before deleting buckets)
        for file_id in state.created_file_ids:
            try:
                admin_headers = {"apikey": config.API_KEY, "Authorization": f"Bearer {admin_token}"} if admin_token else get_headers(auth=True)
                
                response = requests.delete(
                    f"{config.BACKEND_URL}/files/{file_id}",
                    headers=admin_headers
                )
                if response.status_code in [204, 404]:
                    cleanup_results.append(f"✅ Deleted file {file_id}")
                else:
                    cleanup_results.append(f"❌ Failed to delete file {file_id}: {response.status_code}")
                        
            except Exception as e:
                cleanup_results.append(f"❌ Error deleting file {file_id}: {str(e)}")
        
        # Clean up test bucket (backend)
        if state.test_bucket_id and admin_token:
            try:
                admin_headers = {"apikey": config.API_KEY, "Authorization": f"Bearer {admin_token}"}
                
                # First, get and delete all files in the bucket
                try:
                    files_response = requests.get(
                        f"{config.BACKEND_URL}/buckets/{state.test_bucket_id}/files",
                        headers=admin_headers
                    )
                    if files_response.status_code == 200:
                        bucket_files = files_response.json()
                        for file_info in bucket_files:
                            file_id = file_info.get('id')
                            if file_id:
                                delete_response = requests.delete(
                                    f"{config.BACKEND_URL}/files/{file_id}",
                                    headers=admin_headers
                                )
                                if delete_response.status_code in [204, 404]:
                                    cleanup_results.append(f"✅ Deleted bucket file {file_id}")
                except Exception as e:
                    cleanup_results.append(f"⚠️ Warning cleaning bucket files: {str(e)}")
                
                # Now delete the bucket itself
                response = requests.delete(
                    f"{config.BACKEND_URL}/buckets/{state.test_bucket_id}",
                    headers=admin_headers
                )
                if response.status_code in [200, 204, 404]:
                    cleanup_results.append(f"✅ Deleted backend bucket {state.test_bucket_id}")
                else:
                    cleanup_results.append(f"❌ Failed to delete backend bucket {state.test_bucket_id}: {response.status_code}")
            except Exception as e:
                cleanup_results.append(f"❌ Error deleting backend bucket {state.test_bucket_id}: {str(e)}")
        
        # Clean up storage bucket through backend API
        if state.test_storage_bucket_id and state.test_storage_bucket_name:
            try:
                # Use admin token if available, otherwise use user token
                headers = {"apikey": config.API_KEY, "Authorization": f"Bearer {admin_token}"} if admin_token else get_headers(auth=True)
                
                # First, get and delete all files in the storage bucket
                try:
                    files_response = requests.get(
                        f"{config.BACKEND_URL}/buckets/{state.test_storage_bucket_id}/files",
                        headers=headers
                    )
                    if files_response.status_code == 200:
                        bucket_files = files_response.json()
                        for file_info in bucket_files:
                            file_id = file_info.get('id')
                            if file_id:
                                delete_response = requests.delete(
                                    f"{config.BACKEND_URL}/files/{file_id}",
                                    headers=headers
                                )
                                if delete_response.status_code in [204, 404]:
                                    cleanup_results.append(f"✅ Deleted storage bucket file {file_id}")
                except Exception as e:
                    cleanup_results.append(f"⚠️ Warning cleaning storage bucket files: {str(e)}")
                
                # Delete the bucket through backend API
                response = requests.delete(
                    f"{config.BACKEND_URL}/buckets/{state.test_storage_bucket_id}",
                    headers=headers
                )
                if response.status_code in [200, 204, 404]:
                    cleanup_results.append(f"✅ Deleted storage bucket {state.test_storage_bucket_id} ({state.test_storage_bucket_name})")
                else:
                    cleanup_results.append(f"❌ Failed to delete storage bucket {state.test_storage_bucket_name}: {response.status_code}")
                    if response.status_code == 403:
                        cleanup_results.append("   → Bucket might have remaining files or insufficient permissions")
            except Exception as e:
                cleanup_results.append(f"❌ Error deleting storage bucket {state.test_storage_bucket_name}: {str(e)}")
        
        # Clean up ALL test functions - IMPROVED LOGIC
        # First, list all functions to find any we might have created
        if state.access_token:
            try:
                # Get all functions for the current user
                response = requests.get(
                    f"{config.BACKEND_URL}/functions",
                    headers=get_headers(auth=True)
                )
                if response.status_code == 200:
                    all_functions = response.json()
                    # Find test functions by name pattern or from our tracked list
                    for func in all_functions:
                        func_id = func.get('id')
                        func_name = func.get('name', '')
                        # Delete if it's in our tracked list OR if it matches test pattern
                        if func_id and (func_id in state.created_function_ids or func_name.startswith('test-function-')):
                            try:
                                delete_response = requests.delete(
                                    f"{config.BACKEND_URL}/functions/{func_id}",
                                    headers=get_headers(auth=True)
                                )
                                if delete_response.status_code in [204, 404]:
                                    cleanup_results.append(f"✅ Deleted function {func_id} ({func_name})")
                                else:
                                    cleanup_results.append(f"❌ Failed to delete function {func_id} ({func_name}): {delete_response.status_code}")
                            except Exception as e:
                                cleanup_results.append(f"❌ Error deleting function {func_id} ({func_name}): {str(e)}")
            except Exception as e:
                cleanup_results.append(f"⚠️ Warning: Could not list functions for cleanup: {str(e)}")
        
        # Also try to delete any functions from our tracked list that weren't found above
        for function_id in state.created_function_ids:
            try:
                response = requests.delete(
                    f"{config.BACKEND_URL}/functions/{function_id}",
                    headers=get_headers(auth=True)
                )
                if response.status_code in [204, 404]:
                    cleanup_results.append(f"✅ Deleted tracked function {function_id}")
                elif response.status_code != 403:  # Don't report if already handled above
                    cleanup_results.append(f"❌ Failed to delete tracked function {function_id}: {response.status_code}")
            except Exception as e:
                cleanup_results.append(f"❌ Error deleting tracked function {function_id}: {str(e)}")

        # Wait a moment to ensure all deletions are processed
        import time
        time.sleep(2)

        # ------------------------------------------------------------
        # NEW: Clean up any extra users created during tests
        # ------------------------------------------------------------
        extra_user_ids = getattr(state, "created_user_ids", [])
        if extra_user_ids and admin_token:
            admin_headers = {"apikey": config.API_KEY, "Authorization": f"Bearer {admin_token}"}
            for uid in extra_user_ids:
                try:
                    resp = requests.delete(f"{config.BACKEND_URL}/users/{uid}",
                                           headers=admin_headers)
                    if resp.status_code in [200, 204, 404]:
                        cleanup_results.append(f"✅ Deleted extra test user {uid}")
                    else:
                        cleanup_results.append(f"❌ Failed to delete extra test user {uid}: {resp.status_code}")
                except Exception as e:
                    cleanup_results.append(f"❌ Error deleting extra test user {uid}: {str(e)}")
        elif extra_user_ids and not admin_token:
            cleanup_results.append("⚠️  Extra test users present but no admin token to delete them")
        
         # Clean up test user if admin token is available - this must be done last
        if state.test_email and admin_token and state.user_id:
            try:
                admin_headers = {"apikey": config.API_KEY, "Authorization": f"Bearer {admin_token}"}
                
                # First check if user still has resources
                user_functions_response = requests.get(
                    f"{config.BACKEND_URL}/functions",
                    headers={"apikey": config.API_KEY, "Authorization": f"Bearer {state.access_token}"}
                )
                if user_functions_response.status_code == 200:
                    remaining_functions = user_functions_response.json()
                    if remaining_functions:
                        cleanup_results.append(f"⚠️ User still has {len(remaining_functions)} functions - attempting force delete")
                        # Try to delete with admin token
                        for func in remaining_functions:
                            func_id = func.get('id')
                            if func_id:
                                try:
                                    requests.delete(
                                        f"{config.BACKEND_URL}/functions/{func_id}",
                                        headers=admin_headers
                                    )
                                except:
                                    pass
                
                # Now try to delete the user
                response = requests.delete(
                    f"{config.BACKEND_URL}/users/{state.user_id}",
                    headers=admin_headers
                )
                if response.status_code in [200, 204, 404]:
                    cleanup_results.append(f"✅ Deleted test user {state.test_email}")
                else:
                    cleanup_results.append(f"❌ Failed to delete test user {state.test_email}: {response.status_code}")
                    # Try to get more info about why it failed
                    if response.status_code == 409:
                        cleanup_results.append("   → User still has dependent resources")
            except Exception as e:
                cleanup_results.append(f"❌ Error deleting test user {state.test_email}: {str(e)}")
        elif state.test_email and not admin_token:
            cleanup_results.append(f"❌ Cannot delete test user {state.test_email}: No admin token")
        
    except Exception as e:
        cleanup_results.append(f"❌ Unexpected error during cleanup: {str(e)}")
    
    write_to_file("\n--- Cleanup Operation Log ---")
    
    for result in cleanup_results:
        write_to_file(result)
    
    if cleanup_results:
        write_to_file(f"\n🧹 Cleanup completed with {len(cleanup_results)} operations")
    else:
        write_to_file("🧹 No resources to clean up")

# ----------------------- Test Summary Helpers ----------------------------

def _crud_sort_key(desc: str) -> int:
    """Sort key for ordering endpoints by CRUD operation."""
    d = desc.lower()
    if d.startswith(("create", "insert", "initiate", "save", "generate", "upload", "ensure")):
        return 0   # Create
    if d.startswith(("get", "list", "fetch", "download", "view", "backend", "storage", "execute")):
        return 1   # Read
    if d.startswith("update"):
        return 2   # Update
    if d.startswith("delete"):
        return 3   # Delete
    if d.startswith("real-time"):
        return 5   # Real-time tests go at the end
    return 4       # Others

def generate_test_summary():
    """Generate and write the final test summary."""
    write_to_file(f"\n{'=' * 60}")
    write_to_file("🏁 API Testing Complete!")
    write_to_file('=' * 60)
    
    # Write summary
    write_to_file("\n📊 TEST SUMMARY")
    write_to_file("=" * 60)
    write_to_file(f"Total Tests: {state.test_summary['total']}")
    write_to_file(f"Passed: {state.test_summary['passed']} ✅")
    write_to_file(f"Failed: {state.test_summary['failed']} ❌")
    write_to_file(f"Success Rate: {(state.test_summary['passed'] / state.test_summary['total'] * 100) if state.test_summary['total'] > 0 else 0:.1f}%")
    
    if state.test_summary["errors"]:
        write_to_file("\n❌ FAILED TESTS:")
        for error in state.test_summary["errors"]:
            write_to_file(f"  - {error['description']}: Status {error['status_code']} at {error['url']}")
    
    if state.access_token:
        write_to_file("\n✅ Authentication successful - all authenticated endpoints tested")
    else:
        write_to_file("\n⚠️ Authentication failed - only public endpoints tested")
    
    # Add WebSocket service summary
    write_to_file(f"\n📡 REAL-TIME SERVICE SUMMARY")
    write_to_file("=" * 60)
    if state.access_token and state.websocket_notifications:
        write_to_file(f"WebSocket Connection: ✅ Successful")
        write_to_file(f"Total Notifications: {len(state.websocket_notifications)}")
        write_to_file(f"Unique Channels: {len(set(n['notification'].get('subscription_id', '') for n in state.websocket_notifications))}")
        write_to_file(f"Real-time Coverage: {'✅ Complete' if len(state.websocket_notifications) >= 5 else '⚠️ Incomplete'}")
    elif state.access_token:
        write_to_file(f"WebSocket Connection: ❌ Failed or No Notifications")
        write_to_file(f"This indicates potential issues with the real-time service")
    else:
        write_to_file(f"WebSocket Testing: ⚠️ Skipped (No Authentication)")
    
    write_to_file("\nFor full testing:")
    write_to_file("1. Ensure SelfDB backend is running on localhost:8000")
    write_to_file("2. Ensure SelfDB storage service is running on localhost:8001")
    write_to_file("3. Update TEST_EMAIL and TEST_PASSWORD if needed")
    write_to_file("4. Ensure database is accessible and configured")
    
    # List passing endpoints in CRUD order
    if state.test_summary["passed_tests"]:
        write_to_file("\n✅ PASSED ENDPOINTS (CRUD order):")
        for ep in sorted(state.test_summary["passed_tests"], key=_crud_sort_key):
            write_to_file(f"  - {ep}")

# ----------------------- Authentication Helper ----------------------------

def ensure_authentication():
    """Ensure we have a valid authentication token."""
    if state.access_token:
        return True
    
    import time
    from . import config
    
    timestamp = str(int(time.time()))
    test_email = f"{config.TEST_EMAIL_BASE}_{timestamp}@example.com"
    
    try:
        # Register
        register_data = {
            "email": test_email,
            "password": config.TEST_PASSWORD,
            "full_name": "Test User"
        }
        response = requests.post(
            f"{config.BACKEND_URL}/auth/register",
            headers={**get_headers(), "Content-Type": "application/json"},
            json=register_data
        )
        
        if response.status_code != 200:
            write_to_file(f"❌ Failed to register test user: {response.status_code}")
            return False
        
        # Login
        login_data = f"username={test_email}&password={config.TEST_PASSWORD}"
        response = requests.post(
            f"{config.BACKEND_URL}/auth/login",
            headers={**get_headers(), "Content-Type": "application/x-www-form-urlencoded"},
            data=login_data
        )
        
        if response.status_code == 200:
            login_result = response.json()
            state.access_token = login_result.get("access_token")
            state.user_id = login_result.get("user_id")
            state.test_email = test_email
            write_to_file(f"✅ Authentication successful! Token acquired for {test_email}")
            return True
        else:
            write_to_file(f"❌ Failed to login: {response.status_code}")
            return False
            
    except Exception as e:
        write_to_file(f"❌ Error during authentication: {e}")
        return False
