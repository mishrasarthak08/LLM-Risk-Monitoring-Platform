import os
import sys
import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from monitoring.db.models import GoldenSetVersion, GoldenSetCase

def bulk_import(jsonl_path: str):
    print(f"Importing golden set from {jsonl_path}...")
    
    path = Path(jsonl_path)
    if not path.exists():
        print(f"File {jsonl_path} does not exist.")
        sys.exit(1)
        
    db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://dev_user:dev_password@localhost:5432/llm_monitoring_dev")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    
    with open(path, "r") as f:
        lines = f.readlines()
        
    cases_data = [json.loads(line) for line in lines if line.strip()]
    
    if not cases_data:
        print("No cases found.")
        return
        
    # Create GoldenSetVersion
    feature_name = "credit_memo_v1"
    content_hash = hashlib.sha256("".join(lines).encode('utf-8')).hexdigest()
    
    with Session() as session:
        version_num = session.query(GoldenSetVersion).filter_by(feature_name=feature_name).count() + 1
        
        gs_version = GoldenSetVersion(
            id=uuid.uuid4(),
            version_number=version_num,
            feature_name=feature_name,
            content_hash=content_hash,
            case_count=len(cases_data),
            storage_uri=f"local://{path.name}",
            change_summary=f"Bulk imported {len(cases_data)} cases",
            approved_by="automated_script",
        )
        session.add(gs_version)
        session.flush()
        
        # Add cases
        for data in cases_data:
            case = GoldenSetCase(
                id=uuid.uuid4(),
                golden_set_version_id=gs_version.id,
                case_hash=data["case_hash"],
                category=data["category"],
                input_payload=data["input_payload"],
                expected_output=data.get("expected_output"),
                expected_criteria=data.get("expected_criteria"),
                severity=data["severity"],
                tags=data.get("tags"),
                source=data["source"],
                added_by=data["added_by"],
                added_at=datetime.fromisoformat(data["added_at"].replace("Z", "+00:00")),
                notes=data["notes"]
            )
            session.add(case)
            
        session.commit()
        print(f"Successfully imported version {version_num} with {len(cases_data)} cases.")
        print(f"GoldenSetVersion ID: {gs_version.id}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bulk_import_golden_set.py <path_to_jsonl>")
        sys.exit(1)
        
    bulk_import(sys.argv[1])
