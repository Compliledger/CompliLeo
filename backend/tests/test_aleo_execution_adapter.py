"""Tests for ``app.services.aleo_execution_adapter`` (Phase 7)."""
from __future__ import annotations

import subprocess
from typing import Any, Dict
from unittest import mock

import pytest

from app.services import aleo_execution_adapter


# ---------------------------------------------------------------------------
# Mode resolution
# ---------------------------------------------------------------------------
def test_get_execution_mode_defaults_to_simulated(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("ALEO_EXECUTION_MODE", raising=False)
    assert aleo_execution_adapter.get_execution_mode() == "simulated"


def test_get_execution_mode_recognizes_local_cli(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "local_cli")
    assert aleo_execution_adapter.get_execution_mode() == "local_cli"


def test_get_execution_mode_falls_back_to_simulated_for_unknown_value(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "mainnet_yolo")
    assert aleo_execution_adapter.get_execution_mode() == "simulated"


# ---------------------------------------------------------------------------
# Helpers / formatting
# ---------------------------------------------------------------------------
def test_format_u64_rejects_negative():
    with pytest.raises(ValueError):
        aleo_execution_adapter._format_u64(-1)


def test_format_u64_serializes_with_suffix():
    assert aleo_execution_adapter._format_u64(123) == "123u64"


def test_format_bool_serializes_lowercase():
    assert aleo_execution_adapter._format_bool(True) == "true"
    assert aleo_execution_adapter._format_bool(False) == "false"


# ---------------------------------------------------------------------------
# Simulated mode (via ``execute``)
# ---------------------------------------------------------------------------
def test_execute_simulated_mode_returns_placeholder(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "simulated")
    out = aleo_execution_adapter.execute(
        "tokenproof",
        {"issuer_approved": True, "asset_type_supported": False},
    )
    assert out["execution_mode"] == "simulated"
    assert out["program_name"] == "tokenproofx1.aleo"
    assert out["transition_name"] == "verify_token"
    assert out["execution_status"] == "simulated"
    assert out["error_message"] is None
    assert out["raw_output"] is None
    assert out["result"] is None
    assert out["inputs_redacted"]["inputs_redacted"] is True
    assert out["inputs_redacted"]["input_names"] == [
        "issuer_approved",
        "asset_type_supported",
    ]


def test_execute_simulated_mode_does_not_invoke_subprocess(
    monkeypatch: pytest.MonkeyPatch,
):
    """Simulated mode must never shell out, even if Leo is installed."""
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "simulated")
    with mock.patch.object(
        aleo_execution_adapter.subprocess, "run", autospec=True
    ) as run_spy, mock.patch.object(
        aleo_execution_adapter.shutil, "which", autospec=True
    ) as which_spy:
        which_spy.return_value = "/usr/local/bin/leo"
        aleo_execution_adapter.execute(
            "solvencyproof", {"reserves": 10, "liabilities": 5}
        )
    run_spy.assert_not_called()


def test_execute_unknown_module_raises(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "simulated")
    with pytest.raises(KeyError):
        aleo_execution_adapter.execute("nope", {})


# ---------------------------------------------------------------------------
# local_cli mode — Leo CLI not installed
# ---------------------------------------------------------------------------
def test_local_cli_missing_leo_returns_structured_error(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "local_cli")
    with mock.patch.object(
        aleo_execution_adapter.shutil, "which", return_value=None
    ):
        out = aleo_execution_adapter.run_tokenproof_local(True, True)
    assert out["execution_mode"] == "local_cli"
    assert out["execution_status"] == "cli_not_found"
    assert "Leo CLI not found" in out["error_message"]
    assert out["raw_output"] is None
    assert out["result"] is None
    # Privacy: no raw input values appear anywhere in the metadata.
    assert out["inputs_redacted"]["inputs_redacted"] is True
    assert "true" not in str(out["error_message"]).lower().split()


# ---------------------------------------------------------------------------
# local_cli mode — successful CLI execution
# ---------------------------------------------------------------------------
def _completed(stdout: str = "", stderr: str = "", returncode: int = 0):
    return subprocess.CompletedProcess(
        args=["leo"], returncode=returncode, stdout=stdout, stderr=stderr
    )


def _make_run_side_effect(execute_run: subprocess.CompletedProcess):
    """Return a ``subprocess.run`` side effect that responds to both
    ``leo --help`` (used to probe subcommand support) and the actual
    ``leo execute|run`` call.
    """

    def side_effect(cmd, *args, **kwargs):
        # First positional: the command list.
        if "--help" in cmd:
            return _completed(stdout="USAGE:\n  leo execute <NAME>\n  leo run <NAME>\n")
        return execute_run

    return side_effect


