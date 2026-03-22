"""Set up Neo4j Aura graph schema — constraints and indexes.

Neo4j graph model for ContextSuite:

Node labels:
  - Repository   (id, name, url)
  - Issue        (id, title, status, severity)
  - File         (id, path, language)
  - Entity       (id, name, kind)        — functions, classes, modules, etc.
  - Task         (id, run_id, prompt)     — a ContextSuite run
  - Constraint   (id, description, source)

Relationships:
  - (Repository)-[:HAS_FILE]->(File)
  - (Repository)-[:HAS_ISSUE]->(Issue)
  - (File)-[:DEFINES]->(Entity)
  - (File)-[:IMPORTS]->(File)
  - (Entity)-[:CALLS]->(Entity)
  - (Issue)-[:AFFECTS]->(File)
  - (Issue)-[:RELATED_TO]->(Issue)
  - (Task)-[:TARGETS]->(Repository)
  - (Task)-[:TOUCHES]->(File)
  - (Task)-[:RESOLVES]->(Issue)
  - (Constraint)-[:APPLIES_TO]->(Repository)
  - (Constraint)-[:APPLIES_TO]->(File)
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI", "")
user = os.getenv("NEO4J_USERNAME", "") or os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "")

if not uri or not password:
    print("[SKIP] NEO4J_URI or NEO4J_PASSWORD not set")
    sys.exit(0)

if uri.startswith("neo4j+s://"):
    uri = uri.replace("neo4j+s://", "bolt+s://")

# Unset NEO4J_DATABASE — Aura routing doesn't support it, uses home db
os.environ.pop("NEO4J_DATABASE", None)

from neo4j import GraphDatabase

CONSTRAINTS = [
    "CREATE CONSTRAINT repo_id IF NOT EXISTS FOR (r:Repository) REQUIRE r.id IS UNIQUE",
    "CREATE CONSTRAINT issue_id IF NOT EXISTS FOR (i:Issue) REQUIRE i.id IS UNIQUE",
    "CREATE CONSTRAINT file_id IF NOT EXISTS FOR (f:File) REQUIRE f.id IS UNIQUE",
    "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
    "CREATE CONSTRAINT task_id IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE",
    "CREATE CONSTRAINT constraint_id IF NOT EXISTS FOR (c:Constraint) REQUIRE c.id IS UNIQUE",
]

INDEXES = [
    "CREATE INDEX file_path IF NOT EXISTS FOR (f:File) ON (f.path)",
    "CREATE INDEX issue_status IF NOT EXISTS FOR (i:Issue) ON (i.status)",
    "CREATE INDEX task_run_id IF NOT EXISTS FOR (t:Task) ON (t.run_id)",
    "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
]


def main():
    print(f"Connecting to Neo4j: {uri}")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            session.run("RETURN 1")
        print("  [OK] Connected")
    except Exception as e:
        print(f"  [FAIL] {e}")
        sys.exit(1)

    with driver.session() as session:
        print("  Creating constraints...")
        for stmt in CONSTRAINTS:
            session.run(stmt)
            label = stmt.split("FOR (")[1].split(")")[0].split(":")[1]
            print(f"    - {label}")

        print("  Creating indexes...")
        for stmt in INDEXES:
            session.run(stmt)
            name = stmt.split("IF NOT EXISTS FOR")[0].split("INDEX ")[1].strip()
            print(f"    - {name}")

    driver.close()
    print("  [OK] Neo4j schema setup complete")


if __name__ == "__main__":
    main()
