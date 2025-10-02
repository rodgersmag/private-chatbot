"""
Test bucket management endpoints for SelfDB.
"""

import time
import requests
from common import config, state, helpers

def test_bucket_management():
    """Test bucket management endpoints"""
    helpers.print_test_header("Bucket Management")
    
    # Generate unique bucket name for this test run
    timestamp = str(int(time.time()))
    test_bucket_name = f"test-bucket-{timestamp}"
    
    try:
        # List buckets
        if state.access_token:
            response = requests.get(f"{config.BACKEND_URL}/buckets", headers=helpers.get_headers(auth=True))
            helpers.print_response(response, "List Buckets (Authenticated)")
        else:
            response = requests.get(f"{config.BACKEND_URL}/buckets", headers=helpers.get_headers())
            helpers.print_response(response, "List Buckets (Anonymous)")
        
        if not state.access_token:
            print("⚠️ Skipping authenticated bucket tests - no token")
            return
        
        # Create bucket with unique name
        bucket_data = {
            "name": test_bucket_name,
            "is_public": True,
            "description": "Test bucket for API testing"
        }
        response = requests.post(
            f"{config.BACKEND_URL}/buckets",
            headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
            json=bucket_data
        )
        helpers.print_response(response, "Create Bucket")
        
        if response.status_code == 201:
            state.test_bucket_id = response.json().get("id")
            state.test_bucket_name = test_bucket_name
            
            # Get bucket details
            response = requests.get(f"{config.BACKEND_URL}/buckets/{state.test_bucket_id}", headers=helpers.get_headers(auth=True))
            helpers.print_response(response, "Get Bucket Details")
            
            # List bucket files
            response = requests.get(f"{config.BACKEND_URL}/buckets/{state.test_bucket_id}/files", headers=helpers.get_headers(auth=True))
            helpers.print_response(response, "List Bucket Files")
            
            # Update bucket
            update_data = {"description": "Updated test bucket"}
            response = requests.put(
                f"{config.BACKEND_URL}/buckets/{state.test_bucket_id}",
                headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
                json=update_data
            )
            helpers.print_response(response, "Update Bucket")
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing bucket management: {e}")

def run():
    """Run bucket management tests"""
    test_bucket_management()

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
