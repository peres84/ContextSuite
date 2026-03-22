"""Neo4j Aura client for graph retrieval."""

from neo4j import GraphDatabase

from contextsuite_agent.config import settings

_driver = None


def get_neo4j():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
        )
    return _driver


def _session():
    """Open a session targeting the configured database (or home db if empty)."""
    db = settings.neo4j_database or None
    return get_neo4j().session(database=db)


def find_related_issues(file_path: str, limit: int = 5) -> list[dict]:
    """Find issues that affect a given file."""
    with _session() as session:
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
    with _session() as session:
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
    with _session() as session:
        result = session.run(
            """
            MATCH (c:Constraint)-[:APPLIES_TO]->(r:Repository {id: $repo_id})
            RETURN c.id AS id, c.description AS description, c.source AS source
            """,
            repo_id=repo_id,
        )
        return [dict(record) for record in result]
