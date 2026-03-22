"""Test connectivity to Context Agent and CLI Agent endpoints."""

import httpx

CONTEXT_AGENT = "http://localhost:8000"
CLI_AGENT = "http://localhost:8001"


def test_endpoint(name: str, url: str):
    try:
        r = httpx.get(url, timeout=5)
        status = "OK" if r.status_code == 200 else f"FAIL ({r.status_code})"
        print(f"  [{status}] {name} -> {url}")
        if r.status_code == 200:
            print(f"         {r.json()}")
    except httpx.ConnectError:
        print(f"  [DOWN] {name} -> {url} (connection refused)")
    except Exception as e:
        print(f"  [ERR]  {name} -> {url} ({e})")


def main():
    print("=== Context Agent ===")
    test_endpoint("Health", f"{CONTEXT_AGENT}/health")
    test_endpoint("Agent Card", f"{CONTEXT_AGENT}/.well-known/agent.json")

    print()
    print("=== CLI Agent ===")
    test_endpoint("Health", f"{CLI_AGENT}/health")
    test_endpoint("Agent Card", f"{CLI_AGENT}/.well-known/agent.json")


if __name__ == "__main__":
    main()
