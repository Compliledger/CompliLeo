"""Tests for the Aleo program registry (Backend Phase 4)."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import aleo_program_registry
from app.services.aleo_program_registry import (
    ALEO_PROGRAMS,
    UnknownAleoModuleError,
)

client = TestClient(app)


# Repo root: backend/tests/test_*.py -> backend/tests -> backend -> repo
_REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Registry contents
# ---------------------------------------------------------------------------
def test_registry_contains_all_three_modules():
    assert set(ALEO_PROGRAMS) == {"tokenproof", "solvencyproof", "compliguard"}


@pytest.mark.parametrize(
    "module, program_name, transition_name",
    [
        ("tokenproof", "tokenproofx1.aleo", "verify_token"),
        ("solvencyproof", "solvencypx1.aleo", "prove_solvency"),
        ("compliguard", "compliguardx1.aleo", "prove_health"),
    ],
)
def test_registry_program_and_transition_names(
    module: str, program_name: str, transition_name: str
):
    entry = ALEO_PROGRAMS[module]
    assert entry["module"] == module
    assert entry["program_name"] == program_name
    assert entry["transition_name"] == transition_name
    assert entry["description"]  # non-empty


@pytest.mark.parametrize("module", sorted(ALEO_PROGRAMS))
def test_registry_local_paths_exist_relative_to_repo_root(module: str):
    """Every ``local_path`` should resolve to an existing ``main.leo`` file."""
    resolved = aleo_program_registry.resolve_local_path(module)
    assert resolved.is_file(), f"missing Leo program for {module}: {resolved}"
    assert resolved.suffix == ".leo"
    # Sanity: file is inside the repo's ``aleo/`` directory.
    assert (_REPO_ROOT / "aleo") in resolved.parents


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------
def test_get_program_returns_a_copy():
    entry = aleo_program_registry.get_program("tokenproof")
    entry["program_name"] = "mutated.aleo"
    # Mutating the returned dict must not affect the registry.
    assert ALEO_PROGRAMS["tokenproof"]["program_name"] == "tokenproofx1.aleo"


def test_get_program_unknown_module_raises_clean_error():
    with pytest.raises(UnknownAleoModuleError) as exc_info:
        aleo_program_registry.get_program("does_not_exist")
    msg = str(exc_info.value)
    assert "does_not_exist" in msg
    assert "tokenproof" in msg  # message lists known modules


def test_unknown_module_error_is_a_keyerror():
    """Back-compat: ``KeyError`` callers keep working."""
    with pytest.raises(KeyError):
        aleo_program_registry.get_program("nope")


def test_list_programs_returns_all_entries():
    programs = aleo_program_registry.list_programs()
    assert len(programs) == len(ALEO_PROGRAMS)
    assert {p["module"] for p in programs} == set(ALEO_PROGRAMS)


# ---------------------------------------------------------------------------
# HTTP endpoints
# ---------------------------------------------------------------------------
def test_get_programs_endpoint_returns_all_modules():
    r = client.get("/api/aleo/programs")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert {entry["module"] for entry in body} == {
        "tokenproof",
        "solvencyproof",
        "compliguard",
    }
    for entry in body:
        for key in (
            "module",
            "program_name",
            "transition_name",
            "local_path",
            "description",
        ):
            assert key in entry, f"missing field {key} for module {entry.get('module')}"


@pytest.mark.parametrize(
    "module, program_name, transition_name",
    [
        ("tokenproof", "tokenproofx1.aleo", "verify_token"),
        ("solvencyproof", "solvencypx1.aleo", "prove_solvency"),
        ("compliguard", "compliguardx1.aleo", "prove_health"),
    ],
)
def test_get_program_endpoint_returns_one_module(
    module: str, program_name: str, transition_name: str
):
    r = client.get(f"/api/aleo/programs/{module}")
    assert r.status_code == 200
    body = r.json()
    assert body["module"] == module
    assert body["program_name"] == program_name
    assert body["transition_name"] == transition_name


def test_get_program_endpoint_unknown_module_returns_404():
    r = client.get("/api/aleo/programs/does_not_exist")
    assert r.status_code == 404
    assert "does_not_exist" in r.json()["detail"]
