"""
VERITAS AI — Benchmark Dataset Management Service
"""
import uuid
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.dataset import Dataset, DatasetVersion, DatasetCase
from backend.app.core.security import compute_sha256
from backend.app.services.audit_service import record_audit_event


def create_or_get_dataset(
    db: Session,
    project_id: uuid.UUID,
    name: str,
    slug: str,
    description: Optional[str] = None
) -> Dataset:
    dataset = db.query(Dataset).filter(
        Dataset.project_id == project_id,
        Dataset.slug == slug
    ).first()
    if not dataset:
        dataset = Dataset(
            id=uuid.uuid4(),
            project_id=project_id,
            name=name,
            slug=slug,
            description=description
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
    return dataset


def import_dataset_version_from_jsonl(
    db: Session,
    project_id: uuid.UUID,
    dataset_id: uuid.UUID,
    jsonl_content: str,
    author_email: str,
    change_summary: str = "Imported dataset cases",
    version_label: Optional[str] = None
) -> DatasetVersion:
    """
    Parses JSONL content and commits an immutable dataset version.
    """
    latest = db.query(DatasetVersion).filter(
        DatasetVersion.dataset_id == dataset_id
    ).order_by(desc(DatasetVersion.version_number)).first()

    next_version = (latest.version_number + 1) if latest else 1
    label = version_label or f"v{next_version:04d}"
    content_hash = compute_sha256(jsonl_content)

    version = DatasetVersion(
        id=uuid.uuid4(),
        dataset_id=dataset_id,
        version_number=next_version,
        version_label=label,
        content_hash=content_hash,
        change_summary=change_summary,
        approved_by=author_email,
        is_active=True
    )
    db.add(version)

    cases_count = 0
    for line in jsonl_content.splitlines():
        line = line.strip()
        if not line:
            continue
        case_data = json.loads(line)
        case_hash = compute_sha256(case_data)
        case = DatasetCase(
            id=uuid.uuid4(),
            dataset_version_id=version.id,
            case_hash=case_hash,
            category=case_data.get("category", "edge_case"),
            severity=case_data.get("severity", "major"),
            input_payload=case_data.get("input_payload", {}),
            expected_output=case_data.get("expected_output"),
            expected_criteria=case_data.get("expected_criteria"),
            tags=case_data.get("tags", []),
            source=case_data.get("source", "benchmark_suite"),
            notes=case_data.get("notes")
        )
        db.add(case)
        cases_count += 1

    version.case_count = cases_count
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset:
        dataset.active_version_id = version.id

    db.commit()
    db.refresh(version)

    record_audit_event(
        db=db,
        project_id=project_id,
        actor_email=author_email,
        event_type="DATASET_VERSION_APPROVED",
        payload={
            "dataset_id": str(dataset_id),
            "version_id": str(version.id),
            "version_number": next_version,
            "case_count": cases_count,
            "content_hash": content_hash
        }
    )

    return version

