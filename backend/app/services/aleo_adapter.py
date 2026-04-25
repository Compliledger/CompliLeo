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
from app.services import aleo_execution_adapter
from app.services.aleo_program_registry import ALEO_PROGRAMS

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PROOF_STATUS_SIMULATED = "simulated"
PROOF_STATUS_LOCAL_EXECUTED = "local_executed"
PROOF_STATUS_LOCAL_FAILED = "local_execution_failed"
VERIFICATION_STATUS_PENDING = "pending_aleo_execution"
VERIFICATION_STATUS_LOCAL_VERIFIED = "locally_verified"
VERIFICATION_STATUS_LOCAL_FAILED = "local_verification_failed"

#: Mapping from logical CompliLeo module name -> the Aleo program and
#: transition that *would* be executed for that module. Sourced from
#: :mod:`app.services.aleo_program_registry` so program names and
#: transition names live in exactly one place. Exposed for back-compat
#: with callers (e.g. the proof-bundle service) that already read this
#: attribute.
PROGRAM_BY_MODULE: Dict[str, Dict[str, str]] = {
    module: {
        "program_name": entry["program_name"],
        "transition_name": entry["transition_name"],
    }
    for module, entry in ALEO_PROGRAMS.items()
}


# ---------------------------------------------------------------------------
# Input preparation
# ---------------------------------------------------------------------------
def prepare_tokenproof_input(payload: TokenProofRequest) -> Dict[str, Any]:
    """Translate a ``TokenProofRequest`` into ``verify_token`` inputs.

    The Aleo transition expects two ``bool`` arguments. We mirror the
    transition's parameter names so this dict can be consumed verbatim by
    a future Aleo executor.
    """
    return {
        "issuer_approved": bool(payload.issuer_approved),
        "asset_type_supported": bool(payload.asset_type_supported),
    }


def prepare_solvencyproof_input(payload: SolvencyProofRequest) -> Dict[str, Any]:
    """Translate a ``SolvencyProofRequest`` into ``prove_solvency`` inputs.

    The Aleo transition expects two ``u64`` values. We keep them as Python
    ``int`` here; serialization to Aleo's ``u64`` literal form (e.g.
    ``"123u64"``) is the executor's responsibility.
    """
    return {
        "reserves": int(payload.reserves),
        "liabilities": int(payload.liabilities),
    }


def prepare_compliguard_input(payload: CompliGuardRequest) -> Dict[str, Any]:
    """Translate a ``CompliGuardRequest`` into ``prove_health`` inputs."""
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


# ---------------------------------------------------------------------------
# Mode-aware proof / verification metadata
# ---------------------------------------------------------------------------
def _proof_reference(program_name: str, input_commitment: str) -> str:
    """Return a deterministic, opaque reference for a (would-be) proof.

    Real Aleo execution will yield a concrete proof transaction id; in
    simulated mode we synthesize a stable pseudo-id so downstream
    consumers always have *some* reference to render.
    """
    return f"{program_name}:{input_commitment[:16]}"


def build_proof_metadata(
    module: str,
    inputs: Mapping[str, Any],
) -> Dict[str, Any]:
    """Produce the full ``aleo`` block returned by proof endpoints.

    Dispatches through :mod:`app.services.aleo_execution_adapter` so
    behavior is governed by the ``ALEO_EXECUTION_MODE`` environment
    variable:

    * ``simulated`` — returns the legacy placeholder fields plus an
      ``execution_mode`` of ``"simulated"`` and no
      ``local_execution_result``.
    * ``local_cli`` — runs the Leo CLI for the module, attaches the
      structured ``local_execution_result``, and surfaces a
      ``proof_status`` / ``verification_status`` derived from the CLI
      outcome.

    The returned dict always carries the same keys regardless of mode
    so the API response shape is stable for clients.
    """
    program = PROGRAM_BY_MODULE[module]
    program_name = program["program_name"]
    transition_name = program["transition_name"]
    commitment = _input_commitment(inputs)

    base: Dict[str, Any] = {
        "execution_mode": aleo_execution_adapter.get_execution_mode(),
        "program_name": program_name,
        "transition_name": transition_name,
        "proof_status": PROOF_STATUS_SIMULATED,
        "verification_status": VERIFICATION_STATUS_PENDING,
        "input_commitment": commitment,
        "proof_reference": _proof_reference(program_name, commitment),
        "local_execution_result": None,
    }

    if base["execution_mode"] == aleo_execution_adapter.EXECUTION_MODE_SIMULATED:
        return base

    # local_cli — invoke the Leo CLI via the execution adapter. The
    # returned ``local_execution_result`` carries only redacted input
    # metadata; raw private values never appear here.
    execution = aleo_execution_adapter.execute(module, inputs)
    base["local_execution_result"] = execution

    status = execution.get("execution_status")
    if status == aleo_execution_adapter.STATUS_SUCCESS:
        base["proof_status"] = PROOF_STATUS_LOCAL_EXECUTED
        base["verification_status"] = VERIFICATION_STATUS_LOCAL_VERIFIED
    else:
        base["proof_status"] = PROOF_STATUS_LOCAL_FAILED
        base["verification_status"] = VERIFICATION_STATUS_LOCAL_FAILED

    return base
