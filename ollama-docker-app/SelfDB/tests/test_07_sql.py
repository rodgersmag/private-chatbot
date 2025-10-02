"""
Test SQL execution endpoints for SelfDB.
"""

import requests
from common import config, state, helpers

def test_sql_execution():
    """Test SQL execution endpoints"""
    helpers.print_test_header("SQL Execution")
    
    if not state.access_token:
        print("❌ Skipping SQL tests - no authentication token")
        return
    
    try:
        # Execute SQL query
        query_data = {
            "query": "SELECT COUNT(*) as user_count FROM users;"
        }
        response = requests.post(
            f"{config.BACKEND_URL}/sql/query",
            headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
            json=query_data
        )
        helpers.print_response(response, "Execute SQL Query")
        
        # Get SQL snippets
        response = requests.get(f"{config.BACKEND_URL}/sql/snippets", headers=helpers.get_headers(auth=True))
        helpers.print_response(response, "Get SQL Snippets")
        
        # Save SQL snippet
        snippet_data = {
            "name": "Count Users",
            "sql_code": "SELECT COUNT(*) as user_count FROM users;",
            "description": "Count total users",
            "is_shared": False
        }
        response = requests.post(
            f"{config.BACKEND_URL}/sql/snippets",
            headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
            json=snippet_data
        )
        helpers.print_response(response, "Save SQL Snippet")
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing SQL execution: {e}")

def test_schema_endpoints():
    """Test schema information endpoints"""
    helpers.print_test_header("Schema Information")
    
    if not state.access_token:
        print("❌ Skipping schema tests - no authentication token")
        return
    
    try:
        # Get database schema
        response = requests.get(f"{config.BACKEND_URL}/schema", headers=helpers.get_headers(auth=True))
        helpers.print_response(response, "Get Database Schema")
        
        # Get schema visualization
        response = requests.get(f"{config.BACKEND_URL}/schema/visualization", headers=helpers.get_headers(auth=True))
        helpers.print_response(response, "Get Schema Visualization")
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing schema endpoints: {e}")

def run():
    """Run SQL and schema tests"""
    test_sql_execution()
    test_schema_endpoints()

if __name__ == "__main__":
    # When run independently
    helpers.init_results_file()
    
    # Ensure we have authentication
    if not state.access_token:
        helpers.ensure_authentication()
    
    run()
    helpers.generate_test_summary()
    helpers.close_results_file()
    print(f"\n📄 Test results saved to: {helpers.state.results_filename}")
