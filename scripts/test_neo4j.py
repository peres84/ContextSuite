"""Test connectivity to Neo4j Aura."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI", "")
user = os.getenv("NEO4J_USERNAME", "") or os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "")

if not uri or not password:
    print("[SKIP] NEO4J_URI or NEO4J_PASSWORD not set in .env")
    sys.exit(0)

# Aura instances need bolt+s:// for direct connections
if uri.startswith("neo4j+s://"):
    uri = uri.replace("neo4j+s://", "bolt+s://")

# The Neo4j Python driver auto-reads NEO4J_DATABASE from env.
# Aura routing doesn't support specifying database by name — unset it
# so the driver falls back to the home database.
os.environ.pop("NEO4J_DATABASE", None)

from neo4j import GraphDatabase

print(f"Connecting to Neo4j: {uri}")
try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run("RETURN 1 AS n")
        record = result.single()
        print(f"  [OK] Connected. Query returned: {record.data()}")
    driver.close()
except Exception as e:
    print(f"  [FAIL] {e}")
