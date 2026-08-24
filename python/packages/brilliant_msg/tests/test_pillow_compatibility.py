"""Packaging compatibility checks for the published brilliant-msg metadata."""

from importlib import metadata

from packaging.requirements import Requirement
from packaging.version import Version


def test_published_metadata_allows_pillow_12():
    """The published dependency requirement must admit the Pillow 12 line."""
    pillow_requirement = next(
        Requirement(requirement)
        for requirement in metadata.requires("brilliant-msg") or []
        if Requirement(requirement).name.lower() == "pillow"
    )

    assert Version("12.0.0") in pillow_requirement.specifier
