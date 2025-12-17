#!/usr/bin/env python3

"""
型定義モジュール

プロジェクト全体で使用する型エイリアスとTypedDictを定義します。
"""

from typing import Any, Dict, List, TypedDict

# ============================================================================
# 命題データ型
# ============================================================================


class PropositionData(TypedDict, total=False):
    """
    CSVから読み込んだ命題データの型定義

    Attributes:
        id: 命題ID
        antes: 原因ノード（スペース区切り）
        conq: 結果ノード
        type: リンクタイプ
        original_id: 元のID（展開前）
        is_expanded: 展開済みフラグ
    """

    id: str
    antes: str
    conq: str
    type: str
    original_id: str
    is_expanded: bool


class ExpandedProposition(TypedDict):
    """
    展開後の命題データの型定義

    Attributes:
        id: 命題ID
        original_id: 元のID
        is_expanded: 展開済みフラグ
        antes: 原因ノード
        conq: 結果ノード
        type: リンクタイプ
    """

    id: str
    original_id: str
    is_expanded: bool
    antes: str
    conq: str
    type: str


# ============================================================================
# 採点結果型
# ============================================================================


class ScoringResult(TypedDict, total=False):
    """
    採点結果の型定義

    Attributes:
        method: 採点方式名
        results: 詳細結果リスト
        score_counts: スコアごとのカウント
        total_props: 総命題数
        total_score: 合計スコア
        max_score: 最大スコア
        percentage: 達成率（%）
        matched_count: 完全一致数
        precision: 適合率
        recall: 再現率
        f_value: F値
        master_props: 模範解答の命題数
        student_props: 生徒解答の命題数
        proposition_score: 命題スコア（追加スコア前）
        total_proposition_score: 命題合計点（Novak用）
        final_total_score: 最終合計点（Novak用）
        limitation_count: 限定構造の数（Novak用）
        limitation_score: 限定加点（Novak用）
    """

    method: str
    results: List[Dict[str, Any]]
    score_counts: Dict[int, int]
    total_props: int
    total_score: int
    max_score: int
    percentage: float
    matched_count: int
    precision: float
    recall: float
    f_value: float
    master_props: int
    student_props: int
    proposition_score: int
    total_proposition_score: int
    final_total_score: int
    limitation_count: int
    limitation_score: int


class WLEAResult(TypedDict, total=False):
    """
    WLEA (Weighted Link Evaluation Algorithm) 採点結果の型定義

    Attributes:
        method: 採点方式名
        mode: 実行モード
        raw_score: 素点
        max_possible_score: 最大可能スコア
        score_rate: スコア達成率
        recall: 再現率
        precision: 適合率
        f_value: F値
        matched_pairs: マッチングペア数
        unmatched_answers: 未マッチ模範解答数
        unmatched_students: 未マッチ生徒解答数
        coverage_rate: カバレッジ率
        answer_count: 模範解答数
        student_count: 生徒解答数
    """

    method: str
    mode: str
    raw_score: int
    max_possible_score: int
    score_rate: float
    recall: float
    precision: float
    f_value: float
    matched_pairs: int
    unmatched_answers: int
    unmatched_students: int
    coverage_rate: float
    answer_count: int
    student_count: int


# ============================================================================
# 実行結果型
# ============================================================================


class ExecutionResultData(TypedDict):
    """
    アルゴリズム実行結果の型定義

    Attributes:
        algorithm_name: アルゴリズム名
        success: 成功フラグ
        result: 採点結果（成功時）
        error: エラーメッセージ（失敗時）
        execution_time: 実行時間（秒）
    """

    algorithm_name: str
    success: bool
    result: Dict[str, Any]
    error: str
    execution_time: float
