"""
Test function management endpoints for SelfDB.
"""

import time
import requests
from common import config, state, helpers

def test_functions():
    """Test function management endpoints"""
    helpers.print_test_header("Function Management")
    
    if not state.access_token:
        print("❌ Skipping function tests - no authentication token")
        return
    
    try:
        # List functions
        response = requests.get(f"{config.BACKEND_URL}/functions", headers=helpers.get_headers(auth=True))
        helpers.print_response(response, "List Functions")
        
        # Create function with unique name
        timestamp = str(int(time.time()))
        function_name = f"test-function-{timestamp}"
        function_data = {
            "name": function_name,
            "code": 'export default async function handler(req) { return new Response("Hello from test function!"); }',
            "description": "Test function for API testing"
        }
        response = requests.post(
            f"{config.BACKEND_URL}/functions",
            headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
            json=function_data
        )
        helpers.print_response(response, "Create Function")
        
        if response.status_code == 201:
            function_id = response.json().get("id")
            state.add_created_function(function_id)
            
            # Get function
            response = requests.get(f"{config.BACKEND_URL}/functions/{function_id}", headers=helpers.get_headers(auth=True))
            helpers.print_response(response, "Get Function")
            
            # Update function
            update_data = {
                "description": "Updated test function description"
            }
            response = requests.put(
                f"{config.BACKEND_URL}/functions/{function_id}",
                headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
                json=update_data
            )
            helpers.print_response(response, "Update Function")
            
            # List function versions
            response = requests.get(f"{config.BACKEND_URL}/functions/{function_id}/versions", headers=helpers.get_headers(auth=True))
            helpers.print_response(response, "List Function Versions")
            
            # List function environment variables
            response = requests.get(f"{config.BACKEND_URL}/functions/{function_id}/env", headers=helpers.get_headers(auth=True))
            helpers.print_response(response, "List Function Environment Variables")
            
            # Create environment variable
            env_data = {
                "key": "TEST_VAR",
                "value": "test_value"
            }
            response = requests.post(
                f"{config.BACKEND_URL}/functions/{function_id}/env",
                headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
                json=env_data
            )
            helpers.print_response(response, "Create Environment Variable")
            
            if response.status_code == 201:
                env_var_id = response.json().get("id")
                
                # Delete environment variable
                response = requests.delete(
                    f"{config.BACKEND_URL}/functions/{function_id}/env/{env_var_id}",
                    headers=helpers.get_headers(auth=True)
                )
                helpers.print_response(response, "Delete Environment Variable")
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing functions: {e}")

def test_function_templates():
    """Test function template endpoints"""
    helpers.print_test_header("Function Templates")
    
    try:
        # Test get function template
        response = requests.get(f"{config.BACKEND_URL}/functions/templates/default", headers=helpers.get_headers())
        helpers.print_response(response, "Get Function Template (default)")
        
        # Try other common trigger types that might be supported
        for trigger_type in ["http", "cron", "webhook"]:
            response = requests.get(f"{config.BACKEND_URL}/functions/templates/{trigger_type}", headers=helpers.get_headers())
            helpers.print_response(response, f"Get Function Template ({trigger_type})")
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing function templates: {e}")

def run():
    """Run function tests"""
    test_functions()
    test_function_templates()

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
