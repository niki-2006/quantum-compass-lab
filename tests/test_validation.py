"""Tests executing the complete scientific validation suite."""

import pytest
from src.validation import ValidationSuite


def test_full_scientific_validation_suite():
    """Run all 12 validation suite tests and assert all pass."""
    suite = ValidationSuite()
    results = suite.run_all()

    assert len(results) >= 12

    failures = [r for r in results if not r.passed]
    if failures:
        msg = "\n".join([f"FAILED: {f.name} - {f.details}" for f in failures])
        pytest.fail(f"Validation tests failed:\n{msg}")
