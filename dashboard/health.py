#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine

def check_health():
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://dev_user:dev_password@localhost:5432/llm_monitoring_dev")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Just opening a connection is enough to verify DB is reachable
            pass
        print("OK")
        sys.exit(0)
    except Exception as e:
        print(f"Health check failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_health()
