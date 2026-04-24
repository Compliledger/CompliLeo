"""Aleo adapter abstraction.

This module abstracts how CompliLeo would eventually invoke the Aleo
network to execute and verify the ``tokenproofx1.aleo``,
``solvencypx1.aleo``, and ``compliguardx1.aleo`` programs.

For the MVP we do **not** call out to the Aleo network. Instead we:

* normalize backend request models into the typed inputs each Aleo
  transition expects, and
* return placeholder proof / verification metadata so downstream
  components (e.g. the proof-bundle service) can be wired up against a
  stable interface.

When real Aleo execution lands, only the bodies of
:func:`generate_proof_placeholder` and :func:`verify_proof_placeholder`
need to change; the public surface stays the same.
"""
from __future__ import annotations

from typing import Any, Dict, Literal

from app.models import (
    CompliGuardRequest,
    ModuleName,
    SolvencyProofRequest,
    TokenProofRequest,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PROOF_STATUS_SIMULATED = "simulated"
VERIFICATION_STATUS_PENDING = "pending_aleo_execution"

# Mapping from logical module name -> (aleo program name, transition name).
_PROGRAM_BY_MODULE: Dict[str, Dict[str, str]] = {
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
def prepare_tokenproof_input(req: TokenProofRequest) -> Dict[str, Any]:
    """Translate a ``TokenProofRequest`` into ``check_token_admission`` inputs.

    The Aleo transition expects two ``bool`` arguments. We mirror the
    transition's parameter names so this dict can be consumed verbatim by
    a future Aleo executor.
    """
    return {
        "issuer_approved": bool(req.issuer_approved),
        "asset_type_supported": bool(req.asset_type_supported),
    }


def prepare_solvencyproof_input(req: SolvencyProofRequest) -> Dict[str, Any]:
    """Translate a ``SolvencyProofRequest`` into ``check_solvency`` inputs.

    The Aleo transition expects two ``u64`` values. We keep them as Python
    ``int`` here; serialization to Aleo's ``u64`` literal form (e.g.
    ``"123u64"``) is the executor's responsibility.
    """
    return {
        "reserves": int(req.reserves),
        "liabilities": int(req.liabilities),
    }


def prepare_compliguard_input(req: CompliGuardRequest) -> Dict[str, Any]:
    """Translate a ``CompliGuardRequest`` into ``check_system_health`` inputs."""
    return {
        "anomaly_score_below_threshold": bool(req.anomaly_score_below_threshold),
        "critical_alert_open": bool(req.critical_alert_open),
    }


# ---------------------------------------------------------------------------
# Proof generation / verification placeholders
# ---------------------------------------------------------------------------
def _program_metadata(module: ModuleName) -> Dict[str, str]:
    try:
        return _PROGRAM_BY_MODULE[module]
    except KeyError as exc:  # pragma: no cover - guarded by Literal type
        raise ValueError(f"unknown module: {module!r}") from exc


def generate_proof_placeholder(
    module: ModuleName,
    inputs: Dict[str, Any],
) -> Dict[str, Any]:
    """Return placeholder proof metadata for ``module``.

    Does **not** contact the Aleo network. The returned dict captures the
    program / transition that *would* be executed, the inputs that *would*
    be passed in, and a ``proof_status`` indicating that this is a
    simulated (non-cryptographic) placeholder.
    """
    meta = _program_metadata(module)
    return {
        "program_name": meta["program_name"],
        "transition_name": meta["transition_name"],
        "inputs": dict(inputs),
        "proof_status": PROOF_STATUS_SIMULATED,
    }


def verify_proof_placeholder(proof: Dict[str, Any]) -> Dict[str, Any]:
    """Return placeholder verification metadata for ``proof``.

    Does **not** contact the Aleo network. Echoes the program / transition
    from the proof and reports a ``verification_status`` indicating that
    real on-chain verification has not yet been executed.
    """
    return {
        "program_name": proof.get("program_name"),
        "transition_name": proof.get("transition_name"),
        "verification_status": VERIFICATION_STATUS_PENDING,
    }
