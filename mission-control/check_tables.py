#!/usr/bin/env python3
import requests
import json

# Supabase config
SUPABASE_URL = "http://localhost:8000"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

# Try to insert a test record to check if table exists
test_data = {
    "type": "file",
    "description": "Test activity",
    "session_id": "test-session",
    "status": "success"
}

response = requests.post(
    f"{SUPABASE_URL}/rest/v1/activities",
    headers=headers,
    json=test_data
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 404:
    print("\nTables need to be created. Please run the SQL migration manually.")
    print("SQL file location: /home/faisal/.openclaw/workspace/mission-control/supabase/migrations/001_initial_schema.sql")
elif response.status_code == 201:
    print("\n✅ Tables already exist and working!")
else:
    print(f"\n⚠️ Unexpected response: {response.status_code}")