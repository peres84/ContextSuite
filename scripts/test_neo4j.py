"""Test connectivity to Neo4j Aura."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI", "")
user = os.getenv("NEO4J_USERNAME", "") or os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "")
database = os.getenv("NEO4J_DATABASE", "neo4j")

if not uri or not password:
    print("[SKIP] NEO4J_URI or NEO4J_PASSWORD not set in .env")
    sys.exit(0)

from neo4j import GraphDatabase

print(f"Connecting to Neo4j: {uri}")
try:
    driver = GraphDatabase.driver(uri, auth=(user, password), database=database)
    driver.verify_connectivity()
    info = driver.get_server_info()
    print(f"  [OK] Connected. Server: {info.agent} @ {info.address}")
    driver.close()
except Exception as e:
    print(f"  [FAIL] {e}")