def test_local_cli_success_parses_output(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "local_cli")
    fake_stdout = "Leo ✅ Compiled\n\n➡️  Output\n\ntrue\n\nDone\n"
    with mock.patch.object(
        aleo_execution_adapter.shutil, "which", return_value="/fake/leo"
    ), mock.patch.object(
        aleo_execution_adapter.subprocess,
        "run",
        side_effect=_make_run_side_effect(_completed(stdout=fake_stdout)),
    ):
        out = aleo_execution_adapter.run_solvencyproof_local(1000, 750)

    assert out["execution_status"] == "success"
    assert out["execution_mode"] == "local_cli"
    assert out["program_name"] == "solvencypx1.aleo"
    assert out["transition_name"] == "prove_solvency"
    assert out["raw_output"] == fake_stdout
    assert out["result"] == "true"
    assert out["error_message"] is None


def test_local_cli_failure_returns_structured_error(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "local_cli")
    with mock.patch.object(
        aleo_execution_adapter.shutil, "which", return_value="/fake/leo"
    ), mock.patch.object(
        aleo_execution_adapter.subprocess,
        "run",
        side_effect=_make_run_side_effect(
            _completed(stderr="Error: type mismatch", returncode=1)
        ),
    ):
        out = aleo_execution_adapter.run_compliguard_local(True, False)

    assert out["execution_status"] == "cli_error"
    assert out["error_message"] == "Error: type mismatch"
    assert out["result"] is None


def test_local_cli_timeout_returns_structured_error(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "local_cli")

    def side_effect(cmd, *args, **kwargs):
        if "--help" in cmd:
            return _completed(stdout="USAGE:\n  leo run <NAME>\n")
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=1)

    with mock.patch.object(
        aleo_execution_adapter.shutil, "which", return_value="/fake/leo"
    ), mock.patch.object(
        aleo_execution_adapter.subprocess, "run", side_effect=side_effect
    ):
        out = aleo_execution_adapter.run_tokenproof_local(True, True)

    assert out["execution_status"] == "timeout"
    assert "did not complete" in out["error_message"]


def test_local_cli_unexpected_oserror_returns_structured_error(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "local_cli")

    def side_effect(cmd, *args, **kwargs):
        if "--help" in cmd:
            return _completed(stdout="USAGE:\n  leo run <NAME>\n")
        raise OSError("disk on fire")

    with mock.patch.object(
        aleo_execution_adapter.shutil, "which", return_value="/fake/leo"
    ), mock.patch.object(
        aleo_execution_adapter.subprocess, "run", side_effect=side_effect
    ):
        out = aleo_execution_adapter.run_solvencyproof_local(1, 1)

    assert out["execution_status"] == "unexpected_error"
    # Generic error message, no leak of arguments.
    assert "OSError" in out["error_message"]
    assert "1u64" not in out["error_message"]


# ---------------------------------------------------------------------------
# Privacy: raw private inputs must never appear in returned metadata
# ---------------------------------------------------------------------------
def test_local_cli_does_not_expose_private_inputs(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "local_cli")
    with mock.patch.object(
        aleo_execution_adapter.shutil, "which", return_value="/fake/leo"
    ), mock.patch.object(
        aleo_execution_adapter.subprocess,
        "run",
        side_effect=_make_run_side_effect(_completed(stdout="ok\n")),
    ):
        out = aleo_execution_adapter.run_solvencyproof_local(
            reserves=987654321, liabilities=123456789
        )

    # The serialized metadata MUST NOT contain either raw value, in any
    # form (decimal int, ``u64`` literal, JSON, etc.).
    serialized = repr(out)
    assert "987654321" not in serialized
    assert "123456789" not in serialized
    assert "987654321u64" not in serialized
    assert "123456789u64" not in serialized
    # And the redaction flag is set.
    assert out["inputs_redacted"]["inputs_redacted"] is True
    assert out["inputs_redacted"]["input_names"] == ["reserves", "liabilities"]


# ---------------------------------------------------------------------------
# Metadata shape contract
# ---------------------------------------------------------------------------
EXPECTED_KEYS = {
    "execution_mode",
    "program_name",
    "transition_name",
    "inputs_redacted",
    "result",
    "raw_output",
    "execution_status",
    "error_message",
}


@pytest.mark.parametrize(
    "runner,args",
    [
        (aleo_execution_adapter.run_tokenproof_local, (True, False)),
        (aleo_execution_adapter.run_solvencyproof_local, (10, 5)),
        (aleo_execution_adapter.run_compliguard_local, (True, False)),
    ],
)
def test_local_runners_return_expected_metadata_keys(
    monkeypatch: pytest.MonkeyPatch, runner, args
):
    """Every per-module runner must return the documented field set."""
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "local_cli")
    with mock.patch.object(
        aleo_execution_adapter.shutil, "which", return_value=None
    ):
        out: Dict[str, Any] = runner(*args)
    assert EXPECTED_KEYS.issubset(out.keys())


def test_simulated_metadata_returns_expected_keys(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("ALEO_EXECUTION_MODE", "simulated")
    out = aleo_execution_adapter.execute(
        "compliguard",
        {"anomaly_score_below_threshold": True, "critical_alert_open": False},
    )
    assert EXPECTED_KEYS.issubset(out.keys())
