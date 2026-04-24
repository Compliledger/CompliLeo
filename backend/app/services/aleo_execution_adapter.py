"""Aleo execution adapter — Phase 7 real-execution seam.

This module provides a thin, well-typed shim between the CompliLeo
backend and the actual Leo CLI. It supports two modes selected by the
``ALEO_EXECUTION_MODE`` environment variable:

* ``simulated`` (default) — return placeholder execution metadata
  without invoking any external tool. Safe to run in CI and on
  developer machines that have not installed the Leo toolchain.
* ``local_cli`` — locate the on-disk Leo program from
  :mod:`app.services.aleo_program_registry` and invoke the local
  ``leo`` CLI via :mod:`subprocess` to execute the relevant transition.
  Captures ``stdout``/``stderr`` and returns structured metadata.

Privacy
-------
Private inputs are **never** logged and are **never** echoed back in
the returned metadata. The returned dict reports
``"inputs_redacted": True`` to make this explicit. Callers (FastAPI
routers, the proof-bundle service, etc.) should propagate the
returned structure as-is and must not re-inject the original inputs.

A future ``testnet`` mode will submit proofs for Aleo network
verification; it is intentionally **not** implemented in this MVP.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any, Dict, List, Mapping, Optional

from app.services import aleo_program_registry

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
EXECUTION_MODE_SIMULATED = "simulated"
EXECUTION_MODE_LOCAL_CLI = "local_cli"

#: Environment variable that selects the execution mode.
ENV_VAR_EXECUTION_MODE = "ALEO_EXECUTION_MODE"

#: Maximum seconds to wait for the Leo CLI before giving up. Real proof
#: generation can be slow; this is generous but bounded so a hung CLI
#: cannot wedge a request indefinitely.
DEFAULT_LEO_CLI_TIMEOUT_SECONDS = 120

#: ``execution_status`` values emitted by this adapter.
STATUS_SIMULATED = "simulated"
STATUS_SUCCESS = "success"
STATUS_CLI_NOT_FOUND = "cli_not_found"
STATUS_CLI_ERROR = "cli_error"
STATUS_TIMEOUT = "timeout"
STATUS_UNEXPECTED_ERROR = "unexpected_error"


# ---------------------------------------------------------------------------
# Mode resolution
# ---------------------------------------------------------------------------
def get_execution_mode() -> str:
    """Return the currently configured Aleo execution mode.

    Falls back to :data:`EXECUTION_MODE_SIMULATED` when the environment
    variable is unset or set to an unknown value, so the backend always
    has a safe default.
    """
    mode = os.environ.get(ENV_VAR_EXECUTION_MODE, EXECUTION_MODE_SIMULATED).strip()
    if mode not in (EXECUTION_MODE_SIMULATED, EXECUTION_MODE_LOCAL_CLI):
        return EXECUTION_MODE_SIMULATED
    return mode


# ---------------------------------------------------------------------------
# Aleo literal formatting
# ---------------------------------------------------------------------------
def _format_bool(value: bool) -> str:
    """Format a Python ``bool`` as a Leo ``bool`` literal."""
    return "true" if value else "false"


def _format_u64(value: int) -> str:
    """Format a Python ``int`` as a Leo ``u64`` literal."""
    if value < 0:
        raise ValueError("u64 values must be non-negative")
    return f"{int(value)}u64"


# ---------------------------------------------------------------------------
# Leo CLI invocation
# ---------------------------------------------------------------------------
def _build_redacted_inputs(input_names: List[str]) -> Dict[str, Any]:
    """Return a privacy-preserving description of the inputs.

    Records only the *names* of the inputs that were supplied; the
    actual values are never included.
    """
    return {
        "inputs_redacted": True,
        "input_names": list(input_names),
    }


def _resolve_program_dir(module: str) -> str:
    """Return the absolute path to a module's Leo project directory.

    The Leo CLI must be invoked from the directory that contains
    ``program.json`` (i.e. the program root, which is the parent of
    ``src/main.leo``).
    """
    main_leo = aleo_program_registry.resolve_local_path(module)
    return str(main_leo.parent.parent)


def _select_cli_subcommand(leo_executable: str) -> str:
    """Return the subcommand to use against the local Leo CLI.

    Newer Leo CLIs expose ``leo execute`` for proof execution while
    older ones only provide ``leo run``. We probe ``leo --help`` once
    per invocation; on any failure we fall back to ``run`` since it is
    supported by every released Leo CLI.
    """
    try:
        proc = subprocess.run(
            [leo_executable, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "run"
    help_text = (proc.stdout or "") + (proc.stderr or "")
    if "execute" in help_text:
        return "execute"
    return "run"


def _parse_leo_output(stdout: str) -> Optional[str]:
    """Best-effort extraction of the public output from ``leo`` stdout.

    Leo prints the transition outputs after a line containing
    ``Output`` (older builds) or ``Outputs`` (newer builds). We scan
    for the first non-empty line after such a marker. Returns ``None``
    when no marker is present so callers can fall back to the raw
    output instead of guessing.
    """
    if not stdout:
        return None
    lines = stdout.splitlines()
    for idx, line in enumerate(lines):
        # Match either "Output" / "Outputs" at the start of the trimmed
        # line *or* anywhere on the line (Leo prints headings like
        # ``➡️  Output`` with leading marker glyphs).
        lowered = line.lower()
        if "output" in lowered and (
            line.strip().lower().startswith("output") or "➡" in line
        ):
            for candidate in lines[idx + 1:]:
                value = candidate.strip()
                if value:
                    return value
            return None
    return None


def _run_local_cli(
    module: str,
    cli_args: List[str],
    input_names: List[str],
    timeout: int = DEFAULT_LEO_CLI_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    """Run a Leo transition locally via the ``leo`` CLI.

    Parameters
    ----------
    module:
        Logical CompliLeo module name (e.g. ``"tokenproof"``). Used to
        locate the on-disk Leo program directory.
    cli_args:
        Positional arguments to pass to the Leo CLI *after* the
        transition name. These must already be formatted as Leo
        literals (e.g. ``"true"``, ``"1000u64"``). They are considered
        sensitive: this function does not log them and they are not
        echoed in the returned metadata.
    input_names:
        Ordered names of the inputs supplied — recorded in the
        returned ``inputs_redacted`` block so callers can describe
        *which* fields were provided without leaking *what* they were.
    timeout:
        Maximum seconds to wait for the CLI before terminating it.

    Returns
    -------
    dict
        Structured execution metadata. Always includes
        ``execution_mode``, ``program_name``, ``transition_name``,
        ``inputs_redacted``, ``result``, ``raw_output``,
        ``execution_status``, and ``error_message``.
    """
    program = aleo_program_registry.get_program(module)
    program_name = program["program_name"]
    transition_name = program["transition_name"]
    redacted = _build_redacted_inputs(input_names)

    base: Dict[str, Any] = {
        "execution_mode": EXECUTION_MODE_LOCAL_CLI,
        "program_name": program_name,
        "transition_name": transition_name,
        "inputs_redacted": redacted,
        "result": None,
        "raw_output": None,
        "execution_status": STATUS_UNEXPECTED_ERROR,
        "error_message": None,
    }

    leo_executable = shutil.which("leo")
    if leo_executable is None:
        base["execution_status"] = STATUS_CLI_NOT_FOUND
        base["error_message"] = (
            "Leo CLI not found on PATH. Install the Leo toolchain "
            "(https://developer.aleo.org/leo/installation) to enable "
            "ALEO_EXECUTION_MODE=local_cli."
        )
        return base

    try:
        program_dir = _resolve_program_dir(module)
    except aleo_program_registry.UnknownAleoModuleError as exc:
        base["execution_status"] = STATUS_UNEXPECTED_ERROR
        base["error_message"] = str(exc)
        return base

    subcommand = _select_cli_subcommand(leo_executable)
    cmd = [leo_executable, subcommand, transition_name, *cli_args]

    try:
        proc = subprocess.run(
            cmd,
            cwd=program_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        base["execution_status"] = STATUS_TIMEOUT
        base["error_message"] = (
            f"Leo CLI did not complete within {timeout} seconds."
        )
        return base
    except (OSError, subprocess.SubprocessError) as exc:
        # Generic message — never include cli_args, which may be private.
        base["execution_status"] = STATUS_UNEXPECTED_ERROR
        base["error_message"] = f"Failed to invoke Leo CLI: {type(exc).__name__}"
        return base

    base["raw_output"] = proc.stdout or ""
    if proc.returncode != 0:
        base["execution_status"] = STATUS_CLI_ERROR
        # stderr from a Leo build/execute typically contains diagnostics
        # about the program (paths, transition names, type errors) — not
        # the private input values themselves — so it is safe to surface.
        base["error_message"] = (proc.stderr or "").strip() or (
            f"Leo CLI exited with status {proc.returncode}."
        )
        return base

    base["execution_status"] = STATUS_SUCCESS
    base["result"] = _parse_leo_output(proc.stdout or "")
    return base


# ---------------------------------------------------------------------------
# Simulated-mode metadata
# ---------------------------------------------------------------------------
def _simulated_metadata(module: str, input_names: List[str]) -> Dict[str, Any]:
    """Return placeholder execution metadata for the ``simulated`` mode."""
    program = aleo_program_registry.get_program(module)
    return {
        "execution_mode": EXECUTION_MODE_SIMULATED,
        "program_name": program["program_name"],
        "transition_name": program["transition_name"],
        "inputs_redacted": _build_redacted_inputs(input_names),
        "result": None,
        "raw_output": None,
        "execution_status": STATUS_SIMULATED,
        "error_message": None,
    }


# ---------------------------------------------------------------------------
# Public per-module entry points
# ---------------------------------------------------------------------------
def run_tokenproof_local(
    issuer_approved: bool,
    asset_type_supported: bool,
) -> Dict[str, Any]:
    """Execute the ``tokenproof`` transition locally via the Leo CLI.

    Inputs are private and are never logged or returned. See module
    docstring for the structure of the returned metadata.
    """
    input_names = ["issuer_approved", "asset_type_supported"]
    cli_args = [_format_bool(issuer_approved), _format_bool(asset_type_supported)]
    return _run_local_cli("tokenproof", cli_args, input_names)


def run_solvencyproof_local(reserves: int, liabilities: int) -> Dict[str, Any]:
    """Execute the ``solvencyproof`` transition locally via the Leo CLI."""
    input_names = ["reserves", "liabilities"]
    cli_args = [_format_u64(reserves), _format_u64(liabilities)]
    return _run_local_cli("solvencyproof", cli_args, input_names)


def run_compliguard_local(
    anomaly_score_below_threshold: bool,
    critical_alert_open: bool,
) -> Dict[str, Any]:
    """Execute the ``compliguard`` transition locally via the Leo CLI."""
    input_names = ["anomaly_score_below_threshold", "critical_alert_open"]
    cli_args = [
        _format_bool(anomaly_score_below_threshold),
        _format_bool(critical_alert_open),
    ]
    return _run_local_cli("compliguard", cli_args, input_names)


# ---------------------------------------------------------------------------
# Mode-aware dispatcher used by ``aleo_adapter``
# ---------------------------------------------------------------------------
#: Map module name -> (local_cli runner, ordered input field names).
_MODULE_RUNNERS = {
    "tokenproof": (run_tokenproof_local, ["issuer_approved", "asset_type_supported"]),
    "solvencyproof": (run_solvencyproof_local, ["reserves", "liabilities"]),
    "compliguard": (
        run_compliguard_local,
        ["anomaly_score_below_threshold", "critical_alert_open"],
    ),
}


def execute(module: str, inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Dispatch execution for ``module`` according to the configured mode.

    In ``simulated`` mode this returns placeholder metadata without
    touching the Leo CLI. In ``local_cli`` mode it forwards to the
    per-module runner with the typed inputs from ``inputs``.

    The returned dict always carries the same keys regardless of mode
    so downstream consumers can render a consistent shape.
    """
    if module not in _MODULE_RUNNERS:
        raise aleo_program_registry.UnknownAleoModuleError(
            f"Unknown Aleo module '{module}'. "
            f"Known modules: {sorted(_MODULE_RUNNERS)}"
        )

    runner, input_names = _MODULE_RUNNERS[module]
    mode = get_execution_mode()
    if mode == EXECUTION_MODE_SIMULATED:
        return _simulated_metadata(module, input_names)

    # local_cli — pull inputs in the canonical order so positional CLI
    # args line up with the transition signature.
    try:
        ordered = [inputs[name] for name in input_names]
    except KeyError as exc:
        raise KeyError(
            f"Missing input {exc!s} for module '{module}'. "
            f"Required inputs: {input_names}"
        ) from None
    return runner(*ordered)
