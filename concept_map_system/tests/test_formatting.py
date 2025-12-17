#!/usr/bin/env python3

"""
フォーマットユーティリティのテスト
"""

from typing import Any, Dict

from concept_map_system.utils.formatting import (
    create_separator,
    create_title_block,
    format_f_metrics,
    format_score_display,
    join_output,
)


class TestCreateSeparator:
    """create_separator関数のテスト"""

    def test_default_separator(self):
        """デフォルトのセパレーター生成"""
        result = create_separator()
        assert result == "=" * 60
        assert len(result) == 60

    def test_custom_char_separator(self):
        """カスタム文字のセパレーター生成"""
        result = create_separator("-", 40)
        assert result == "-" * 40
        assert len(result) == 40

    def test_different_lengths(self):
        """異なる長さのセパレーター生成"""
        assert len(create_separator("*", 10)) == 10
        assert len(create_separator("#", 80)) == 80

    def test_zero_length_separator(self):
        """長さ0のセパレーター生成"""
        result = create_separator("=", 0)
        assert result == ""
        assert len(result) == 0

    def test_empty_char_separator(self):
        """空文字のセパレーター生成"""
        result = create_separator("", 10)
        assert result == ""
        assert len(result) == 0


class TestCreateTitleBlock:
    """create_title_block関数のテスト"""

    def test_default_title_block(self):
        """デフォルトのタイトルブロック生成"""
        result = create_title_block("テストタイトル")
        assert len(result) == 4
        assert result[0] == "=" * 60
        assert result[1] == "テストタイトル"
        assert result[2] == "=" * 60
        assert result[3] == ""

    def test_custom_separator_title_block(self):
        """カスタムセパレーターのタイトルブロック生成"""
        result = create_title_block("カスタム", "-", 40)
        assert len(result) == 4
        assert result[0] == "-" * 40
        assert result[1] == "カスタム"

    def test_empty_title_block(self):
        """空のタイトルブロック生成"""
        result = create_title_block("")
        assert len(result) == 4
        assert result[0] == "=" * 60
        assert result[1] == ""
        assert result[2] == "=" * 60
        assert result[3] == ""


class TestFormatFMetrics:
    """format_f_metrics関数のテスト"""

    def test_default_f_metrics(self):
        """デフォルトのF値フォーマット"""
        results = {
            "matched_count": 10,
            "precision": 0.85,
            "recall": 0.90,
            "f_value": 0.874,
        }
        output = format_f_metrics(results)
        assert len(output) == 5
        assert "【F値・精度指標】" in output[0]
        assert "完全一致数: 10" in output[1]
        assert "Precision（適合率）: 0.850" in output[2]
        assert "Recall（再現率）: 0.900" in output[3]
        assert "F値: 0.874" in output[4]

    def test_custom_title_f_metrics(self):
        """カスタムタイトルのF値フォーマット"""
        results = {
            "matched_count": 5,
            "precision": 0.75,
            "recall": 0.80,
            "f_value": 0.774,
        }
        output = format_f_metrics(results, title="【カスタム指標】")
        assert "【カスタム指標】" in output[0]

    def test_missing_keys_f_metrics(self):
        """キーが欠けている場合のF値フォーマット"""
        results: Dict[str, Any] = {}
        output = format_f_metrics(results)
        assert len(output) == 5
        assert "完全一致数: 0" in output[1]
        assert "Precision（適合率）: 0.000" in output[2]

    def test_partial_keys_f_metrics(self):
        """一部のキーのみある場合のF値フォーマット"""
        results = {"matched_count": 5, "precision": 0.5}
        output = format_f_metrics(results)
        assert len(output) == 5
        assert "完全一致数: 5" in output[1]
        assert "Precision（適合率）: 0.500" in output[2]
        assert "Recall（再現率）: 0.000" in output[3]
        assert "F値: 0.000" in output[4]

    def test_custom_keys_f_metrics(self):
        """カスタムキーを使用する場合のF値フォーマット"""
        results = {
            "my_count": 8,
            "my_precision": 0.7,
            "my_recall": 0.8,
            "my_f": 0.746,
        }
        output = format_f_metrics(
            results,
            matched_count_key="my_count",
            precision_key="my_precision",
            recall_key="my_recall",
            f_value_key="my_f",
        )
        assert "完全一致数: 8" in output[1]
        assert "Precision（適合率）: 0.700" in output[2]
        assert "Recall（再現率）: 0.800" in output[3]
        assert "F値: 0.746" in output[4]


class TestFormatScoreDisplay:
    """format_score_display関数のテスト"""

    def test_score_display(self):
        """採点内訳の表示"""
        score_counts = {3: 10, 2: 5, 1: 3, 0: 2}
        score_labels = {
            3: "✓ 完全一致 (3点)",
            2: "↔ 向き不一致 (2点)",
            1: "≠ ラベル不一致 (1点)",
            0: "✗ 不一致 (0点)",
        }
        output = format_score_display(score_counts, score_labels)
        assert len(output) == 5
        assert output[0] == "【採点内訳】"
        # スコアは降順でソートされる
        assert "完全一致" in output[1]
        assert "向き不一致" in output[2]
        assert "ラベル不一致" in output[3]
        assert "不一致" in output[4]

    def test_empty_score_display(self):
        """空の採点内訳"""
        output = format_score_display({}, {})
        assert len(output) == 1
        assert output[0] == "【採点内訳】"

    def test_mismatched_keys_score_display(self):
        """キーが一致しない場合の採点内訳"""
        score_counts = {3: 10, 2: 5}
        score_labels = {3: "完全一致", 2: "部分一致", 1: "不一致"}
        output = format_score_display(score_counts, score_labels)
        assert len(output) == 4  # タイトル + 3つのラベル
        assert "完全一致: 10" in output[1]
        assert "部分一致: 5" in output[2]
        assert "不一致: 0" in output[3]  # カウントがない場合は0

    def test_custom_title_score_display(self):
        """カスタムタイトルの採点内訳"""
        score_counts = {2: 3}
        score_labels = {2: "部分一致"}
        output = format_score_display(score_counts, score_labels, title="【カスタム内訳】")
        assert output[0] == "【カスタム内訳】"
        assert "部分一致: 3" in output[1]


class TestJoinOutput:
    """join_output関数のテスト"""

    def test_join_simple_output(self):
        """シンプルな出力結合"""
        lines = ["line1", "line2", "line3"]
        result = join_output(lines)
        assert result == "line1\nline2\nline3"

    def test_join_empty_output(self):
        """空の出力結合"""
        result = join_output([])
        assert result == ""

    def test_join_single_line(self):
        """単一行の出力結合"""
        result = join_output(["single"])
        assert result == "single"
