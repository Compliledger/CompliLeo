"""Proof bundle service: builds a deterministic, hash-anchored bundle.

The bundle is a JSON object capturing the decision metadata for a proof
module. The ``bundle_hash`` is a SHA-256 over the canonical JSON
serialization (sorted keys, no whitespace) of all the other fields, so that
two clients producing the same logical bundle will always agree on the
hash.

Aleo program / transition / proof status / verification status fields are
sourced from :mod:`app.services.aleo_adapter` so that real Aleo execution
can later be plugged in without changing the bundle layout.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.models import ProofBundle, ProofBundleRequest
from app.services import aleo_adapter


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

    # Generate placeholder Aleo proof + verification metadata via the adapter.
    # Inputs are intentionally empty here: the proof bundle records the
    # *decision* outcome and the program/transition that would attest to it,
    # not the raw inputs (which live with the originating proof module and
    # are summarized by ``input_commitment``).
    program = aleo_adapter.PROGRAM_BY_MODULE[req.module]
    proof = aleo_adapter.generate_proof_placeholder(
        program["program_name"],
        program["transition_name"],
        inputs={},
    )
    verification = aleo_adapter.verify_proof_placeholder(proof)

    body: Dict[str, Any] = {
        "module": req.module,
        "decision_result": req.decision_result,
        "reason_codes": list(req.reason_codes),
        "timestamp": ts,
        "input_commitment": proof["input_commitment"],
        "aleo_program": proof["program_name"],
        "transition_name": proof["transition_name"],
        "proof_status": proof["proof_status"],
        "verification_status": verification["verification_status"],
    }

    bundle_hash = _compute_bundle_hash(body)

    return ProofBundle(**body, bundle_hash=bundle_hash)

