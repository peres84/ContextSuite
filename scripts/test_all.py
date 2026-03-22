"""Run all connectivity tests."""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

scripts = [
    ("Services (Context Agent + CLI Agent)", "test_services.py"),
    ("Supabase", "test_supabase.py"),
    ("Qdrant Cloud", "test_qdrant.py"),
    ("Neo4j Aura", "test_neo4j.py"),
    ("Gemini Embedding 2", "test_gemini.py"),
]


def main():
    print("=" * 60)
    print("ContextSuite — Connectivity Test Suite")
    print("=" * 60)
    print()

    for label, script in scripts:
        print(f"--- {label} ---")
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / script)],
            capture_output=False,
        )
        if result.returncode != 0:
            print(f"  (script exited with code {result.returncode})")
        print()

    print("=" * 60)
    print("Done.")


if __name__ == "__main__":
    main()
