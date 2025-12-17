#!/usr/bin/env python3

"""
概念マップ採点統合システム - アルゴリズムモジュール

このモジュールは、利用可能なすべての採点アルゴリズムをインポートし、
システムに登録します。

利用可能なアルゴリズム:
    - McClureAlgorithm: McClure (1999) 方式
    - NovakAlgorithm: Novak方式
    - WLEAAlgorithm: WLEA (Weighted Link Evaluation Algorithm) 方式
"""

import logging
import sys

from ..core.logging_config import get_logger

# ロガーの設定
logger = get_logger(__name__)

__all__ = []

# ============================================================================
# アルゴリズムのインポート
# ============================================================================

# McClureアルゴリズム
try:
    from .mcclure_algorithm import McClureAlgorithm

    __all__.append("McClureAlgorithm")
except ImportError as e:
    logger.warning(f"McClureアルゴリズムのインポートに失敗しました: {e}")

# Novakアルゴリズム
try:
    from .novak_algorithm import NovakAlgorithm

    __all__.append("NovakAlgorithm")
except ImportError as e:
    logger.warning(f"Novakアルゴリズムのインポートに失敗しました: {e}")

# WLEAアルゴリズム
try:
    from .wlea_algorithm import WLEAAlgorithm

    __all__.append("WLEAAlgorithm")
except ImportError as e:
    logger.warning(f"WLEAアルゴリズムのインポートに失敗しました: {e}")

# Hybridアルゴリズム (McClure + Jaccard)
try:
    from .hybrid_algorithm import HybridAlgorithm

    __all__.append("HybridAlgorithm")
except ImportError as e:
    logger.warning(f"Hybridアルゴリズムのインポートに失敗しました: {e}")

# ============================================================================
# コアモジュールのエクスポート（他のモジュールから利用可能にする）
# ============================================================================

# 基底クラスとユーティリティをエクスポート
__all__.extend(
    [
        "AlgorithmExecutionError",
        "BaseConceptMapScorer",
        "CSVLoadError",
        "ConceptMapError",
    ]
)

try:
    from ..core.exceptions import (
        AlgorithmExecutionError,
        CSVLoadError,
    )
    from ..core.exceptions import (
        ConceptMapSystemError as ConceptMapError,
    )
    from .concept_map_core import BaseConceptMapScorer
except ImportError as e:
    logger.error(f"コアモジュールのインポートに失敗しました: {e}")


# WLEAコアもエクスポート（カスタムアルゴリズム用）
__all__.extend(
    [
        "Link",
        "LinkCSVError",
        "calculate_f_value",
        "calculate_optimal_matching_bruteforce",
        "compare_links",
        "create_links_from_csv",
    ]
)

try:
    from .wlea_core import (
        Link,
        LinkCSVError,
        calculate_f_value,
        calculate_optimal_matching_bruteforce,
        compare_links,
        create_links_from_csv,
    )
except ImportError as e:
    logger.warning(f"WLEAコアモジュールのインポートに失敗しました: {e}")


# ============================================================================
# カスタムアルゴリズムの追加
# ============================================================================

# カスタムアルゴリズムを追加する場合は、ここにインポートを追加してください
# 例:
# try:
#     from .custom_algorithm import CustomAlgorithm
#     __all__.append("CustomAlgorithm")
# except ImportError as e:
#     logger.warning(f"カスタムアルゴリズムのインポートに失敗しました: {e}")
