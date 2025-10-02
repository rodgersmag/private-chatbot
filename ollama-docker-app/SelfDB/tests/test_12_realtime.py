"""
Test real-time WebSocket functionality for SelfDB.
"""

import time
import json
import asyncio
import requests
import websockets
from common import config, state, helpers

async def test_realtime_table_subscription():
    """Test dedicated real-time subscription to a specific table with a regular user."""
    helpers.print_test_header("Real-time Table Subscription")

    # Use the regular user's token
    if not state.access_token:
        helpers.write_to_file("❌ Skipping real-time table subscription test - no user token available.")
        state.test_summary["total"] += 1
        state.test_summary["failed"] += 1
        state.test_summary["errors"].append({"description": "Real-time: No user token", "status_code": "N/A", "url": "N/A"})
        return

    user_headers = helpers.get_headers(auth=True)
    table_name = f"rt_test_{str(int(time.time()))}"

    # 1. Ensure the table exists
    table_payload = {
        "name": table_name,
        "description": "Realtime test table for regular user",
        "if_not_exists": True,
        "columns": [
            {"name": "id", "type": "UUID", "nullable": False, "primary_key": True, "default": "gen_random_uuid()"},
            {"name": "message", "type": "TEXT", "nullable": False},
            {"name": "created_at", "type": "TIMESTAMPTZ", "nullable": True, "default": "now()"}
        ]
    }
    r = requests.post(f"{config.BACKEND_URL}/tables", headers={**user_headers, "Content-Type": "application/json"}, json=table_payload)
    helpers.print_response(r, f"Ensure '{table_name}' table exists for real-time test")
    
    # 2. Set up WebSocket connection and specific subscription
    ws_url = config.BACKEND_URL.replace("http://", "ws://").replace("https://", "wss://") + f"/realtime/ws?apikey={config.API_KEY}"
    row_id = None
    received_notifications = []
    seen_operations = set()

    try:
        async with websockets.connect(ws_url) as ws:
            # Authenticate with the user's token
            await ws.send(json.dumps({"type": "authenticate", "token": state.access_token}))
            auth_response = json.loads(await ws.recv())
            helpers.write_to_file(f"WS-RTTest: Authenticated: {auth_response}")

            # Subscribe specifically to the new table's changes
            subscription_id = f"{table_name}_changes"
            await ws.send(json.dumps({"type": "subscribe", "subscription_id": subscription_id}))
            sub_response = json.loads(await ws.recv())
            helpers.write_to_file(f"WS-RTTest: Subscribed: {sub_response}")

            # 3. Perform CRUD operations to trigger notifications
            # INSERT
            insert_data = {"message": "Hello, world!"}
            insert_res = requests.post(
                f"{config.BACKEND_URL}/tables/{table_name}/data", 
                headers=user_headers, 
                json=insert_data
            )
            if insert_res.status_code == 200:
                insert_json = insert_res.json()
                row_id = insert_json.get("id")
            helpers.write_to_file(f"WS-RTTest: Inserted row with ID: {row_id} - Status: {insert_res.status_code}")
            
            await asyncio.sleep(1.0)
            
            # UPDATE
            if row_id:
                update_data = {"message": "Hello, updated world!"}
                update_res = requests.put(
                    f"{config.BACKEND_URL}/tables/{table_name}/data/{row_id}?id_column=id",
                    headers=user_headers,
                    json=update_data
                )
                helpers.write_to_file(f"WS-RTTest: Updated row with ID: {row_id} - Status: {update_res.status_code}")
                await asyncio.sleep(1.0)

                # DELETE
                delete_res = requests.delete(
                    f"{config.BACKEND_URL}/tables/{table_name}/data/{row_id}?id_column=id",
                    headers=user_headers
                )
                helpers.write_to_file(f"WS-RTTest: Deleted row with ID: {row_id} - Status: {delete_res.status_code}")
                await asyncio.sleep(1.0)
            else:
                helpers.write_to_file("WS-RTTest: Skipping UPDATE and DELETE - no row ID from INSERT")

            # 4. Collect notifications
            helpers.write_to_file("\nWS-RTTest: Collecting notifications...")
            end_time = time.time() + 15
            while time.time() < end_time and len(received_notifications) < 3:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    data = json.loads(msg)
                    if data.get("type") == "database_change" and data.get("subscription_id") == subscription_id:
                        operation = data.get('data', {}).get('operation', 'UNKNOWN')
                        row_data = data.get('data', {}).get('data', {})
                        old_data = data.get('data', {}).get('old_data', {})
                        
                        if operation == 'DELETE' and old_data:
                            row_data_id = old_data.get('id') if isinstance(old_data, dict) else None
                        else:
                            row_data_id = row_data.get('id') if isinstance(row_data, dict) else None
                        
                        helpers.write_to_file(f"WS-RTTest: Notification received - Operation: {operation}, Row ID: {row_data_id}, Our Row ID: {row_id}")
                        
                        if row_data_id == row_id or (operation == 'INSERT' and not row_id):
                            operation_key = f"{operation}:{row_data_id or 'new'}"
                            if operation_key not in seen_operations:
                                seen_operations.add(operation_key)
                                received_notifications.append(data)
                                helpers.write_to_file(f"WS-RTTest: ✓ Counted notification: {operation} for row {row_data_id}")
                                
                                if operation == 'INSERT' and not row_id and row_data_id:
                                    row_id = row_data_id
                                    helpers.write_to_file(f"WS-RTTest: Captured row ID from notification: {row_id}")
                            else:
                                helpers.write_to_file(f"WS-RTTest: Skipped duplicate: {operation_key}")
                        else:
                            helpers.write_to_file(f"WS-RTTest: Skipped notification for different row: {row_data_id} != {row_id}")
                except asyncio.TimeoutError:
                    if len(received_notifications) >= 3:
                        helpers.write_to_file("WS-RTTest: Collected all expected notifications")
                        break
                    continue
                except Exception as e:
                    helpers.write_to_file(f"WS-RTTest: Error receiving notification: {e}")
                    break
            
            helpers.write_to_file(f"\nWS-RTTest: Collection complete. Total notifications: {len(received_notifications)}")
            helpers.write_to_file(f"WS-RTTest: Operations seen: {seen_operations}")
                    
    except Exception as e:
        helpers.write_to_file(f"❌ An error occurred during the real-time table test: {e}")

    # 5. Verify the notifications
    helpers.write_to_file("\n--- Real-time Table Subscription Verification ---")
    helpers.write_to_file(f"Total notifications received: {len(received_notifications)}")
    helpers.write_to_file(f"Unique operations tracked: {seen_operations}")
    
    test_desc_count = "Real-time: Received correct number of notifications (3)"
    state.test_summary["total"] += 1
    if len(received_notifications) == 3:
        state.test_summary["passed"] += 1
        state.test_summary["passed_tests"].append(test_desc_count)
        helpers.write_to_file(f"✅ {test_desc_count}")
    else:
        state.test_summary["failed"] += 1
        state.test_summary["errors"].append({"description": test_desc_count, "status_code": f"Got {len(received_notifications)}", "url": "WebSocket"})
        helpers.write_to_file(f"❌ {test_desc_count} - Got {len(received_notifications)}")

    expected_ops = ["INSERT", "UPDATE", "DELETE"]
    actual_ops = [n.get("data", {}).get("operation") for n in received_notifications]
    test_desc_order = f"Real-time: Received correct operations in order ({', '.join(expected_ops)})"
    state.test_summary["total"] += 1
    if actual_ops == expected_ops:
        state.test_summary["passed"] += 1
        state.test_summary["passed_tests"].append(test_desc_order)
        helpers.write_to_file(f"✅ {test_desc_order}")
    else:
        state.test_summary["failed"] += 1
        state.test_summary["errors"].append({"description": test_desc_order, "status_code": f"Got {actual_ops}", "url": "WebSocket"})
        helpers.write_to_file(f"❌ {test_desc_order} - Got {actual_ops}")

    # Final cleanup of the test table
    if state.access_token:
        helpers.write_to_file(f"\nWS-RTTest: Cleaning up '{table_name}' table...")
        cleanup_res = requests.delete(f"{config.BACKEND_URL}/tables/{table_name}", headers=user_headers)
        helpers.write_to_file(f"WS-RTTest: Cleanup status: {cleanup_res.status_code}")

def run():
    """Run real-time tests"""
    asyncio.run(test_realtime_table_subscription())

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
