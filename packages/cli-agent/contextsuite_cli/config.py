"""Environment config loader for the CLI Agent."""

from pydantic_settings import BaseSettings


class CliSettings(BaseSettings):
    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}

    # Server
    cli_agent_host: str = "127.0.0.1"
    cli_agent_port: int = 8001
    cli_agent_reload: bool = False

    # A2A
    a2a_shared_secret: str = ""

    # Default workspace
    default_workspace: str = "."


settings = CliSettings()
