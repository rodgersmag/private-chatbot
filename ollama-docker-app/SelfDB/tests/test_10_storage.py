"""
Test storage service endpoints for SelfDB.
"""

import time
import requests
from common import config, state, helpers

def test_storage_service():
    """Test storage service endpoints through backend integration"""
    helpers.print_test_header("Storage Service Integration")
    
    # Generate unique storage bucket name
    timestamp = str(int(time.time()))
    test_bucket_name = f"test-storage-bucket-{timestamp}"
    
    try:
        if not state.access_token:
            print("⚠️ Skipping storage tests - no authentication token")
            return
        
        # Step 1: Create bucket through backend API (source of truth)
        bucket_data = {
            "name": test_bucket_name,
            "is_public": True,
            "description": "Test bucket for storage service integration"
        }
        response = requests.post(
            f"{config.BACKEND_URL}/buckets",
            headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
            json=bucket_data
        )
        helpers.print_response(response, "Create Bucket via Backend")
        
        if response.status_code == 201:
            bucket_info = response.json()
            bucket_id = bucket_info["id"]
            state.test_storage_bucket_id = bucket_id
            state.test_storage_bucket_name = test_bucket_name
            
            # Verify bucket exists in storage service by listing files through backend
            response = requests.get(
                f"{config.BACKEND_URL}/buckets/{bucket_id}/files",
                headers=helpers.get_headers(auth=True)
            )
            helpers.print_response(response, "List Files in New Bucket via Backend")
            
            # Step 2: Initiate file upload through backend API
            test_filename = f"test-file-{timestamp}.txt"
            upload_data = {
                "filename": test_filename,
                "content_type": "text/plain",
                "size": 54,  # Length of our test content
                "bucket_id": bucket_id
            }
            response = requests.post(
                f"{config.BACKEND_URL}/files/initiate-upload",
                headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
                json=upload_data
            )
            helpers.print_response(response, "Initiate File Upload via Backend")
            
            if response.status_code == 201:
                upload_result = response.json()
                file_id = upload_result["file_metadata"]["id"]
                state.add_created_file(file_id)
                upload_url = upload_result["presigned_upload_info"]["upload_url"]
                
                # Step 3: Upload file directly to storage service using presigned URL
                test_content = f"This is test content for storage service - {timestamp}."
                upload_response = requests.put(
                    upload_url,
                    headers={"Content-Type": "text/plain"},
                    data=test_content
                )
                helpers.print_response(upload_response, "Direct Upload to Storage Service")
                
                # Step 4: Get download info from backend
                response = requests.get(
                    f"{config.BACKEND_URL}/files/{file_id}/download-info",
                    headers=helpers.get_headers(auth=True)
                )
                helpers.print_response(response, "Get File Download Info via Backend")
                
                if response.status_code == 200:
                    download_info = response.json()
                    download_url = download_info["download_url"]
                    
                    # Step 5: Download file directly from storage service
                    download_response = requests.get(download_url)
                    helpers.print_response(download_response, "Direct Download from Storage Service")
                
                # Step 6: Get view info from backend
                response = requests.get(
                    f"{config.BACKEND_URL}/files/{file_id}/view-info",
                    headers=helpers.get_headers(auth=True)
                )
                helpers.print_response(response, "Get File View Info via Backend")
                
                if response.status_code == 200:
                    view_info = response.json()
                    view_url = view_info["view_url"]
                    
                    # Step 7: View file directly from storage service
                    view_response = requests.get(view_url)
                    helpers.print_response(view_response, "Direct View from Storage Service")
                
                # Step 8: Test public file access (if bucket is public)
                if bucket_info.get("is_public"):
                    response = requests.get(
                        f"{config.BACKEND_URL}/files/public/{file_id}/download-info",
                        headers=helpers.get_headers()  # No auth
                    )
                    helpers.print_response(response, "Get Public File Download Info")
                    
                    if response.status_code == 200:
                        public_download_info = response.json()
                        public_download_url = public_download_info["download_url"]
                        
                        # Download via public URL
                        public_download_response = requests.get(public_download_url)
                        helpers.print_response(public_download_response, "Public Download from Storage Service")
                    
                    response = requests.get(
                        f"{config.BACKEND_URL}/files/public/{file_id}/view-info",
                        headers=helpers.get_headers()  # No auth
                    )
                    helpers.print_response(response, "Get Public File View Info")
                    
                    if response.status_code == 200:
                        public_view_info = response.json()
                        public_view_url = public_view_info["view_url"]
                        
                        # View via public URL
                        public_view_response = requests.get(public_view_url)
                        helpers.print_response(public_view_response, "Public View from Storage Service")
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing storage service integration: {e}")

