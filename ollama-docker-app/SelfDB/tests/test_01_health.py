"""
Test health check endpoints for SelfDB.
"""

import requests
from common import config, helpers

def test_health_endpoints():
    """Test health check endpoints"""
    helpers.print_test_header("Health Check Endpoints")
    
    try:
        # Backend health
        response = requests.get(f"{config.BACKEND_URL}/health", headers=helpers.get_headers())
        helpers.print_response(response, "Backend API Health")
        
        # Backend database health
        response = requests.get(f"{config.BACKEND_URL}/health/db", headers=helpers.get_headers())
        helpers.print_response(response, "Backend Database Health")
        
        # Storage service health
        response = requests.get(f"{config.STORAGE_URL}/health", headers=helpers.get_headers())
        helpers.print_response(response, "Storage Service Health")
        
        # Storage service root endpoint
        response = requests.get(f"{config.STORAGE_URL}/", headers=helpers.get_headers())
        helpers.print_response(response, "Storage Service Root")
        
    except requests.exceptions.RequestException as e:
        print(f"Error testing health endpoints: {e}")

def run():
    """Run health tests"""
    test_health_endpoints()

if __name__ == "__main__":
    # When run independently
    helpers.init_results_file()
    run()
    helpers.generate_test_summary()
    helpers.close_results_file()
    print(f"\n📄 Test results saved to: {helpers.state.results_filename}")
