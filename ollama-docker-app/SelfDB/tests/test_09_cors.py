"""
Test CORS management endpoints for SelfDB.
"""

import time
import requests
from common import config, state, helpers

def test_cors_management():
    """Test CORS management endpoints"""
    helpers.print_test_header("CORS Management")
    
    # Get admin token for superuser operations
    admin_token = helpers.get_admin_token()
    
    if not admin_token:
        print("❌ Skipping CORS tests - unable to authenticate as admin/superuser")
        # Still test that regular users get proper 403/401 responses
        if state.access_token:
            response = requests.get(f"{config.BACKEND_URL}/cors/origins/", headers=helpers.get_headers(auth=True))
            helpers.print_response(response, "List CORS Origins (Regular User)", expected_status=403)
        return
    
    # Use admin headers for all CORS operations
    admin_headers = {"apikey": config.API_KEY, "Authorization": f"Bearer {admin_token}"}
    
    try:
        # List CORS origins
        response = requests.get(f"{config.BACKEND_URL}/cors/origins/", headers=admin_headers)
        helpers.print_response(response, "List CORS Origins")
        
        # Test CORS origin validation
        response = requests.post(
            f"{config.BACKEND_URL}/cors/origins/validate",
            headers=admin_headers,
            params={"origin": "https://example.com"}
        )
        helpers.print_response(response, "Validate CORS Origin")
        
        # Test refresh CORS cache
        response = requests.post(f"{config.BACKEND_URL}/cors/origins/refresh-cache", headers=admin_headers)
        helpers.print_response(response, "Refresh CORS Cache")
        
        # Create a UNIQUE CORS origin
        timestamp = str(int(time.time()))
        unique_origin_url = f"https://test-origin-{timestamp}.example.com"
        cors_data = {
            "origin": unique_origin_url,
            "description": "Test CORS origin for API testing"
        }
        response = requests.post(
            f"{config.BACKEND_URL}/cors/origins/",
            headers={**admin_headers, "Content-Type": "application/json"},
            json=cors_data
        )
        helpers.print_response(response, "Create CORS Origin")
        
        cors_id = None
        if response.status_code == 201:
            cors_id = response.json().get("id")

            # Test creating the SAME origin again (should fail with 409)
            response = requests.post(
                f"{config.BACKEND_URL}/cors/origins/",
                headers={**admin_headers, "Content-Type": "application/json"},
                json=cors_data
            )
            helpers.print_response(response, "Create Duplicate CORS Origin", expected_status=409)
            
            # Test getting the specific CORS origin
            response = requests.get(f"{config.BACKEND_URL}/cors/origins/{cors_id}", headers=admin_headers)
            helpers.print_response(response, "Get CORS Origin")
            
            # Test updating the CORS origin
            update_data = {"description": "Updated test CORS origin"}
            response = requests.put(
                f"{config.BACKEND_URL}/cors/origins/{cors_id}",
                headers={**admin_headers, "Content-Type": "application/json"},
                json=update_data
            )
            helpers.print_response(response, "Update CORS Origin")
            
            # Test soft delete
            response = requests.delete(f"{config.BACKEND_URL}/cors/origins/{cors_id}", headers=admin_headers)
            helpers.print_response(response, "Delete CORS Origin (Soft)")
            
            # List origins including inactive ones
            response = requests.get(
                f"{config.BACKEND_URL}/cors/origins/?active_only=false", 
                headers=admin_headers
            )
            helpers.print_response(response, "List CORS Origins (Including Inactive)")
            
            # Test hard delete
            response = requests.delete(
                f"{config.BACKEND_URL}/cors/origins/{cors_id}?hard_delete=true", 
                headers=admin_headers
            )
            helpers.print_response(response, "Delete CORS Origin (Hard)")
        
        # Test validation with invalid origin
        response = requests.post(
            f"{config.BACKEND_URL}/cors/origins/validate",
            headers=admin_headers,
            params={"origin": "not-a-valid-url"}
        )
        helpers.print_response(response, "Validate Invalid CORS Origin")
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing CORS management: {e}")

def run():
    """Run CORS tests"""
    test_cors_management()

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
