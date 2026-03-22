"""Environment config loader for the Context Agent."""

from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}

    # Server
    context_agent_host: str = "0.0.0.0"
    context_agent_port: int = 8000

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Qdrant
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "contextsuite"

    # Neo4j
    neo4j_uri: str = ""
    neo4j_username: str = ""
    neo4j_password: str = ""
    neo4j_database: str = "neo4j"

    # Gemini
    google_api_key: str = ""
    gemini_embedding_model: str = "models/gemini-embedding-2-preview"

    # CLI Agent target
    cli_agent_host: str = "127.0.0.1"
    cli_agent_port: int = 8001

    # A2A
    a2a_shared_secret: str = ""


settings = AgentSettings()
