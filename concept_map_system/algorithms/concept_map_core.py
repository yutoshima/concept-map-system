#!/usr/bin/env python3

"""
概念マップ採点プログラム - コアロジック

このモジュールは、概念マップの採点に必要な基本機能を提供します。
主な機能：
- CSVファイルの読み込み
- 命題の展開（限定構造の分解）
- ノードマッチングのサポート
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple, cast

from ..core import constants
from ..core.logging_config import get_logger
from ..core.types import ExpandedProposition, PropositionData, ScoringResult
from ..utils import CSVLoader

# ロガーの取得
logger = get_logger(__name__)


# ============================================================================
# 基底採点クラス
# ============================================================================


class BaseConceptMapScorer:
    """
    概念マップ採点の基底クラス

    このクラスは、概念マップの採点に必要な共通機能を提供します。
    サブクラスで score_all メソッドを実装することで、
    独自の採点ロジックを実装できます。

    Attributes:
        master_data: 模範解答の元データ（CSV行のリスト）
        student_data: 生徒の回答の元データ（CSV行のリスト）
        master_map: 展開後の模範解答の命題リスト
        student_map: 展開後の生徒の回答の命題リスト
        JUNCTION_TYPE: 仮想ノードのリンクタイプ
    """

    JUNCTION_TYPE = "Junction"

    def __init__(self) -> None:
        """初期化"""
        self.master_data: List[PropositionData] = []
        self.student_data: List[PropositionData] = []
        self.master_map: List[ExpandedProposition] = []
        self.student_map: List[ExpandedProposition] = []

    def load_csv(self, filepath: str) -> List[PropositionData]:
        """
        CSVファイルを読み込む

        Args:
            filepath: CSVファイルのパス

        Returns:
            CSVデータの辞書リスト

        Raises:
            CSVLoadError: ファイルの読み込みに失敗した場合
        """

        # CSVLoaderを使用して読み込み
        def row_filter(row: Dict[str, Any]) -> bool:
            # 必須フィールドがすべて存在する行のみを含める
            has_all_fields = all(field in row for field in ["id", "antes", "conq"])
            if not has_all_fields:
                logger.warning(f"必須フィールドが不足している行をスキップします: {row}")
            return has_all_fields

        return cast(
            List[PropositionData],
            CSVLoader.load_csv(
                filepath, required_fields=["id", "antes", "conq"], row_filter=row_filter
            ),
        )

    def normalize_ids(self, ids_string: str) -> List[str]:
        """
        ID文字列をリストに正規化

        スペース区切りのID文字列をソート済みのリストに変換します。

        Args:
            ids_string: スペース区切りのID文字列（例: "A B C"）

        Returns:
            ソート済みのIDリスト（例: ["A", "B", "C"]）

        Examples:
            >>> scorer = BaseConceptMapScorer()
            >>> scorer.normalize_ids("C A B")
            ['A', 'B', 'C']
        """
        if not ids_string:
            return []
        return sorted(node_id for node_id in str(ids_string).split() if node_id)

    def _is_many_to_many(
        self, prop: PropositionData, antes_ids: List[str], conq_ids: List[str]
    ) -> bool:
        """
        多対多構造かチェック

        Args:
            prop: 命題データ
            antes_ids: 前提ノードIDリスト
            conq_ids: 結論ノードIDリスト

        Returns:
            多対多の場合True
        """
        is_antes_multi = len(antes_ids) > 1
        is_conq_multi = len(conq_ids) > 1

        if is_antes_multi and is_conq_multi:
            logger.warning(
                "多対多のデータはサポートされていません。無視します。"
                f"(ID: {prop.get('id', 'N/A')}, antes: '{prop.get('antes')}', "
                f"conq: '{prop.get('conq')}')"
            )
            return True
        return False

    def _expand_many_to_one(
        self, prop: PropositionData, antes_ids: List[str], conq_ids: List[str]
    ) -> Tuple[List[ExpandedProposition], str]:
        """
        多対一構造を展開（下位変換ノード使用）

        A, B, C → D を以下のように展開:
        - A→t_to_D, B→t_to_D, C→t_to_D, t_from_A_B_C→D

        Args:
            prop: 命題データ
            antes_ids: 前提ノードIDリスト
            conq_ids: 結論ノードIDリスト

        Returns:
            (展開された命題リスト, メインリンクの前提ノードID)
        """
        expanded_props: List[ExpandedProposition] = []

        # Junction用の限定ノード (〜への限定)
        conq_str = "_".join(conq_ids)
        junction_node = f"{constants.JUNCTION_PREFIX_TO}{conq_str}"

        # メインリンク用の限定ノード (〜からの限定)
        antes_str = "_".join(antes_ids)
        main_node = f"{constants.JUNCTION_PREFIX_FROM}{antes_str}"

        for ante_id in antes_ids:
            expanded_props.append(
                {
                    "id": f"{prop['id']}_{ante_id}_A",
                    "original_id": prop["id"],
                    "is_expanded": True,
                    "antes": ante_id,
                    "conq": junction_node,
                    "type": self.JUNCTION_TYPE,
                }
            )

        return expanded_props, main_node

    def _expand_one_to_many(
        self, prop: PropositionData, antes_ids: List[str], conq_ids: List[str]
    ) -> Tuple[List[ExpandedProposition], str]:
        """
        一対多構造を展開（上位変換ノード使用）

        A → B, C, D を以下のように展開:
        - t_from_A→B, t_from_A→C, t_from_A→D, A→t_to_B_C_D

        Args:
            prop: 命題データ
            antes_ids: 前提ノードIDリスト
            conq_ids: 結論ノードIDリスト

        Returns:
            (展開された命題リスト, メインリンクの結論ノードID)
        """
        expanded_props: List[ExpandedProposition] = []

        # メインリンク後半用の限定ノード (〜への限定)
        conq_str = "_".join(conq_ids)
        main_node = f"{constants.JUNCTION_PREFIX_TO}{conq_str}"

        # Junction用の限定ノード (〜からの限定)
        antes_str = "_".join(antes_ids)
        junction_node = f"{constants.JUNCTION_PREFIX_FROM}{antes_str}"

        for conq_id in conq_ids:
            expanded_props.append(
                {
                    "id": f"{prop['id']}_{conq_id}_C",
                    "original_id": prop["id"],
                    "is_expanded": True,
                    "antes": junction_node,
                    "conq": conq_id,
                    "type": self.JUNCTION_TYPE,
                }
            )

        return expanded_props, main_node

    def _create_main_link(
        self,
        prop: PropositionData,
        antes_node: str,
        conq_node: str,
        is_expanded: bool,
    ) -> ExpandedProposition:
        """
        メインリンクを作成

        Args:
            prop: 元の命題データ
            antes_node: 前提ノードID
            conq_node: 結論ノードID
            is_expanded: 展開されたかどうか

        Returns:
            メインリンクの辞書
        """
        return {
            "id": f"{prop['id']}_Main" if is_expanded else prop["id"],
            "original_id": prop["id"],
            "is_expanded": is_expanded,
            "antes": antes_node,
            "conq": conq_node,
            "type": prop.get("type", ""),
        }

    def expand_proposition(self, prop: PropositionData) -> List[ExpandedProposition]:
        """
        命題を展開

        限定構造（多対一、一対多）を複数の単純な命題に展開します。
        多対多構造はサポートされておらず、警告を表示して空リストを返します。

        展開ルール:
        - 一対一: そのまま
        - 多対一: 各antesノードから仮想ノードへのリンク + 仮想ノードからconqへのリンク
        - 一対多: antesから仮想ノードへのリンク + 仮想ノードから各conqノードへのリンク
        - 多対多: サポート外（警告表示）

        Args:
            prop: 元の命題データ（辞書）

        Returns:
            展開後の命題リスト

        Raises:
            InvalidPropositionError: 命題データが不正な場合
        """
        antes_ids = self.normalize_ids(prop.get("antes", ""))
        conq_ids = self.normalize_ids(prop.get("conq", ""))

        if not antes_ids or not conq_ids:
            return []

        # 多対多チェック
        if self._is_many_to_many(prop, antes_ids, conq_ids):
            return []

        expanded_props: List[ExpandedProposition] = []
        is_antes_multi = len(antes_ids) > 1
        is_conq_multi = len(conq_ids) > 1

        final_antes_node = antes_ids[0]
        final_conq_node = conq_ids[0]

        # 多対一の展開
        if is_antes_multi:
            junction_props, final_antes_node = self._expand_many_to_one(prop, antes_ids, conq_ids)
            expanded_props.extend(junction_props)

        # 一対多の展開
        elif is_conq_multi:
            junction_props, final_conq_node = self._expand_one_to_many(prop, antes_ids, conq_ids)
            expanded_props.extend(junction_props)

        # メインリンクを追加
        is_expanded = is_antes_multi or is_conq_multi
        main_link = self._create_main_link(prop, final_antes_node, final_conq_node, is_expanded)
        expanded_props.append(main_link)

        return expanded_props

    def process_map_data(self, csv_data: List[PropositionData]) -> List[ExpandedProposition]:
        """
        CSVデータから命題マップを生成

        各行を展開し、重複を除去して命題マップを作成します。

        Args:
            csv_data: CSVから読み込んだデータ

        Returns:
            展開後の命題リスト（重複除去済み）
        """
        all_props: List[ExpandedProposition] = []

        for row in csv_data:
            if row.get("antes") and row.get("conq"):
                expanded = self.expand_proposition(row)
                all_props.extend(expanded)

        # 重複を除去（antes, conq, typeの組み合わせで判定）
        unique_props: Dict[str, ExpandedProposition] = {}
        for prop in all_props:
            key = f"{prop['antes']}_{prop['conq']}_{prop.get('type', '')}"
            if key not in unique_props:
                unique_props[key] = prop

        return list(unique_props.values())

    def normalize_type(self, type_str: str) -> str:
        """
        ラベルを正規化

        ラベル文字列を小文字に変換し、前後の空白を除去します。

        Args:
            type_str: ラベル文字列

        Returns:
            正規化されたラベル

        Examples:
            >>> scorer = BaseConceptMapScorer()
            >>> scorer.normalize_type("  CAUSES  ")
            'causes'
        """
        return str(type_str or "").lower().strip()

    def _extract_nodes_from_junction_id(
        self, node_id: str
    ) -> Tuple[Optional[Set[str]], Optional[Set[str]]]:
        """
        変換ノード(Tノード)IDから元のノードIDセットを抽出

        新しい命名規則（t_to_... / t_from_...）に対応。

        Args:
            node_id: 変換ノードID（例: "t_from_1_2" (下位変換ノード) or "t_to_3" (上位変換ノード)）

        Returns:
            (antesノードセット, conqノードセット) のタプル
            パース失敗時は (None, None)

        Examples:
            >>> scorer = BaseConceptMapScorer()
            >>> scorer._extract_nodes_from_junction_id("t_from_1_2")
            ({'1', '2'}, set())
            >>> scorer._extract_nodes_from_junction_id("t_to_3")
            (set(), {'3'})
        """
        # 新しい命名規則: t_from_... (下位変換ノード) または t_to_... (上位変換ノード)
        if node_id.startswith(constants.JUNCTION_PREFIX_FROM):
            # t_from_1_2 → antes = {1, 2}, conq = {} (複数の前提を集約する変換点)
            nodes_part = node_id[len(constants.JUNCTION_PREFIX_FROM) :]
            antes_nodes = set(filter(None, nodes_part.split("_")))
            return antes_nodes, set()

        if node_id.startswith(constants.JUNCTION_PREFIX_TO):
            # t_to_3 → antes = {}, conq = {3} (限定から結論への接続を表す変換点)
            nodes_part = node_id[len(constants.JUNCTION_PREFIX_TO) :]
            conq_nodes = set(filter(None, nodes_part.split("_")))
            return set(), conq_nodes

        # 限定ノードではない通常のノード
        return None, None

    def is_subset_match(self, student_node_id: str, master_node_id: str) -> bool:
        """
        生徒の変換ノード(Tノード)が模範の変換ノードの部分集合であるかを判定

        生徒が模範解答の一部だけを記述した場合でもマッチとみなすための
        サブセットマッチング機能。

        新しい命名規則（t_from_... / t_to_...）に対応し、
        3つ以上のノードも自然に扱えます。

        Args:
            student_node_id: 生徒の変換ノードID
            master_node_id: 模範の変換ノードID

        Returns:
            部分集合の場合True、それ以外False

        Examples:
            >>> scorer = BaseConceptMapScorer()
            >>> scorer.is_subset_match("t_from_1", "t_from_1_2")
            True
            >>> scorer.is_subset_match("t_from_1_2", "t_from_1_2_3")
            True
        """
        student_antes, student_conq = self._extract_nodes_from_junction_id(student_node_id)
        master_antes, master_conq = self._extract_nodes_from_junction_id(master_node_id)

        if student_antes is None or master_antes is None:
            return False

        # 両方が空集合の場合はマッチしない
        if not student_antes and not student_conq:
            return False
        if not master_antes and not master_conq:
            return False

        # 同じタイプの限定ノード（from同士、to同士）のみ比較
        if student_antes and master_antes:
            return student_antes.issubset(master_antes)
        if student_conq and master_conq:
            return student_conq.issubset(master_conq)

        return False

    def load_data(self, master_file: str, student_file: str) -> None:
        """
        模範解答と生徒の回答を読み込む

        CSVファイルを読み込み、展開処理を行って内部状態に格納します。

        Args:
            master_file: 模範解答のCSVファイルパス
            student_file: 生徒の回答のCSVファイルパス

        Raises:
            CSVLoadError: ファイルの読み込みに失敗した場合
        """
        self.master_data = self.load_csv(master_file)
        self.student_data = self.load_csv(student_file)
        self.master_map = self.process_map_data(self.master_data)
        self.student_map = self.process_map_data(self.student_data)

    def nodes_match(
        self, student_antes: str, student_conq: str, master_antes: str, master_conq: str
    ) -> bool:
        """
        ノードペアが一致するか判定（サブセットマッチング対応）

        Args:
            student_antes: 生徒の前提ノードID
            student_conq: 生徒の結論ノードID
            master_antes: 模範の前提ノードID
            master_conq: 模範の結論ノードID

        Returns:
            一致する場合True

        Examples:
            >>> scorer = BaseConceptMapScorer()
            >>> scorer.nodes_match("A", "B", "A", "B")
            True
        """
        antes_match = (student_antes == master_antes) or self.is_subset_match(
            student_antes, master_antes
        )
        conq_match = (student_conq == master_conq) or self.is_subset_match(
            student_conq, master_conq
        )
        return antes_match and conq_match

    def calculate_metrics(
        self, matched_count: int, student_count: int, master_count: int
    ) -> Dict[str, float]:
        """
        評価指標（Precision、Recall、F値）を計算

        Args:
            matched_count: 完全一致した命題の数
            student_count: 生徒の命題数
            master_count: 模範の命題数

        Returns:
            {'precision': float, 'recall': float, 'f_value': float}

        Examples:
            >>> scorer = BaseConceptMapScorer()
            >>> scorer.calculate_metrics(3, 7, 9)
            {'precision': 0.42857..., 'recall': 0.33333..., 'f_value': 0.375}
        """
        precision = (matched_count / student_count) if student_count > 0 else 0.0
        recall = (matched_count / master_count) if master_count > 0 else 0.0
        f_value = (
            (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        )

        return {"precision": precision, "recall": recall, "f_value": f_value}

    def score_all(
        self,
        student_map: Optional[List[ExpandedProposition]] = None,
        master_map: Optional[List[ExpandedProposition]] = None,
    ) -> ScoringResult:
        """
        全命題を採点（サブクラスで実装）

        Args:
            student_map: 生徒の命題マップ（Noneの場合は self.student_map を使用）
            master_map: 模範の命題マップ（Noneの場合は self.master_map を使用）

        Returns:
            採点結果の辞書

        Raises:
            NotImplementedError: サブクラスで実装されていない場合
        """
        msg = "サブクラスで score_all メソッドを実装してください"
        raise NotImplementedError(msg)


# ============================================================================
# 命題単位採点用の基底クラス
# ============================================================================


class SimplePropositionScorer(BaseConceptMapScorer):
    """
    命題を1つずつ採点するアルゴリズムの基底クラス

    McClure方式やNovak方式のように、各命題に対してスコアを付与する
    アルゴリズムの共通ロジックを提供します。

    サブクラスで実装すべきメソッド:
    - score_proposition(): 1つの命題を採点
    - get_perfect_match_score(): 完全一致のスコアを返す
    - calculate_additional_score(): 追加スコア計算（オプション）
    """

    def score_proposition(
        self, student_prop: ExpandedProposition, master_map: List[ExpandedProposition]
    ) -> Tuple[int, str]:
        """
        生徒の命題を採点（サブクラスで実装）

        Args:
            student_prop: 生徒の命題
            master_map: 模範解答の命題マップ

        Returns:
            (スコア, マッチタイプ)のタプル

        Raises:
            NotImplementedError: サブクラスで実装されていない場合
        """
        msg = "サブクラスで score_proposition を実装してください"
        raise NotImplementedError(msg)

    def get_perfect_match_score(self) -> int:
        """
        完全一致のスコアを返す（サブクラスで実装）

        Returns:
            完全一致時のスコア

        Raises:
            NotImplementedError: サブクラスで実装されていない場合
        """
        msg = "サブクラスで get_perfect_match_score を実装してください"
        raise NotImplementedError(msg)

    def calculate_additional_score(
        self,
        student_map: List[ExpandedProposition],
        student_original_data: Optional[List[PropositionData]] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        """
        追加スコアを計算（サブクラスでオーバーライド可能）

        Novak方式の限定ボーナスなど、命題採点以外の追加スコアを
        計算する場合にオーバーライドします。

        Args:
            student_map: 生徒の命題マップ
            student_original_data: 生徒の元データ（オプション）

        Returns:
            (追加スコア, 追加情報の辞書)のタプル
        """
        return 0, {}

    def _resolve_parameters(
        self,
        student_map: Optional[List[ExpandedProposition]],
        master_map: Optional[List[ExpandedProposition]],
        student_original_data: Optional[List[PropositionData]],
    ) -> tuple[List[ExpandedProposition], List[ExpandedProposition], List[PropositionData]]:
        """
        採点パラメータのデフォルト値を解決

        Args:
            student_map: 生徒の命題マップ（Noneの場合self.student_mapを使用）
            master_map: 模範の命題マップ（Noneの場合self.master_mapを使用）
            student_original_data: 生徒の元データ（Noneの場合self.student_dataを使用）

        Returns:
            解決済みのパラメータタプル
        """
        resolved_student_map = student_map or self.student_map
        resolved_master_map = master_map or self.master_map
        resolved_student_data = student_original_data or self.student_data
        return resolved_student_map, resolved_master_map, resolved_student_data

    def _score_propositions(
        self, student_map: List[ExpandedProposition], master_map: List[ExpandedProposition]
    ) -> Dict[str, Any]:
        """
        全命題を採点し統計を収集

        Args:
            student_map: 生徒の命題マップ
            master_map: 模範の命題マップ

        Returns:
            採点統計の辞書
        """
        results: List[Dict[str, Any]] = []
        score_counts: Dict[int, int] = defaultdict(int)
        proposition_score = 0
        matched_count = 0
        perfect_match_score = self.get_perfect_match_score()

        for student_prop in student_map:
            score, match_type = self.score_proposition(student_prop, master_map)
            score_counts[score] += 1
            proposition_score += score

            if score == perfect_match_score:
                matched_count += 1

            results.append({"student_prop": student_prop, "score": score, "match_type": match_type})

        return {
            "results": results,
            "score_counts": dict(score_counts),
            "proposition_score": proposition_score,
            "matched_count": matched_count,
            "perfect_match_score": perfect_match_score,
        }

    def _calculate_final_scores(
        self,
        proposition_score: int,
        additional_score: int,
        student_count: int,
        perfect_match_score: int,
    ) -> Dict[str, Any]:
        """
        最終スコアとパーセンテージを計算

        Args:
            proposition_score: 命題スコアの合計
            additional_score: 追加スコア
            student_count: 生徒の命題数
            perfect_match_score: 完全一致時のスコア

        Returns:
            スコア情報の辞書
        """
        total_score = proposition_score + additional_score
        max_score = (student_count * perfect_match_score) + additional_score
        percentage = (total_score / max_score * 100) if max_score > 0 else 0.0

        return {
            "total_score": total_score,
            "max_score": max_score,
            "percentage": percentage,
        }

    def _build_scoring_result(
        self,
        scoring_stats: Dict[str, Any],
        final_scores: Dict[str, Any],
        metrics: Dict[str, Any],
        additional_info: Dict[str, Any],
        student_count: int,
        master_count: int,
    ) -> ScoringResult:
        """
        採点結果の辞書を構築

        Args:
            scoring_stats: 採点統計
            final_scores: 最終スコア情報
            metrics: 評価指標
            additional_info: 追加情報
            student_count: 生徒の命題数
            master_count: 模範の命題数

        Returns:
            採点結果
        """
        result = {
            "results": scoring_stats["results"],
            "score_counts": scoring_stats["score_counts"],
            "total_props": student_count,
            "proposition_score": scoring_stats["proposition_score"],
            "master_props": master_count,
            "student_props": student_count,
            **final_scores,
            **metrics,
            **additional_info,
        }
        return cast(ScoringResult, result)

    def score_all(
        self,
        student_map: Optional[List[ExpandedProposition]] = None,
        master_map: Optional[List[ExpandedProposition]] = None,
        student_original_data: Optional[List[PropositionData]] = None,
    ) -> ScoringResult:
        """
        全命題を採点（共通実装）

        Args:
            student_map: 生徒の命題マップ
            master_map: 模範の命題マップ
            student_original_data: 生徒の元データ（追加スコア計算用）

        Returns:
            採点結果の辞書
        """
        # パラメータの解決
        student_map, master_map, student_original_data = self._resolve_parameters(
            student_map, master_map, student_original_data
        )

        # 命題の採点
        scoring_stats = self._score_propositions(student_map, master_map)

        # 追加スコアの計算
        additional_score, additional_info = self.calculate_additional_score(
            student_map, student_original_data
        )

        # 最終スコアの計算
        final_scores = self._calculate_final_scores(
            scoring_stats["proposition_score"],
            additional_score,
            len(student_map),
            scoring_stats["perfect_match_score"],
        )

        # 評価指標の計算
        metrics = self.calculate_metrics(
            scoring_stats["matched_count"], len(student_map), len(master_map)
        )

        # 結果の構築
        return self._build_scoring_result(
            scoring_stats, final_scores, metrics, additional_info, len(student_map), len(master_map)
        )
