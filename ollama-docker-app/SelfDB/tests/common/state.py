"""
Shared state management for SelfDB test suite.
This module manages dynamic variables that are generated and shared during test runs.
"""

import threading
from typing import Optional, List
import asyncio

# Thread-safe state management
_lock = threading.Lock()

# Authentication state
access_token: Optional[str] = None
admin_access_token: Optional[str] = None
user_id: Optional[str] = None
test_email: Optional[str] = None

# Test resource tracking
test_bucket_id: Optional[str] = None
test_bucket_name: Optional[str] = None
test_storage_bucket_name: Optional[str] = None
created_function_ids: List[str] = []
created_file_ids: List[str] = []

# WebSocket state
websocket_notifications = []
websocket_connection = None
websocket_thread = None
websocket_loop: Optional[asyncio.AbstractEventLoop] = None

# Test results tracking
test_summary = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": [],
    "passed_tests": []
}

# File logging
results_file = None
results_filename: Optional[str] = None

def reset_state():
    """Reset all state variables to initial values."""
    global access_token, admin_access_token, user_id, test_email
    global test_bucket_id, test_bucket_name, test_storage_bucket_name
    global created_function_ids, created_file_ids
    global websocket_notifications, websocket_connection, websocket_thread, websocket_loop
    global test_summary, results_file, results_filename
    
    with _lock:
        access_token = None
        admin_access_token = None
        user_id = None
        test_email = None
        
        test_bucket_id = None
        test_bucket_name = None
        test_storage_bucket_name = None
        created_function_ids = []
        created_file_ids = []
        
        websocket_notifications = []
        websocket_connection = None
        websocket_thread = None
        websocket_loop = None
        
        test_summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "passed_tests": []
        }
        
        if results_file:
            results_file.close()
        results_file = None
        results_filename = None

def get_auth_token() -> Optional[str]:
    """Get the current authentication token."""
    return access_token

def set_auth_token(token: str):
    """Set the authentication token."""
    global access_token
    with _lock:
        access_token = token

def add_created_file(file_id: str):
    """Add a file ID to the cleanup list."""
    with _lock:
        created_file_ids.append(file_id)

def add_created_function(function_id: str):
    """Add a function ID to the cleanup list."""
    with _lock:
        created_function_ids.append(function_id)
