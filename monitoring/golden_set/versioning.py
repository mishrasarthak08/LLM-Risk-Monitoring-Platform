import hashlib
import json


def content_hash(payload: str | dict) -> str:
    """Canonical content hash. For dicts, sort keys so semantically
    identical JSON in different key order hashes the same."""
    if isinstance(payload, dict):
        payload = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def golden_set_hash(case_hashes: list[str]) -> str:
    """Hash of a hash list — order-independent so reordering cases
    in the source file doesn't spuriously bump the version."""
    return content_hash(json.dumps(sorted(case_hashes)))
