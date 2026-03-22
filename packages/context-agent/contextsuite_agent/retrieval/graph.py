"""Neo4j Aura client for graph retrieval."""

import os

from neo4j import GraphDatabase

from contextsuite_agent.config import settings

# The Neo4j driver auto-reads NEO4J_DATABASE from env, but Aura routing
# doesn't support specifying it. Unset to use the home database.
if "NEO4J_DATABASE" in os.environ:
    del os.environ["NEO4J_DATABASE"]

_driver = None


def get_neo4j():
    global _driver
    if _driver is None:
        uri = settings.neo4j_uri
        # Aura instances need bolt+s:// for direct connections
        if uri.startswith("neo4j+s://"):
            uri = uri.replace("neo4j+s://", "bolt+s://")
        _driver = GraphDatabase.driver(
            uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
        )
    return _driver


def find_related_issues(file_path: str, limit: int = 5) -> list[dict]:
    """Find issues that affect a given file."""
    with get_neo4j().session() as session:
        result = session.run(
            """
            MATCH (i:Issue)-[:AFFECTS]->(f:File {path: $path})
            RETURN i.id AS id, i.title AS title, i.status AS status, i.severity AS severity
            ORDER BY i.severity DESC
            LIMIT $limit
            """,
            path=file_path,
            limit=limit,
        )
        return [dict(record) for record in result]


def find_file_dependencies(file_path: str) -> list[dict]:
    """Find files imported by a given file."""
    with get_neo4j().session() as session:
        result = session.run(
            """
            MATCH (f:File {path: $path})-[:IMPORTS]->(dep:File)
            RETURN dep.path AS path, dep.language AS language
            """,
            path=file_path,
        )
        return [dict(record) for record in result]


def find_constraints_for_repo(repo_id: str) -> list[dict]:
    """Find constraints that apply to a repository."""
    with get_neo4j().session() as session:
        result = session.run(
            """
            MATCH (c:Constraint)-[:APPLIES_TO]->(r:Repository {id: $repo_id})
            RETURN c.id AS id, c.description AS description, c.source AS source
            """,
            repo_id=repo_id,
        )
        return [dict(record) for record in result]
