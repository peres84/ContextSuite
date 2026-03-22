"""Test connectivity to Neo4j Aura."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI", "")
user = os.getenv("NEO4J_USERNAME", "") or os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "")
database = os.getenv("NEO4J_DATABASE", "") or None

if not uri or not password:
    print("[SKIP] NEO4J_URI or NEO4J_PASSWORD not set in .env")
    sys.exit(0)

from neo4j import GraphDatabase

print(f"Connecting to Neo4j: {uri}")
print(f"  Database: {database or '(home)'}")
try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session(database=database) as session:
        result = session.run("RETURN 1 AS n")
        record = result.single()
        print(f"  [OK] Connected. Query returned: {record.data()}")
    driver.close()
except Exception as e:
    print(f"  [FAIL] {e}")
