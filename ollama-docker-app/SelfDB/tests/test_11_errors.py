"""
Test error conditions and edge cases for SelfDB.
"""

import requests
from common import config, state, helpers

def test_error_conditions():
    """Test error conditions and edge cases"""
    helpers.print_test_header("Error Conditions and Edge Cases")
    
    try:
        # Test invalid endpoint (expect 404)
        response = requests.get(f"{config.BACKEND_URL}/nonexistent", headers=helpers.get_headers())
        helpers.print_response(response, "Invalid Endpoint (Should be 404)", expected_status=404)
        
        # Test missing anon key (expect 401)
        response = requests.get(f"{config.BACKEND_URL}/health")
        helpers.print_response(response, "Missing Anon Key (Should be 401)", expected_status=401)
        
        # Test invalid anon key (expect 401)
        response = requests.get(f"{config.BACKEND_URL}/health", headers={"apikey": "invalid_key"})
        helpers.print_response(response, "Invalid Anon Key (Should be 401)", expected_status=401)
        
        # Test unauthorized access to protected endpoint (expect 401)
        response = requests.get(f"{config.BACKEND_URL}/users/me", headers=helpers.get_headers())
        helpers.print_response(response, "Unauthorized Access (Should be 401)", expected_status=401)
        
        # Test invalid JSON in request body (expect 422)
        response = requests.post(
            f"{config.BACKEND_URL}/auth/register",
            headers={**helpers.get_headers(), "Content-Type": "application/json"},
            data="invalid json"
        )
        helpers.print_response(response, "Invalid JSON (Should be 422)", expected_status=422)
        
        # Test storage service error conditions
        # Test access to non-existent bucket (expect 404)
        response = requests.get(f"{config.STORAGE_URL}/buckets/nonexistent-bucket", headers=helpers.get_headers())
        helpers.print_response(response, "Non-existent Storage Bucket (Should be 404)", expected_status=404)
        
        # Test file access in non-existent bucket (expect 404)
        response = requests.get(f"{config.STORAGE_URL}/files/list/nonexistent-bucket", headers=helpers.get_headers())
        helpers.print_response(response, "List Files in Non-existent Bucket (Should be 404)", expected_status=404)
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing error conditions: {e}")

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    helpers.print_test_header("Edge Cases and Boundary Conditions")
    
    if not state.access_token:
        print("❌ Skipping edge case tests - no authentication token")
        return
    
    try:
        # Test SQL query with empty query
        empty_query_data = {"query": ""}
        response = requests.post(
            f"{config.BACKEND_URL}/sql/query",
            headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
            json=empty_query_data
        )
        helpers.print_response(response, "Empty SQL Query")
        
        
        # Test bucket creation with invalid name
        invalid_bucket_data = {
            "name": "",
            "is_public": True,
            "description": "Invalid bucket test"
        }
        response = requests.post(
            f"{config.BACKEND_URL}/buckets",
            headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
            json=invalid_bucket_data
        )
        helpers.print_response(response, "Create Bucket with Empty Name", expected_status=400)
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing edge cases: {e}")

def test_function_errors():
    """Test error cases for function operations"""
    helpers.print_test_header("Function Error Cases")
    
    if not state.access_token:
        print("❌ Skipping function error tests - no authentication token")
        return
    
    try:
        # Create function for testing
        function_data = {
            "name": "empty-function",
            "code": "",  # Empty code
            "description": "Empty function test"
        }
        response = requests.post(
            f"{config.BACKEND_URL}/functions",
            headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
            json=function_data
        )
        
        if response.status_code == 201:
            function_id = response.json().get("id")
            state.add_created_function(function_id)
            helpers.print_response(response, "Create Function with Empty Code", expected_status=201)
        else:
            helpers.print_response(response, "Create Function with Empty Code (validation may have failed)")
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing function errors: {e}")

def run():
    """Run error and edge case tests"""
    test_error_conditions()
    test_edge_cases()
    test_function_errors()

if __name__ == "__main__":
    # When run independently
    helpers.init_results_file()
    
    # For edge cases, ensure we have authentication
    if not state.access_token:
        helpers.ensure_authentication()
    
    run()
    helpers.generate_test_summary()
    helpers.close_results_file()
    print(f"\n📄 Test results saved to: {helpers.state.results_filename}")
