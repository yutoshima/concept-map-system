#!/usr/bin/env python3

"""
概念マップ採点統合システム

McClure、Novak、WLEA、data_validation、カスタムアルゴリズムを
統合したシステムです。
"""

__version__ = "1.0.0"
__author__ = "Concept Map System Team"

from .core import (
    AlgorithmRegistry,
    BaseAlgorithm,
    ExecutionResult,
    ParallelExecutor,
    SequentialExecutor,
    register_algorithm,
)

__all__ = [
    "AlgorithmRegistry",
    "BaseAlgorithm",
    "ExecutionResult",
    "ParallelExecutor",
    "SequentialExecutor",
    "__author__",
    "__version__",
    "register_algorithm",
]
