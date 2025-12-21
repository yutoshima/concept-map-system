#!/usr/bin/env python3

"""
概念マップ採点統合システム - アルゴリズムモジュール

このモジュールは、利用可能なすべての採点アルゴリズムをインポートし、
システムに登録します。

利用可能なアルゴリズム:
    - McClureAlgorithm: McClure (1999) 方式
    - NovakAlgorithm: Novak方式
    - LEAAlgorithm: LEA (Link Evaluation Algorithm) 方式
"""

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

# LEAアルゴリズム
try:
    from .lea_algorithm import LEAAlgorithm

    __all__.append("LEAAlgorithm")
except ImportError as e:
    logger.warning(f"LEAアルゴリズムのインポートに失敗しました: {e}")

# ============================================================================
# コアモジュールのエクスポート（他のモジュールから利用可能にする）
# ============================================================================

# 基底クラスとユーティリティをインポート
try:
    from ..core.exceptions import (
        AlgorithmExecutionError,
        CSVLoadError,
    )
    from ..core.exceptions import (
        ConceptMapSystemError as ConceptMapError,
    )
    from .concept_map_core import BaseConceptMapScorer

    # インポート成功後に__all__に追加
    __all__.extend(
        [
            "AlgorithmExecutionError",
            "BaseConceptMapScorer",
            "CSVLoadError",
            "ConceptMapError",
        ]
    )
except ImportError as e:
    logger.error(f"コアモジュールのインポートに失敗しました: {e}")


# LEAコアもエクスポート（カスタムアルゴリズム用）
try:
    from .lea_core import (
        Link,
        LinkCSVError,
        calculate_f_value,
        calculate_optimal_matching_bruteforce,
        compare_links,
        create_links_from_csv,
    )

    # インポート成功後に__all__に追加
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
except ImportError as e:
    logger.warning(f"LEAコアモジュールのインポートに失敗しました: {e}")


# ============================================================================
# カスタムアルゴリズムの追加
# ============================================================================

# カスタムアルゴリズムを追加する場合は、以下のパターンでインポートを追加してください:
# from .your_algorithm import YourAlgorithm
# __all__.append("YourAlgorithm")
