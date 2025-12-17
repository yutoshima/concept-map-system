#!/usr/bin/env python3

"""
Novak採点アルゴリズム

Novak方式の概念マップ採点を実装します。
完全一致のみを採点し、限定構造（多対一、一対多）に対して追加の加点を行います。

採点基準：
    - 完全一致（ノード、方向、ラベルすべて一致）: 3点
    - 不一致: 0点
    - Conflictリンク: 0点
    - 限定（多対一または一対多）: +4点/個
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
# Novak採点クラス
# ============================================================================


class NovakScorer(SimplePropositionScorer):
    """
    Novak方式の概念マップ採点クラス

    完全一致のみを採点し、限定構造に対して追加の加点を行います。
    """

    # 採点値の定義（定数から取得）
    SCORE_PERFECT_MATCH = constants.ScoringConstants.NOVAK_PERFECT_MATCH
    SCORE_NO_MATCH = constants.ScoringConstants.NOVAK_NO_MATCH
    LIMITATION_BONUS = constants.ScoringConstants.NOVAK_LIMITATION_BONUS  # 限定1つあたりの加点

    # 特殊なリンクタイプ（定数から取得）
    CONFLICT_TYPE = constants.ScoringConstants.CONFLICT_LINK_TYPE

    def __init__(self, cross_link_score: int = 0) -> None:
        """
        初期化

        Args:
            cross_link_score: 交差リンク（conflict）1つあたりの点数（0-4点、デフォルト0）
        """
        super().__init__()
        self.cross_link_point_per_item = max(0, min(4, cross_link_score))  # 0-4点に制限

    def count_conflicts(self, student_map: List[ExpandedProposition]) -> int:
        """
        Conflictリンク（交差リンク）の数をカウント

        Args:
            student_map: 生徒の命題マップ

        Returns:
            Conflictリンクの数
        """
        conflict_count = 0
        for prop in student_map:
            prop_type = self.normalize_type(prop.get("type", ""))
            if prop_type == self.CONFLICT_TYPE:
                conflict_count += 1
        return conflict_count

    def score_proposition(
        self, student_prop: ExpandedProposition, master_map: List[ExpandedProposition]
    ) -> Tuple[int, str]:
        """
        生徒の命題を採点

        Args:
            student_prop: 生徒の命題
            master_map: 模範解答の命題マップ

        Returns:
            (得点, マッチタイプの説明) のタプル
        """
        student_type = self.normalize_type(student_prop.get("type", ""))
        student_antes = student_prop["antes"]
        student_conq = student_prop["conq"]

        # 完全一致（3点）をチェック（conflictも含む）
        for master_prop in master_map:
            master_type = self.normalize_type(master_prop.get("type", ""))

            # タイプが一致し、ノードも一致する場合
            if master_type == student_type and self.nodes_match(
                student_antes, student_conq, master_prop["antes"], master_prop["conq"]
            ):
                master_id = master_prop.get("original_id", master_prop["id"])
                if student_type == self.CONFLICT_TYPE:
                    return (self.SCORE_PERFECT_MATCH, f"完全一致・Conflict (模範ID: {master_id})")
                return (self.SCORE_PERFECT_MATCH, f"完全一致 (模範ID: {master_id})")

        # それ以外は0点
        if student_type == self.CONFLICT_TYPE:
            return (self.SCORE_NO_MATCH, "Conflict（模範に該当なし）")
        return (self.SCORE_NO_MATCH, "模範に該当なし")

    def count_limitations(self, original_data: List[PropositionData]) -> int:
        """
        元データから限定（多対一、一対多）の数をカウント

        Args:
            original_data: CSVから読み込んだ元データ

        Returns:
            限定の数
        """
        limitation_count = 0
        for prop in original_data:
            antes_ids = self.normalize_ids(prop.get("antes", ""))
            conq_ids = self.normalize_ids(prop.get("conq", ""))

            if not antes_ids or not conq_ids:
                continue

            is_antes_multi = len(antes_ids) > 1
            is_conq_multi = len(conq_ids) > 1

            # 多対一（多対多は除く）
            if (is_antes_multi and not is_conq_multi) or (not is_antes_multi and is_conq_multi):
                limitation_count += 1

        return limitation_count

    def get_perfect_match_score(self) -> int:
        """完全一致のスコアを返す"""
        return self.SCORE_PERFECT_MATCH

    def calculate_metrics(
        self, matched_count: int, student_count: int, master_count: int
    ) -> Dict[str, float]:
        """
        評価指標（Precision、Recall、F値）を点数ベースで計算

        交差リンク（conflict）の加点を含めた点数ベースの計算を行います。

        Args:
            matched_count: 完全一致した命題の数（conflictを含む）
            student_count: 生徒の命題数（conflictを含む総数）
            master_count: 模範の命題数（conflictを含む）

        Returns:
            {'precision': float, 'recall': float, 'f_value': float}
        """
        # 限定スコアと交差リンク加点スコアを取得
        limitation_score = getattr(self, '_current_limitation_score', 0)
        cross_link_score = getattr(self, '_current_cross_link_score', 0)

        # 命題の点数を計算（conflictも含む）
        proposition_score = matched_count * self.SCORE_PERFECT_MATCH

        # 獲得点数（命題 + 限定 + 交差リンク加点）
        total_earned_score = proposition_score + limitation_score + cross_link_score

        # 生徒の最大可能点数（全命題 + 限定 + 交差リンク加点）
        student_max_score = (student_count * self.SCORE_PERFECT_MATCH) + limitation_score + cross_link_score

        # 模範の最大可能点数（全命題 + 限定、交差リンク加点は含めない）
        master_max_score = (master_count * self.SCORE_PERFECT_MATCH) + limitation_score

        # Precision: 生徒の回答に対する達成度
        precision = (total_earned_score / student_max_score) if student_max_score > 0 else 0.0

        # Recall: 模範解答に対する達成度（交差リンク加点は含めない）
        recall_score = proposition_score + limitation_score
        recall = (recall_score / master_max_score) if master_max_score > 0 else 0.0

        # F値
        f_value = (
            (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        )

        return {"precision": precision, "recall": recall, "f_value": f_value}

    def calculate_additional_score(
        self,
        student_map: List[ExpandedProposition],
        student_original_data: Optional[List[PropositionData]] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        """
        限定構造のボーナススコアを計算

        Args:
            student_map: 生徒の命題マップ
            student_original_data: 生徒の元データ

        Returns:
            (限定スコア, 追加情報)のタプル
        """
        limitation_count = self.count_limitations(student_original_data or [])
        limitation_score = limitation_count * self.LIMITATION_BONUS

        return limitation_score, {
            "limitation_count": limitation_count,
            "limitation_score": limitation_score,
        }

    def score_all(
        self,
        student_map: Optional[List[ExpandedProposition]] = None,
        master_map: Optional[List[ExpandedProposition]] = None,
        student_original_data: Optional[List[PropositionData]] = None,
    ) -> ScoringResult:
        """
        全命題を採点し、限定点と交差リンク（conflict）点を加点

        Args:
            student_map: 生徒の命題マップ（展開後）
            master_map: 模範の命題マップ（展開後）
            student_original_data: 生徒の元データ（限定カウント用）

        Returns:
            採点結果の辞書
        """
        # パラメータの解決（基底クラスから取得）
        if student_map is None:
            student_map = self.student_map
        if master_map is None:
            master_map = self.master_map
        if student_original_data is None:
            student_original_data = self.student_data

        # 限定スコアを事前に計算してインスタンス変数に保存（calculate_metricsで使用）
        limitation_count = self.count_limitations(student_original_data)
        self._current_limitation_score = limitation_count * self.LIMITATION_BONUS

        # 交差リンク（conflict）をカウントして加点スコアを計算
        conflict_count = self.count_conflicts(student_map)
        cross_link_score = conflict_count * self.cross_link_point_per_item
        self._current_cross_link_score = cross_link_score

        # 基底クラスのscore_allを呼び出し
        result = super().score_all(student_map, master_map, student_original_data)

        # 交差リンクスコアを加算
        result["conflict_count"] = conflict_count
        result["cross_link_point_per_item"] = self.cross_link_point_per_item
        result["cross_link_score"] = cross_link_score
        result["total_score"] = result.get("total_score", 0) + cross_link_score

        # Novak固有のフィールドを追加・調整
        result["method"] = "Novak"
        result["total_proposition_score"] = result.get("proposition_score", 0)
        result["final_total_score"] = result.get("total_score", 0)
        result["matched_count"] = result.get("matched_count", 0)

        return result


# ============================================================================
# アルゴリズムラッパークラス
# ============================================================================


@register_algorithm
class NovakAlgorithm(BaseAlgorithm):
    """Novak方式の概念マップ採点アルゴリズム"""

    def __init__(self) -> None:
        """初期化"""
        super().__init__(
            name="novak",
            description="Novak (ノバック) 概念マップ採点方式。完全一致のみ採点し、限定構造に加点。",
        )

    def execute(self, master_file: str, student_file: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Novak方式で採点を実行

        Args:
            master_file: 模範解答のCSVファイル
            student_file: 生徒の回答のCSVファイル
            **kwargs: 追加のオプション（verbose, debug, cross_link_scoreなど）

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

        # 交差リンクスコアの取得（デフォルト0）
        cross_link_score = kwargs.get("cross_link_score", 0)

        # NovakScorerのインスタンスを作成
        scorer = NovakScorer(cross_link_score=cross_link_score)

        # 共通の実行ロジックとエラーハンドリング
        return self._execute_scoring_with_error_handling(
            scorer, master_file, student_file, "Novak", verbose, debug
        )

    def get_supported_options(self) -> Dict[str, Dict[str, Any]]:
        """
        サポートされているオプションの定義を返す

        Returns:
            オプション定義
        """
        options = self.get_common_options()
        options["cross_link_score"] = {
            "type": int,
            "default": 0,
            "help": "交差リンク（Conflict）1つあたりの点数 (0-4点、デフォルト0)",
        }
        return options

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
        output.extend(create_title_block("【Novak方式 採点結果】"))

        score_counts = results.get("score_counts", {})
        total_props = results.get("total_props", 0)

        output.append(f"総命題数（生徒・展開後）: {total_props}")
        output.append(f"総命題数（模範・展開後）: {results.get('master_props', 0)}")
        output.append("")
        output.append(f"✓ 一致 (3点): {score_counts.get(3, 0)}")
        output.append(f"✗ 不一致/Conflict (0点): {score_counts.get(0, 0)}")
        output.append("")
        output.append(create_separator("-", constants.SEPARATOR_WIDTH_SHORT))
        output.append(f"命題合計点: {results.get('total_proposition_score', 0)}")
        output.append(create_separator("-", constants.SEPARATOR_WIDTH_SHORT))
        output.append("")
        output.append(create_separator("-", constants.SEPARATOR_WIDTH_SHORT))
        output.append(f"限定数: {results.get('limitation_count', 0)}")
        output.append(
            f"限定加点: +{results.get('limitation_score', 0)} "
            f"({results.get('limitation_count', 0)} × 4点)"
        )
        output.append(create_separator("-", constants.SEPARATOR_WIDTH_SHORT))
        output.append("")

        # 交差リンク（conflict）スコアの表示
        conflict_count = results.get('conflict_count', 0)
        cross_link_point_per_item = results.get('cross_link_point_per_item', 0)
        cross_link_score = results.get('cross_link_score', 0)

        if conflict_count > 0 or cross_link_point_per_item > 0:
            output.append(create_separator("-", constants.SEPARATOR_WIDTH_SHORT))
            output.append(f"交差リンク数（Conflict）: {conflict_count}")
            if cross_link_point_per_item > 0:
                output.append(
                    f"交差リンク加点: +{cross_link_score} "
                    f"({conflict_count} × {cross_link_point_per_item}点)"
                )
            else:
                output.append(f"交差リンク加点: +0 （1つあたり0点指定）")
            output.append(create_separator("-", constants.SEPARATOR_WIDTH_SHORT))
            output.append("")

        output.append(create_separator("=", constants.SEPARATOR_WIDTH_SHORT))
        output.append(
            f"総合計点: {results.get('final_total_score', 0)}/{results.get('max_score', 0)} "
            f"({results.get('percentage', 0):.1f}%)"
        )
        output.append(create_separator("=", constants.SEPARATOR_WIDTH_SHORT))
        output.append("")

        # F値・精度指標
        output.extend(format_f_metrics(results, title="【F値・精度指標（命題一致ベース）】"))

        return join_output(output)
