"""
Test file management endpoints for SelfDB.
"""

import time
import requests
from common import config, state, helpers

def test_file_management():
    """Test file management endpoints"""
    helpers.print_test_header("File Management")
    
    if not state.access_token:
        print("❌ Skipping file tests - no authentication token")
        return
    
    try:
        # List user files
        response = requests.get(f"{config.BACKEND_URL}/files", headers=helpers.get_headers(auth=True))
        helpers.print_response(response, "List User Files")
        
        # First, ensure we have a bucket by creating one through the backend
        bucket_id = state.test_bucket_id
        if not bucket_id:
            # Create a bucket through backend for file testing
            timestamp = str(int(time.time()))
            bucket_data = {
                "name": f"test-file-bucket-{timestamp}",
                "is_public": True,
                "description": "Test bucket for file management"
            }
            response = requests.post(
                f"{config.BACKEND_URL}/buckets",
                headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
                json=bucket_data
            )
            helpers.print_response(response, "Create Bucket for File Tests")
            
            if response.status_code == 201:
                bucket_info = response.json()
                bucket_id = bucket_info["id"]
                state.test_bucket_id = bucket_id
                state.test_bucket_name = bucket_info["name"]
        
        if bucket_id:
            # Initiate file upload through backend
            upload_data = {
                "filename": "test-document.txt",
                "content_type": "text/plain",
                "size": 24,  # Corrected size for "This is a test document."
                "bucket_id": bucket_id
            }
            response = requests.post(
                f"{config.BACKEND_URL}/files/initiate-upload",
                headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
                json=upload_data
            )
            helpers.print_response(response, "Initiate File Upload")
            
            if response.status_code == 201:
                upload_result = response.json()
                file_id = upload_result["file_metadata"]["id"]
                state.add_created_file(file_id)
                upload_url = upload_result["presigned_upload_info"]["upload_url"]
                
                # Upload file directly to storage service using presigned URL
                test_content = b"This is a test document."
                upload_response = requests.put(
                    upload_url,
                    headers={"Content-Type": "text/plain"},
                    data=test_content
                )
                helpers.print_response(upload_response, "Upload File to Storage Service")
                
                # Get file download info from backend
                response = requests.get(
                    f"{config.BACKEND_URL}/files/{file_id}/download-info",
                    headers=helpers.get_headers(auth=True)
                )
                helpers.print_response(response, "Get File Download Info")
                
                if response.status_code == 200:
                    download_info = response.json()
                    download_url = download_info["download_url"]
                    
                    # Download file directly from storage service
                    download_response = requests.get(download_url)
                    helpers.print_response(download_response, "Download File from Storage Service")
                
                # Get file view info from backend
                response = requests.get(
                    f"{config.BACKEND_URL}/files/{file_id}/view-info",
                    headers=helpers.get_headers(auth=True)
                )
                helpers.print_response(response, "Get File View Info")
                
                if response.status_code == 200:
                    view_info = response.json()
                    view_url = view_info["view_url"]
                    
                    # View file directly from storage service
                    view_response = requests.get(view_url)
                    helpers.print_response(view_response, "View File from Storage Service")
                
                # Test public file access endpoints (if bucket is public)
                response = requests.get(
                    f"{config.BACKEND_URL}/files/public/{file_id}/download-info",
                    headers=helpers.get_headers()
                )
                helpers.print_response(response, "Get Public File Download Info")
                
                response = requests.get(
                    f"{config.BACKEND_URL}/files/public/{file_id}/view-info",
                    headers=helpers.get_headers()
                )
                helpers.print_response(response, "Get Public File View Info")
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing file management: {e}")

def run():
    """Run file management tests"""
    test_file_management()

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
