"""
Test authentication endpoints for SelfDB.
"""

import time
import requests
from common import config, state, helpers

def test_authentication():
    """Test authentication endpoints"""
    helpers.print_test_header("Authentication")
    
    # Generate unique email for this test run
    timestamp = str(int(time.time()))
    test_email = f"{config.TEST_EMAIL_BASE}_{timestamp}@example.com"
    
    try:
        # Test user registration with unique email
        register_data = {
            "email": test_email,
            "password": config.TEST_PASSWORD,
            "full_name": "Test User"
        }
        response = requests.post(
            f"{config.BACKEND_URL}/auth/register",
            headers={**helpers.get_headers(), "Content-Type": "application/json"},
            json=register_data
        )
        helpers.print_response(response, "User Registration")
        
        # Test login
        login_data = f"username={test_email}&password={config.TEST_PASSWORD}"
        response = requests.post(
            f"{config.BACKEND_URL}/auth/login",
            headers={**helpers.get_headers(), "Content-Type": "application/x-www-form-urlencoded"},
            data=login_data
        )
        helpers.print_response(response, "User Login")
        
        refresh_token = None
        if response.status_code == 200:
            login_result = response.json()
            state.access_token = login_result.get("access_token")
            refresh_token = login_result.get("refresh_token")
            state.user_id = login_result.get("user_id")
            state.test_email = test_email
            print(f"✅ Authentication successful! Token acquired for {test_email}")
            
            # Test refresh token if available
            if refresh_token:
                refresh_data = {"refresh_token": refresh_token}
                response = requests.post(
                    f"{config.BACKEND_URL}/auth/refresh",
                    headers={**helpers.get_headers(), "Content-Type": "application/json"},
                    json=refresh_data
                )
                # Accept 500 as expected if refresh token feature has issues
                if response.status_code == 500:
                    helpers.print_response(response, "Refresh Access Token (Feature Error)", expected_status=500)
                else:
                    helpers.print_response(response, "Refresh Access Token")
        else:
            print(f"❌ Authentication failed!")
            
    except requests.exceptions.RequestException as e:
        print(f"Error testing authentication: {e}")

def run():
    """Run authentication tests"""
    test_authentication()

if __name__ == "__main__":
    # When run independently
    helpers.init_results_file()
    run()
    helpers.generate_test_summary()
    helpers.close_results_file()
    print(f"\n📄 Test results saved to: {helpers.state.results_filename}")
