"""
Test table management endpoints for SelfDB.
"""

import time
import requests
from common import config, state, helpers

def test_table_management():
    """Test table management endpoints"""
    helpers.print_test_header("Table Management")
    
    try:
        # List tables
        response = requests.get(f"{config.BACKEND_URL}/tables", headers=helpers.get_headers(auth=state.access_token is not None))
        helpers.print_response(response, "List Tables")
        
        # Get table details for users table
        response = requests.get(f"{config.BACKEND_URL}/tables/users", headers=helpers.get_headers(auth=state.access_token is not None))
        helpers.print_response(response, "Get Users Table Details")
        
        # Get table data
        response = requests.get(
            f"{config.BACKEND_URL}/tables/users/data?page=1&page_size=5",
            headers=helpers.get_headers(auth=state.access_token is not None)
        )
        helpers.print_response(response, "Get Users Table Data")
        
        if not state.access_token:
            print("⚠️ Skipping table modification tests - no token")
            return
        
        # Create test table with unique name
        timestamp = str(int(time.time()))
        test_table_name = f"test_products_{timestamp}"
        table_data = {
            "name": test_table_name,
            "description": "Test products table",
            "if_not_exists": True,
            "columns": [
                {
                    "name": "id",
                    "type": "UUID",
                    "nullable": False,
                    "primary_key": True,
                    "default": "gen_random_uuid()"
                },
                {
                    "name": "name",
                    "type": "VARCHAR(255)",
                    "nullable": False,
                    "description": "Product name"
                },
                {
                    "name": "price",
                    "type": "DECIMAL(10,2)",
                    "nullable": True
                }
            ]
        }
        response = requests.post(
            f"{config.BACKEND_URL}/tables",
            headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
            json=table_data
        )
        helpers.print_response(response, "Create Test Table")
        
        # Insert test data
        if response.status_code == 201:
            insert_data = {
                "name": "Test Product",
                "price": 19.99
            }
            response = requests.post(
                f"{config.BACKEND_URL}/tables/{test_table_name}/data",
                headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
                json=insert_data
            )
            helpers.print_response(response, "Insert Test Data")
            
            # Capture inserted row's primary key
            row_json = response.json()
            row_id = row_json.get("id") or row_json.get("ID")
            
            # Update the row
            if row_id:
                update_data = {"price": 29.99}
                response = requests.put(
                    f"{config.BACKEND_URL}/tables/{test_table_name}/data/{row_id}?id_column=id",
                    headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
                    json=update_data
                )
                helpers.print_response(response, "Update Row Data")
            
            # Update table description
            table_update = {"description": "Updated test products table"}
            response = requests.put(
                f"{config.BACKEND_URL}/tables/{test_table_name}",
                headers={**helpers.get_headers(auth=True), "Content-Type": "application/json"},
                json=table_update
            )
            helpers.print_response(response, "Update Table Description")
            
            # Delete the table
            response = requests.delete(
                f"{config.BACKEND_URL}/tables/{test_table_name}",
                headers=helpers.get_headers(auth=True)
            )
            helpers.print_response(response, "Delete Test Table")
            
    except requests.exceptions.RequestException as e:
        print(f"Error testing table management: {e}")

def run():
    """Run table management tests"""
    test_table_management()

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
