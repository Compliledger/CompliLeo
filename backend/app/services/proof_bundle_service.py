"""Proof bundle service: builds a deterministic, hash-anchored bundle.

The bundle is a JSON object capturing the decision metadata for a proof
module. The ``bundle_hash`` is a SHA-256 over the canonical JSON
serialization (sorted keys, no whitespace) of all the other fields, so that
two clients producing the same logical bundle will always agree on the
hash.

This MVP uses placeholder values for fields that will eventually be backed
by real Aleo programs / commitments / proof statuses.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.models import ProofBundle, ProofBundleRequest

# Mapping from module name -> placeholder Aleo program identifier.
_ALEO_PROGRAM_BY_MODULE: Dict[str, str] = {
    "tokenproof": "tokenproofx1.aleo",
    "solvencyproof": "solvencypx1.aleo",
    "compliguard": "compliguardx1.aleo",
}

# Placeholder values used until real Aleo integration lands.
_INPUT_COMMITMENT_PLACEHOLDER = "placeholder_input_commitment"
_PROOF_STATUS_PLACEHOLDER = "pending"


def _canonical_json(payload: Dict[str, Any]) -> str:
    """Serialize a dict to canonical JSON (sorted keys, compact separators)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _compute_bundle_hash(payload: Dict[str, Any]) -> str:
    """Compute SHA-256 over canonical JSON of ``payload``."""
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def create_bundle(
    req: ProofBundleRequest,
    *,
    timestamp: Optional[str] = None,
) -> ProofBundle:
    """Build a deterministic proof bundle for the given decision.

    ``timestamp`` may be supplied (e.g. by tests) for determinism; otherwise
    the current UTC time in ISO 8601 format is used.
    """
    ts = timestamp if timestamp is not None else datetime.now(timezone.utc).isoformat()

    body: Dict[str, Any] = {
        "module": req.module,
        "decision_result": req.decision_result,
        "reason_codes": list(req.reason_codes),
        "timestamp": ts,
        "input_commitment": _INPUT_COMMITMENT_PLACEHOLDER,
        "aleo_program": _ALEO_PROGRAM_BY_MODULE[req.module],
        "proof_status": _PROOF_STATUS_PLACEHOLDER,
    }

    bundle_hash = _compute_bundle_hash(body)

    return ProofBundle(**body, bundle_hash=bundle_hash)