def test_additional_storage_endpoints():
    """Test additional storage service integration scenarios"""
    helpers.print_test_header("Additional Storage Service Integration")
    
    if not state.access_token or not state.test_storage_bucket_id:
        print("❌ Skipping additional storage tests - no authentication token or test bucket")
        return
    
    try:
        timestamp = str(int(time.time()))
        
        # Test multiple file upload scenario
        for i in range(2):
            filename = f"multi-upload-{timestamp}-{i}.txt"
            content = f"Multiple file test content {i} - {timestamp}"
            
            # Initiate upload through backend
            upload_data = {
                "filename": filename,
                "content_type": "text/plain",
                "size": len(content),
                "bucket_id": state.test_storage_bucket_id
            }
            response = requests.post(
                f"{config.BACKEND_URL}/files/initiate-upload",
                headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
                json=upload_data
            )
            helpers.print_response(response, f"Initiate Multi-File Upload {i+1}")
            
            if response.status_code == 201:
                upload_result = response.json()
                file_id = upload_result["file_metadata"]["id"]
                state.add_created_file(file_id)
                upload_url = upload_result["presigned_upload_info"]["upload_url"]
                
                # Upload to storage service
                upload_response = requests.put(
                    upload_url,
                    headers={"Content-Type": "text/plain"},
                    data=content
                )
                helpers.print_response(upload_response, f"Upload Multi-File {i+1} to Storage")
        
        # List files in bucket through backend
        response = requests.get(
            f"{config.BACKEND_URL}/buckets/{state.test_storage_bucket_id}/files",
            headers=helpers.get_headers(auth=True)
        )
        helpers.print_response(response, "List Files in Bucket via Backend")
        
        # Test file deletion through backend
        if state.created_file_ids:
            file_id_to_delete = state.created_file_ids[-1]
            response = requests.delete(
                f"{config.BACKEND_URL}/files/{file_id_to_delete}",
                headers=helpers.get_headers(auth=True)
            )
            helpers.print_response(response, "Delete File via Backend")
            
            if response.status_code == 204:
                state.created_file_ids.remove(file_id_to_delete)
        
        # Update bucket through backend
        update_data = {
            "description": "Updated test storage bucket description",
            "is_public": True
        }
        response = requests.put(
            f"{config.BACKEND_URL}/buckets/{state.test_storage_bucket_id}",
            headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
            json=update_data
        )
        helpers.print_response(response, "Update Bucket via Backend")
        
        # Get bucket info with stats
        response = requests.get(
            f"{config.BACKEND_URL}/buckets/{state.test_storage_bucket_id}",
            headers=helpers.get_headers(auth=True)
        )
        helpers.print_response(response, "Get Bucket with Stats via Backend")
        
        # Test anonymous access to public bucket
        if state.test_storage_bucket_name:
            # Get bucket info with anon key
            response = requests.get(
                f"{config.BACKEND_URL}/buckets/{state.test_storage_bucket_id}",
                headers=helpers.get_headers()  # Uses anon key
            )
            helpers.print_response(response, "Get Public Bucket Info (Anonymous)")
            
            # List files in public bucket with anon key
            response = requests.get(
                f"{config.BACKEND_URL}/buckets/{state.test_storage_bucket_id}/files",
                headers=helpers.get_headers()  # Uses anon key
            )
            helpers.print_response(response, "List Files in Public Bucket (Anonymous)")
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing additional storage integration: {e}")

def run():
    """Run storage tests"""
    test_storage_service()
    test_additional_storage_endpoints()

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
