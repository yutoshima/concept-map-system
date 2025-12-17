"""Tests for base algorithm class."""

import tempfile

import pytest

from concept_map_system.core import BaseAlgorithm


class DummyAlgorithm(BaseAlgorithm):
    """Dummy algorithm for testing."""

    def __init__(self):
        super().__init__(name="dummy", description="Dummy algorithm for testing")

    def execute(self, master_file: str, student_file: str, **kwargs):
        """Execute dummy algorithm."""
        return {"method": "Dummy", "result": "success"}

    def get_supported_options(self):
        """Get supported options."""
        return {"verbose": {"type": bool, "default": False, "help": "Verbose output"}}


class TestBaseAlgorithm:
    """Test cases for BaseAlgorithm."""

    def test_algorithm_creation(self):
        """Test creating an algorithm."""
        algo = DummyAlgorithm()
        assert algo.name == "dummy"
        assert algo.description == "Dummy algorithm for testing"

    def test_validate_files_success(self):
        """Test file validation with existing files."""
        with tempfile.NamedTemporaryFile(suffix=".csv") as master, tempfile.NamedTemporaryFile(
            suffix=".csv"
        ) as student:
            algo = DummyAlgorithm()
            assert algo.validate_files(master.name, student.name) is True

    def test_validate_files_missing_master(self):
        """Test file validation with missing master file."""
        with tempfile.NamedTemporaryFile(suffix=".csv") as student:
            algo = DummyAlgorithm()
            with pytest.raises(FileNotFoundError, match="模範解答ファイルが見つかりません"):
                algo.validate_files("/nonexistent/master.csv", student.name)

    def test_validate_files_missing_student(self):
        """Test file validation with missing student file."""
        with tempfile.NamedTemporaryFile(suffix=".csv") as master:
            algo = DummyAlgorithm()
            with pytest.raises(FileNotFoundError, match="生徒の回答ファイルが見つかりません"):
                algo.validate_files(master.name, "/nonexistent/student.csv")

    def test_get_info(self):
        """Test getting algorithm info."""
        algo = DummyAlgorithm()
        info = algo.get_info()
        assert info["name"] == "dummy"
        assert info["description"] == "Dummy algorithm for testing"
        assert "supported_options" in info
