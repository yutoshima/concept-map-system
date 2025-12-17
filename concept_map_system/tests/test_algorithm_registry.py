"""Tests for algorithm registry."""

from concept_map_system.core import AlgorithmRegistry, BaseAlgorithm, register_algorithm


# テスト用のダミーアルゴリズムを定義（外部依存なし）
@register_algorithm
class DummyAlgorithm1(BaseAlgorithm):
    """Dummy algorithm 1 for testing."""

    def __init__(self):
        super().__init__(name="test1", description="Test algorithm 1")

    def execute(self, master_file: str, student_file: str, **kwargs):
        """Execute test algorithm."""
        return {"method": "Test1", "result": "success"}

    def get_supported_options(self):
        """Get supported options."""
        return {"verbose": {"type": bool, "default": False, "help": "Verbose output"}}


@register_algorithm
class DummyAlgorithm2(BaseAlgorithm):
    """Dummy algorithm 2 for testing."""

    def __init__(self):
        super().__init__(name="test2", description="Test algorithm 2")

    def execute(self, master_file: str, student_file: str, **kwargs):
        """Execute test algorithm."""
        return {"method": "Test2", "result": "success"}

    def get_supported_options(self):
        """Get supported options."""
        return {}


class TestAlgorithmRegistry:
    """Test cases for AlgorithmRegistry."""

    def test_list_algorithms(self):
        """Test listing registered algorithms."""
        algorithms = AlgorithmRegistry.list_algorithms()
        assert isinstance(algorithms, list)
        assert len(algorithms) >= 2  # At least test1 and test2
        assert "test1" in algorithms
        assert "test2" in algorithms

    def test_get_algorithm(self):
        """Test getting an algorithm by name."""
        test1 = AlgorithmRegistry.get_algorithm("test1")
        assert test1 is not None
        assert test1.name == "test1"

    def test_get_nonexistent_algorithm(self):
        """Test getting a non-existent algorithm."""
        algo = AlgorithmRegistry.get_algorithm("nonexistent")
        assert algo is None

    def test_algorithm_info(self):
        """Test getting algorithm info."""
        info = AlgorithmRegistry.get_algorithm_info("test1")
        assert info is not None
        assert "description" in info
        assert "supported_options" in info
        assert isinstance(info["supported_options"], dict)
