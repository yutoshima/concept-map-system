#!/usr/bin/env python3

"""
フォーマット用ユーティリティ

結果表示のための共通フォーマット関数を提供します。
"""

from typing import Any, Dict, List


def create_separator(char: str = "=", length: int = 60) -> str:
    """
    セパレーター文字列を作成

    Args:
        char: セパレーター文字（デフォルト: "="）
        length: セパレーターの長さ（デフォルト: 60）

    Returns:
        セパレーター文字列

    Examples:
        >>> create_separator()
        '============================================================'
        >>> create_separator("-", 40)
        '----------------------------------------'
    """
    return char * length


def create_title_block(
    title: str, separator_char: str = "=", separator_length: int = 60
) -> List[str]:
    """
    タイトルブロックを作成

    Args:
        title: タイトル文字列
        separator_char: セパレーター文字（デフォルト: "="）
        separator_length: セパレーターの長さ（デフォルト: 60）

    Returns:
        タイトルブロックの行リスト

    Examples:
        >>> create_title_block("テスト結果")
        ['============================================================',
         'テスト結果',
         '============================================================',
         '']
    """
    separator = create_separator(separator_char, separator_length)
    return [separator, title, separator, ""]


def format_f_metrics(
    results: Dict[str, Any],
    matched_count_key: str = "matched_count",
    precision_key: str = "precision",
    recall_key: str = "recall",
    f_value_key: str = "f_value",
    title: str = "【F値・精度指標】",
) -> List[str]:
    """
    F値と精度指標をフォーマット

    Args:
        results: 結果辞書
        matched_count_key: 一致数のキー
        precision_key: 適合率のキー
        recall_key: 再現率のキー
        f_value_key: F値のキー
        title: セクションタイトル

    Returns:
        フォーマット済みの行リスト

    Examples:
        >>> results = {"matched_count": 10, "precision": 0.85, "recall": 0.90, "f_value": 0.874}
        >>> format_f_metrics(results)
        ['【F値・精度指標】',
         '完全一致数: 10',
         'Precision（適合率）: 0.850',
         'Recall（再現率）: 0.900',
         'F値: 0.874']
    """
    output = [title]
    output.append(f"完全一致数: {results.get(matched_count_key, 0)}")
    output.append(f"Precision（適合率）: {results.get(precision_key, 0):.3f}")
    output.append(f"Recall（再現率）: {results.get(recall_key, 0):.3f}")
    output.append(f"F値: {results.get(f_value_key, 0):.3f}")
    return output


def format_score_display(
    score_counts: Dict[int, int],
    score_labels: Dict[int, str],
    title: str = "【採点内訳】",
) -> List[str]:
    """
    採点内訳を表示

    Args:
        score_counts: スコアごとのカウント辞書
        score_labels: スコアごとのラベル辞書
        title: セクションタイトル

    Returns:
        フォーマット済みの行リスト

    Examples:
        >>> score_counts = {3: 10, 2: 5, 1: 3, 0: 2}
        >>> score_labels = {3: "完全一致", 2: "向き不一致", 1: "ラベル不一致", 0: "不一致"}
        >>> format_score_display(score_counts, score_labels)
        ['【採点内訳】', '完全一致: 10', '向き不一致: 5', 'ラベル不一致: 3', '不一致: 2']
    """
    output = [title]
    # スコアの降順でソート
    for score in sorted(score_labels.keys(), reverse=True):
        label = score_labels[score]
        count = score_counts.get(score, 0)
        output.append(f"{label}: {count}")
    return output


def join_output(lines: List[str]) -> str:
    """
    出力行を結合

    Args:
        lines: 出力行のリスト

    Returns:
        改行で結合された文字列

    Examples:
        >>> join_output(["line1", "line2", "line3"])
        'line1\\nline2\\nline3'
    """
    return "\n".join(lines)
