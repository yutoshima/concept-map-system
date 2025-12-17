#!/usr/bin/env python3

"""
統一された例外階層

概念マップ採点システム全体で使用する例外クラスを定義します。
"""


class ConceptMapSystemError(Exception):
    """概念マップシステム全体の基底例外クラス"""


# ============================================================================
# データ読み込み関連のエラー
# ============================================================================


class DataLoadError(ConceptMapSystemError):
    """データ読み込みに関する基底例外クラス"""


class CSVLoadError(DataLoadError):
    """CSVファイルの読み込みエラー"""


class InvalidPropositionError(DataLoadError):
    """無効な命題データ"""


class LinkCSVError(DataLoadError):
    """Linkファイルの読み込みエラー"""


class UnsupportedStructureError(DataLoadError):
    """サポートされていない構造エラー（多対多など）"""


# ============================================================================
# アルゴリズム実行関連のエラー
# ============================================================================


class AlgorithmExecutionError(ConceptMapSystemError):
    """アルゴリズム実行時のエラー"""


class ScoringError(AlgorithmExecutionError):
    """採点処理のエラー"""


# ============================================================================
# 検証関連のエラー
# ============================================================================


class ValidationError(ConceptMapSystemError):
    """データ検証のエラー"""


class FileValidationError(ValidationError):
    """ファイル検証のエラー"""
