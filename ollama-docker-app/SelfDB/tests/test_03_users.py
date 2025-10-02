"""
Test user management endpoints for SelfDB.
"""

import requests
from common import config, state, helpers
import time

def test_user_management():
    """Test user management endpoints"""
    helpers.print_test_header("User Management")
    
    if not state.access_token:
        print("❌ Skipping user tests - no authentication token")
        return
    
    try:
        user_headers = helpers.get_headers(auth=True)

        # -------------------- CURRENT USER ENDPOINTS --------------------
        # Get current user
        response = requests.get(f"{config.BACKEND_URL}/users/me", headers=user_headers)
        helpers.print_response(response, "Get Current User")
        current_user_json = response.json() if response.status_code == 200 else {}

        # Update own user
        update_self = {"full_name": "Test User Updated"}
        response = requests.put(
            f"{config.BACKEND_URL}/users/me", headers=user_headers, json=update_self
        )
        helpers.print_response(response, "Update Current User")

        # Change own password
        pwd_payload = {
            "current_password": config.TEST_PASSWORD,
            "new_password": f"{config.TEST_PASSWORD}new"
        }
        response = requests.put(
            f"{config.BACKEND_URL}/users/me/password",
            headers=user_headers,
            json=pwd_payload
        )
        helpers.print_response(response, "Change Current User Password")

        # Get user count
        response = requests.get(f"{config.BACKEND_URL}/users/count", headers=user_headers)
        helpers.print_response(response, "Get User Count")
        
        # Get anon key
        response = requests.get(f"{config.BACKEND_URL}/users/me/anon-key", headers=user_headers)
        helpers.print_response(response, "Get Anonymous Key")
        
        # List active users (non-superusers)
        response = requests.get(f"{config.BACKEND_URL}/users/list", headers=user_headers)
        helpers.print_response(response, "List Active Users")
        
        # -------------------- ADMIN / SUPERUSER ENDPOINTS --------------------
        admin_token = helpers.get_admin_token()
        if not admin_token:
            print("⚠️  Skipping admin-level user tests - no admin token")
            return
        admin_headers = helpers.get_headers(admin=True)

        # List all users (superuser)
        # NOTE: endpoint requires trailing slash, otherwise 405 Method Not Allowed
        response = requests.get(f"{config.BACKEND_URL}/users/", headers=admin_headers)
        helpers.print_response(response, "List All Users (Admin)")

        # Create a new user (admin)
        ts = int(time.time())
        new_user_email = f"autouser_{ts}@example.com"
        new_user_data = {
            "email": new_user_email,
            "password": "TempPass123!",
            "full_name": "Auto User"
        }
        response = requests.post(
            f"{config.BACKEND_URL}/users",
            headers=admin_headers,
            json=new_user_data
        )
        helpers.print_response(response, "Create User (Admin)")
        if response.status_code != 200:
            return  # stop early if creation failed

        new_user_id = response.json().get("id")

        # Track for eventual cleanup if something fails later
        if not hasattr(state, "created_user_ids"):
            state.created_user_ids = []
        state.created_user_ids.append(new_user_id)
 
        # Fetch the created user by id
        response = requests.get(
            f"{config.BACKEND_URL}/users/{new_user_id}", headers=admin_headers
        )
        helpers.print_response(response, "Get User By ID (Admin)")

        # Update the created user
        update_admin = {"full_name": "Auto User Updated"}
        response = requests.put(
            f"{config.BACKEND_URL}/users/{new_user_id}",
            headers=admin_headers,
            json=update_admin
        )
        helpers.print_response(response, "Update User (Admin)")

        # Delete the created user
        response = requests.delete(
            f"{config.BACKEND_URL}/users/{new_user_id}", headers=admin_headers
        )
        helpers.print_response(response, "Delete User (Admin)")

        # -------------------- DELETE OWN ACCOUNT TEST --------------------
        # Test delete own account (DELETE /me)
        # Create a temporary user, login as that user, then delete themselves
        temp_user_email = f"temp_delete_{int(time.time())}@example.com"
        temp_user_data = {
            "email": temp_user_email,
            "password": "TempPass123!"
        }
        
        # Create temp user using admin privileges
        response = requests.post(
            f"{config.BACKEND_URL}/users",
            headers=admin_headers,
            json=temp_user_data
        )
        helpers.print_response(response, "Create Temp User for Delete Test")
        
        if response.status_code == 200:
            temp_user_id = response.json().get("id")
            
            # Login as the temporary user
            print(f"   Attempting to login as {temp_user_email}")
            login_response = requests.post(
                f"{config.BACKEND_URL}/auth/login",
                headers={
                    "apikey": config.API_KEY
                },
                data={
                    "username": temp_user_email,
                    "password": "TempPass123!"
                }
            )
            
            if login_response.status_code == 200:
                temp_token = login_response.json().get("access_token")
                temp_headers = {
                    "Authorization": f"Bearer {temp_token}",
                    "Accept": "*/*",
                    "apikey": config.API_KEY
                }
                
                print(f"   Successfully logged in as {temp_user_email}")
                
                # Test delete own account using DELETE /me
                response = requests.delete(
                    f"{config.BACKEND_URL}/users/me",
                    headers=temp_headers
                )
                helpers.print_response(response, "Delete Own Account (DELETE /me)")
                
                # Verify deletion by trying to get user info (should fail)
                verify_response = requests.get(
                    f"{config.BACKEND_URL}/users/me",
                    headers=temp_headers
                )
                if verify_response.status_code == 401:
                    print("✅ User successfully deleted - cannot access account anymore")
                else:
                    print(f"⚠️  Unexpected status after deletion: {verify_response.status_code}")
            else:
                print(f"❌ Could not login as temp user: {login_response.status_code}")
                helpers.print_response(login_response, "Failed Login Attempt")
                if login_response.text:
                    print(f"   Error: {login_response.text}")
        else:
            print(f"❌ Could not create temp user for delete test: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error testing user management: {e}")

def run():
    """Run user management tests"""
    test_user_management()

if __name__ == "__main__":
    # When run independently
    helpers.init_results_file()
    
    # Ensure we have authentication
    if not state.access_token:
        helpers.ensure_authentication()
    
    run()
    # Use the main cleanup helper (now safe for standalone runs)
    helpers.cleanup_test_resources()
    helpers.generate_test_summary()
    helpers.close_results_file()
    print(f"\n📄 Test results saved to: {helpers.state.results_filename}")
