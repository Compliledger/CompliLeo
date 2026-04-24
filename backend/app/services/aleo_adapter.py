"""Aleo adapter — **placeholder** layer for CompliLeo Backend Phase 2.

This module abstracts how CompliLeo will eventually invoke the Aleo
network to execute and verify the ``tokenproofx1.aleo``,
``solvencypx1.aleo``, and ``compliguardx1.aleo`` programs.

.. warning::
   Everything in this module is a **simulated placeholder**. It does
   **not** call the Aleo network, does **not** require a wallet, and
   does **not** generate real zero-knowledge proofs. When real Aleo
   execution is wired in, only the bodies of
   :func:`generate_proof_placeholder` and :func:`verify_proof_placeholder`
   need to change; the public surface stays the same.

The module exposes:

* per-module input preparation helpers that normalize backend request
  payloads into the typed inputs each Aleo transition expects, and
* :func:`generate_proof_placeholder` / :func:`verify_proof_placeholder`
  which return stable, deterministic metadata so downstream components
  (e.g. the proof-bundle service) can be wired up against a final-shape
  interface today.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Mapping

from app.models import (
    CompliGuardRequest,
    SolvencyProofRequest,
    TokenProofRequest,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PROOF_STATUS_SIMULATED = "simulated"
VERIFICATION_STATUS_PENDING = "pending_aleo_execution"

#: Mapping from logical CompliLeo module name -> the Aleo program and
#: transition that *would* be executed for that module. Exposed so callers
#: (e.g. the proof-bundle service) don't need to hard-code these strings.
PROGRAM_BY_MODULE: Dict[str, Dict[str, str]] = {
    "tokenproof": {
        "program_name": "tokenproofx1.aleo",
        "transition_name": "check_token_admission",
    },
    "solvencyproof": {
        "program_name": "solvencypx1.aleo",
        "transition_name": "check_solvency",
    },
    "compliguard": {
        "program_name": "compliguardx1.aleo",
        "transition_name": "check_system_health",
    },
}


# ---------------------------------------------------------------------------
# Input preparation
# ---------------------------------------------------------------------------
def prepare_tokenproof_input(payload: TokenProofRequest) -> Dict[str, Any]:
    """Translate a ``TokenProofRequest`` into ``check_token_admission`` inputs.

    The Aleo transition expects two ``bool`` arguments. We mirror the
    transition's parameter names so this dict can be consumed verbatim by
    a future Aleo executor.
    """
    return {
        "issuer_approved": bool(payload.issuer_approved),
        "asset_type_supported": bool(payload.asset_type_supported),
    }


def prepare_solvencyproof_input(payload: SolvencyProofRequest) -> Dict[str, Any]:
    """Translate a ``SolvencyProofRequest`` into ``check_solvency`` inputs.

    The Aleo transition expects two ``u64`` values. We keep them as Python
    ``int`` here; serialization to Aleo's ``u64`` literal form (e.g.
    ``"123u64"``) is the executor's responsibility.
    """
    return {
        "reserves": int(payload.reserves),
        "liabilities": int(payload.liabilities),
    }


def prepare_compliguard_input(payload: CompliGuardRequest) -> Dict[str, Any]:
    """Translate a ``CompliGuardRequest`` into ``check_system_health`` inputs."""
    return {
        "anomaly_score_below_threshold": bool(payload.anomaly_score_below_threshold),
        "critical_alert_open": bool(payload.critical_alert_open),
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _canonical_json(payload: Mapping[str, Any]) -> str:
    """Serialize ``payload`` to canonical JSON (sorted keys, compact)."""
    return json.dumps(dict(payload), sort_keys=True, separators=(",", ":"))


def _input_commitment(inputs: Mapping[str, Any]) -> str:
    """Deterministic SHA-256 hex digest over canonical JSON of ``inputs``.

    Used as a *placeholder* for what will eventually be the Aleo input
    commitment. It is deterministic for identical inputs, and changes as
    soon as any input changes — which is enough for downstream bundle
    hashing to remain meaningful.
    """
    return hashlib.sha256(_canonical_json(inputs).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Proof generation / verification placeholders
# ---------------------------------------------------------------------------
def generate_proof_placeholder(
    program_name: str,
    transition_name: str,
    inputs: Mapping[str, Any],
) -> Dict[str, Any]:
    """Return placeholder proof metadata for an Aleo transition call.

    Does **not** contact the Aleo network and does **not** produce a real
    zero-knowledge proof. The returned dict captures the program /
    transition that *would* be executed, a deterministic
    ``input_commitment`` over the inputs, and status fields indicating
    that this is a simulated, not-yet-verified placeholder.
    """
    return {
        "program_name": program_name,
        "transition_name": transition_name,
        "proof_status": PROOF_STATUS_SIMULATED,
        "verification_status": VERIFICATION_STATUS_PENDING,
        "input_commitment": _input_commitment(inputs),
    }


def verify_proof_placeholder(proof_metadata: Mapping[str, Any]) -> Dict[str, Any]:
    """Return placeholder verification metadata for ``proof_metadata``.

    Does **not** contact the Aleo network. Echoes the program / transition
    / input commitment from the proof and reports a ``verification_status``
    of ``"pending_aleo_execution"`` since real on-chain verification has
    not yet been executed.
    """
    return {
        "program_name": proof_metadata.get("program_name"),
        "transition_name": proof_metadata.get("transition_name"),
        "input_commitment": proof_metadata.get("input_commitment"),
        "verification_status": VERIFICATION_STATUS_PENDING,
    }
