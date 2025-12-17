#!/usr/bin/env python3

"""
McClure採点アルゴリズム

McClure (1999) 方式の概念マップ採点を実装します。
完全一致、向き不一致、ラベル不一致に対して段階的な部分点を与えます。

採点基準：
    - 完全一致（ノード、方向、ラベルすべて一致）: 3点
    - 向き不一致（ノードとラベルは一致、方向のみ不一致）: 2点
    - ラベル不一致（ノードは一致、ラベルのみ不一致）: 1点
    - 不一致: 0点
"""

from typing import Any, Dict, List, Optional, Tuple

from ..core import BaseAlgorithm, constants, register_algorithm
from ..core.types import ExpandedProposition, PropositionData, ScoringResult
from ..utils.formatting import (
    create_separator,
    create_title_block,
    format_f_metrics,
    join_output,
)
from .concept_map_core import SimplePropositionScorer

# ============================================================================
# McClure採点クラス
# ============================================================================


class McClureScorer(SimplePropositionScorer):
    """
    McClure方式の概念マップ採点クラス

    完全一致だけでなく、向き不一致やラベル不一致に対しても部分点を与えます。
    """

    # 採点値の定義（定数から取得）
    SCORE_PERFECT_MATCH = constants.ScoringConstants.MCCLURE_PERFECT_MATCH  # 完全一致
    SCORE_DIRECTION_MISMATCH = constants.ScoringConstants.MCCLURE_DIRECTION_MISMATCH  # 向き不一致
    SCORE_LABEL_MISMATCH = constants.ScoringConstants.MCCLURE_LABEL_MISMATCH  # ラベル不一致
    SCORE_NO_MATCH = constants.ScoringConstants.MCCLURE_NO_MATCH  # 不一致

    def score_proposition(
        self, student_prop: ExpandedProposition, master_map: List[ExpandedProposition]
    ) -> Tuple[int, str]:
        """
        生徒の命題を採点（サブセットマッチング対応版）

        Args:
            student_prop: 生徒の命題
            master_map: 模範解答の命題マップ

        Returns:
            (得点, マッチタイプの説明) のタプル
        """
        student_type = self.normalize_type(student_prop.get("type", ""))
        student_antes = student_prop["antes"]
        student_conq = student_prop["conq"]

        # 1. 完全一致（3点）をチェック
        for master_prop in master_map:
            master_type = self.normalize_type(master_prop.get("type", ""))

            # タイプとノードがすべて一致
            if master_type == student_type and self.nodes_match(
                student_antes, student_conq, master_prop["antes"], master_prop["conq"]
            ):
                master_id = master_prop.get("original_id", master_prop["id"])
                return (self.SCORE_PERFECT_MATCH, f"完全一致 (模範ID: {master_id})")

        # 2. 向き不一致（2点）をチェック
        for master_prop in master_map:
            master_type = self.normalize_type(master_prop.get("type", ""))

            # タイプは一致、ノードが逆向き
            if master_type == student_type and self.nodes_match(
                student_antes,
                student_conq,
                master_prop["conq"],
                master_prop["antes"],  # 逆向き
            ):
                master_id = master_prop.get("original_id", master_prop["id"])
                return (self.SCORE_DIRECTION_MISMATCH, f"向き不一致 (模範ID: {master_id})")

        # 3. ラベル不一致（1点）をチェック
        for master_prop in master_map:
            # ノードは一致、タイプが不一致
            if self.nodes_match(
                student_antes, student_conq, master_prop["antes"], master_prop["conq"]
            ):
                master_type = master_prop.get("type", "N/A")
                return (self.SCORE_LABEL_MISMATCH, f"ラベル不一致 (模範: {master_type})")

        # 4. それ以外は0点
        return (self.SCORE_NO_MATCH, "模範に該当なし")

    def get_perfect_match_score(self) -> int:
        """完全一致のスコアを返す"""
        return self.SCORE_PERFECT_MATCH

    def score_all(
        self,
        student_map: Optional[List[ExpandedProposition]] = None,
        master_map: Optional[List[ExpandedProposition]] = None,
        student_original_data: Optional[List[PropositionData]] = None,
    ) -> ScoringResult:
        """
        全命題を採点（基底クラスを使用してメソッド名を追加）

        Args:
            student_map: 生徒の命題マップ（展開後）
            master_map: 模範の命題マップ（展開後）
            student_original_data: 生徒の元データ（未使用）

        Returns:
            採点結果の辞書
        """
        # 基底クラスのscore_allを呼び出し
        result = super().score_all(student_map, master_map, student_original_data)

        # McClure固有のフィールドを追加
        result["method"] = "McClure"
        result["matched_count"] = result.get("matched_count", 0)

        return result


# ============================================================================
# アルゴリズムラッパークラス
# ============================================================================


@register_algorithm
class McClureAlgorithm(BaseAlgorithm):
    """McClure方式の概念マップ採点アルゴリズム"""

    def __init__(self) -> None:
        """初期化"""
        super().__init__(
            name="mcclure",
            description=(
                "McClure (1999) 概念マップ採点方式。完全一致、向き不一致、ラベル不一致を判定。"
            ),
        )

    def execute(self, master_file: str, student_file: str, **kwargs: Any) -> Dict[str, Any]:
        """
        McClure方式で採点を実行

        Args:
            master_file: 模範解答のCSVファイル
            student_file: 生徒の回答のCSVファイル
            **kwargs: 追加のオプション（verbose, debugなど）

        Returns:
            採点結果

        Raises:
            Exception: 採点中にエラーが発生した場合
        """
        # ファイルの検証
        self.validate_files(master_file, student_file)

        # オプションの取得
        options = self._extract_execution_options(**kwargs)
        verbose = options["verbose"]
        debug = options["debug"]

        # McClureScorerのインスタンスを作成
        scorer = McClureScorer()

        # 共通の実行ロジックとエラーハンドリング
        return self._execute_scoring_with_error_handling(
            scorer, master_file, student_file, "McClure", verbose, debug
        )

    def get_supported_options(self) -> Dict[str, Dict[str, Any]]:
        """
        サポートされているオプションの定義を返す

        Returns:
            オプション定義
        """
        return self.get_common_options()

    def format_results(self, results: Dict[str, Any]) -> str:
        """
        結果を人間が読みやすい形式にフォーマット

        Args:
            results: 実行結果

        Returns:
            フォーマットされた結果
        """
        output = []

        # タイトルブロック
        output.extend(create_title_block("【McClure方式 採点結果】"))

        score_counts = results.get("score_counts", {})
        total = results.get("total_props", 0)

        output.append(f"総命題数（生徒）: {total}")
        output.append(f"総命題数（模範）: {results.get('master_props', 0)}")
        output.append("")
        output.append(f"✓ 完全一致 (3点): {score_counts.get(3, 0)}")
        output.append(f"↔ 向き不一致 (2点): {score_counts.get(2, 0)}")
        output.append(f"≠ ラベル不一致 (1点): {score_counts.get(1, 0)}")
        output.append(f"✗ 不一致 (0点): {score_counts.get(0, 0)}")
        output.append("")
        output.append(create_separator("-", constants.SEPARATOR_WIDTH_SHORT))
        output.append(
            f"合計得点: {results.get('total_score', 0)}/{results.get('max_score', 0)} "
            f"({results.get('percentage', 0):.1f}%)"
        )
        output.append(create_separator("-", constants.SEPARATOR_WIDTH_SHORT))
        output.append("")

        # F値・精度指標
        output.extend(format_f_metrics(results))

        return join_output(output)
