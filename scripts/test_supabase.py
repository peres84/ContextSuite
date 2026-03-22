"""Test connectivity to Supabase."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL", "")
key = os.getenv("SUPABASE_ANON_KEY", "")

if not url or not key:
    print("[SKIP] SUPABASE_URL or SUPABASE_ANON_KEY not set in .env")
    sys.exit(0)

from supabase import create_client

print(f"Connecting to Supabase: {url}")
try:
    client = create_client(url, key)
    # Use RPC or a simple query to verify connectivity
    result = client.table("_test_connectivity").select("*").limit(1).execute()
    print(f"  [OK] Connected.")
except Exception as e:
    err_msg = str(e)
    # These errors mean we connected successfully but the table doesn't exist (expected)
    if "Could not find" in err_msg or "does not exist" in err_msg or "PGRST" in err_msg:
        print(f"  [OK] Connected to Supabase (no tables yet, which is expected).")
    else:
        print(f"  [FAIL] {e}")
