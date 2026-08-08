import os
from typing import Dict, Any, List
from datetime import datetime
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from monitoring.db.models import DriftReferenceDistribution

def get_engine():
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://dev_user:dev_password@localhost:5432/llm_monitoring_dev"
    )
    return create_engine(db_url)

def get_session():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal()


def build_reference_distribution(feature_name: str, metric: str, distribution_data: Any, start_time: str, end_time: str) -> str:
    """
    Builds a baseline reference distribution for a specific metric over a stable time window.
    Saves it to the real database table DriftReferenceDistribution.
    """
    session = get_session()
    try:
        # Mark existing active references for this feature/metric as superseded
        active_refs = session.query(DriftReferenceDistribution).filter(
            DriftReferenceDistribution.feature_name == feature_name,
            DriftReferenceDistribution.metric == metric,
            DriftReferenceDistribution.superseded_by == None
        ).all()
        
        new_id = uuid.uuid4()

        for ref in active_refs:
            ref.superseded_by = new_id

        # The built_from_window is a TSTZRANGE. For psycopg2/sqlalchemy we can insert as a string or psycopg2 Range
        # Let's format it as a postgres range string
        range_str = f"[{start_time},{end_time}]"

        new_reference = DriftReferenceDistribution(
            id=new_id,
            feature_name=feature_name,
            metric=metric,
            distribution_summary=distribution_data,
            built_from_window=range_str,
            superseded_by=None
        )

        session.add(new_reference)
        session.commit()

        return str(new_id)
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_active_reference(feature_name: str, metric: str) -> list | dict | None:
    """
    Retrieves the currently active (not superseded) reference distribution data.
    """
    session = get_session()
    try:
        active_ref = session.query(DriftReferenceDistribution).filter(
            DriftReferenceDistribution.feature_name == feature_name,
            DriftReferenceDistribution.metric == metric,
            DriftReferenceDistribution.superseded_by == None
        ).order_by(DriftReferenceDistribution.created_at.desc()).first()
        
        if active_ref:
            return active_ref.distribution_summary
        return None
    finally:
        session.close()
