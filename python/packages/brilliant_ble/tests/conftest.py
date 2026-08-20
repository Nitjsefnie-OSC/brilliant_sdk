"""Keeps a bare `pytest` run hardware-free in this directory.

Most `test_*.py` files here are standalone device-exercise scripts, not pytest
tests: they parse argv and call `asyncio.run(main())` at module level, so
merely importing them (which pytest does during collection) would connect to a
device over BLE — or hang looking for one. They are excluded from collection
and are meant to be run directly:

    uv run python packages/brilliant_ble/tests/test_camera.py --name Halo

The genuine pytest modules remain collected. Of those, the ones that need a
real device are skipped unless BRILLIANT_DEVICE=1 is set:

    BRILLIANT_DEVICE=1 uv run pytest packages/brilliant_ble/tests/
"""

import os
import re
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent

# Genuine pytest modules that talk to a real device over BLE.
DEVICE_TEST_MODULES = {"test_ble"}

RUN_DEVICE_TESTS = os.environ.get("BRILLIANT_DEVICE") == "1"

# A module-level (column-0) asyncio.run / sys.exit call marks a file as a
# standalone script: importing it would execute it.
_SCRIPT_PATTERN = re.compile(r"^(?:asyncio\.run|sys\.exit)\(", re.MULTILINE)

collect_ignore = [
    p.name
    for p in TESTS_DIR.glob("test_*.py")
    if _SCRIPT_PATTERN.search(p.read_text())
]

_skip_device = pytest.mark.skip(
    reason="needs a Brilliant device over BLE; set BRILLIANT_DEVICE=1 to run"
)


def pytest_collection_modifyitems(config, items):
    for item in items:
        if Path(item.fspath).stem in DEVICE_TEST_MODULES:
            item.add_marker(pytest.mark.device)
            if not RUN_DEVICE_TESTS:
                item.add_marker(_skip_device)
