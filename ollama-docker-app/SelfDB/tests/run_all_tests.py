#!/usr/bin/env python3
"""
Universal test runner for SelfDB API test suite.

This script runs all test modules in the correct sequence, managing shared state
and generating a comprehensive test report.

Usage:
    python run_all_tests.py
    
Environment Variables:
    BACKEND_URL  - Backend API URL (default: https://api.selfdb.io/api/v1)
    STORAGE_URL  - Storage service URL (default: https://storage.selfdb.io)
    API_KEY      - Anonymous API key (default: hardcoded test key)
"""

import sys
import os

# Add the parent directory to the path so we can import test modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import config, state, helpers

# Import all test modules
import test_01_health
import test_02_auth
import test_03_users
import test_04_buckets
import test_05_files
import test_06_tables
import test_07_sql
import test_08_functions
import test_09_cors
import test_10_storage
import test_11_errors
import test_12_realtime

def main():
    """Main test runner"""
    # Initialize results file
    filename = helpers.init_results_file()
    
    try:
        # Get admin token early for WebSocket monitoring
        state.admin_access_token = helpers.get_admin_token()
        if state.admin_access_token:
            helpers.write_to_file("\n📡 Starting WebSocket monitoring (admin)…")
            helpers.start_websocket_monitoring(token_override=state.admin_access_token)
        
        # Run tests in sequence
        test_01_health.run()
        test_02_auth.run()
        
        # Start WebSocket monitoring with user token if not started with admin
        if not state.websocket_connection and state.access_token:
            helpers.write_to_file("\n📡 Starting WebSocket monitoring (test user)…")
            helpers.start_websocket_monitoring()
        
        # Continue with remaining tests
        test_03_users.run()
        test_04_buckets.run()
        test_05_files.run()
        test_06_tables.run()
        test_07_sql.run()
        test_08_functions.run()
        test_09_cors.run()
        test_10_storage.run()
        test_11_errors.run()
        test_12_realtime.run()
        
        # Generate WebSocket summary before cleanup
        helpers.generate_websocket_summary()
        
        # Clean up test resources
        helpers.cleanup_test_resources()
        
    finally:
        # Clean up WebSocket connection
        helpers.cleanup_websocket()
        
        # Generate final test summary
        helpers.generate_test_summary()
        
        # Close results file
        helpers.close_results_file()
        
        print(f"\n📄 Test results saved to: {filename}")

if __name__ == "__main__":
    main()
