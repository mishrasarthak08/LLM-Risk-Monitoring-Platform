#!/usr/bin/env python3
"""
VERITAS AI — Cryptographic Audit Trail Verification CLI
Performs mathematical verification of the append-only SHA-256 hash chain.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import SessionLocal
from backend.app.models.tenant import Project
from backend.app.services.audit_service import verify_audit_chain


def main():
    print("=" * 70)
    print("VERITAS AI — Cryptographic Audit Ledger Integrity Verification")
    print("=" * 70)

    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.slug == "credit-memo-underwriting").first()
        if not project:
            project = db.query(Project).first()

        if not project:
            print("Error: No projects found in database.")
            sys.exit(1)

        print(f"Auditing Project: {project.name} ({project.id})")
        res = verify_audit_chain(db, project.id)

        print("\nVerification Results:")
        print(f" Status:             {'✅ UNBROKEN / VALID' if res['is_valid'] else '🛑 COMPROMISED'}")
        print(f" Total Records:      {res['total_records']}")
        print(f" Head Hash:          {res.get('head_hash')}")
        print(f" Diagnostics:        {res['message']}")
        print("=" * 70)

        sys.exit(0 if res["is_valid"] else 1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

