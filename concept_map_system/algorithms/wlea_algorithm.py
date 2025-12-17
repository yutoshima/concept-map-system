#!/usr:bin/env python3

"""
WLEA (Weighted Link Evaluation Algorithm) 採点アルゴリズム

因果関係リンク評価システム。
最適マッチングアルゴリズムにより、F値、再現率、適合率を計算します。

採点基準：
    - 4点: 完全一致（位置とタイプが同じ）
    - 3点: 位置一致だがタイプ違い、または方向が逆
    - 2点: 部分一致でタイプも同じ
    - 1点: 部分一致だがタイプ違い、または方向が逆
    - 0点: 一致なし
"""

from typing import Any, Dict

from ..core import BaseAlgorithm, constants, register_algorithm
from ..core.constants import ResultKeys
from ..core.exceptions import AlgorithmExecutionError
from ..utils.formatting import create_separator, create_title_block, join_output
from .wlea_core import (
    MAX_LINK_SCORE,
    LinkCSVError,
    calculate_f_value,
    calculate_optimal_matching_bruteforce,
    create_links_from_csv,
)

# ============================================================================
# アルゴリズムラッパークラス
# ============================================================================


@register_algorithm
class WLEAAlgorithm(BaseAlgorithm):
    """WLEA (Weighted Link Evaluation Algorithm) 因果関係リンク評価アルゴリズム"""

    def __init__(self) -> None:
        """初期化"""
        super().__init__(
            name="wlea",
            description=(
                "WLEA法: 因果関係リンク評価システム。最適マッチングによりF値、再現率、適合率を計算。"
            ),
        )

    def _load_links(self, master_file: str, student_file: str, debug: bool) -> tuple[list, list]:
        """
        CSVファイルからリンクデータを読み込む

        Args:
            master_file: 模範解答ファイル
            student_file: 生徒の回答ファイル
            debug: デバッグモード

        Returns:
            (模範解答リンク, 生徒リンク)のタプル

        Raises:
            LinkCSVError: 読み込みに失敗した場合
        """
        self.logger.info(f"データを読み込み中: master={master_file}, student={student_file}")

        answers = create_links_from_csv(master_file)
        if not answers:
            msg = "模範解答が読み込めませんでした"
            raise LinkCSVError(msg)

        student_links = create_links_from_csv(student_file)
        if not student_links:
            msg = "生徒の回答が読み込めませんでした"
            raise LinkCSVError(msg)

        if debug:
            self.logger.debug(f"模範解答数: {len(answers)}個")
            self.logger.debug(f"生徒の回答数: {len(student_links)}個")

        return answers, student_links

    def _build_matching_details(self, answers: list, student_links: list, matching: list) -> list:
        """
        マッチング詳細情報を構築

        Args:
            answers: 模範解答リンク
            student_links: 生徒リンク
            matching: マッチングリスト

        Returns:
            詳細情報のリスト
        """
        return [
            {
                "answer_index": a_idx,
                "student_index": s_idx,
                "answer": str(answers[a_idx]),
                "student": str(student_links[s_idx]),
            }
            for a_idx, s_idx in matching
        ]

    def _build_simple_result(
        self,
        score: int,
        answers: list,
        student_links: list,
        matching: list,
        verbose: bool,
    ) -> Dict[str, Any]:
        """
        素点のみモードの結果を構築

        Args:
            score: スコア
            answers: 模範解答リンク
            student_links: 生徒リンク
            matching: マッチングリスト
            verbose: 詳細モード

        Returns:
            結果辞書
        """
        max_possible_score = min(len(answers), len(student_links)) * MAX_LINK_SCORE
        score_rate = score / max_possible_score if max_possible_score > 0 else 0.0

        results: Dict[str, Any] = {
            ResultKeys.METHOD: "WLEA",
            "mode": "simple_score_only",
            ResultKeys.RAW_SCORE: score,
            ResultKeys.MAX_POSSIBLE_SCORE: max_possible_score,
            ResultKeys.SCORE_RATE: score_rate,
            ResultKeys.PERCENTAGE: score_rate * 100,
            "answer_count": len(answers),
            "student_count": len(student_links),
            "matched_pairs": len(matching),
        }

        if verbose:
            results["matching_details"] = self._build_matching_details(
                answers, student_links, matching
            )

        return results

    def _build_full_result(
        self,
        score: int,
        answers: list,
        student_links: list,
        matching: list,
        used_answers: list,
        used_students: list,
        verbose: bool,
    ) -> Dict[str, Any]:
        """
        通常モードの完全な結果を構築

        Args:
            score: スコア
            answers: 模範解答リンク
            student_links: 生徒リンク
            matching: マッチングリスト
            used_answers: 使用された模範解答インデックス
            used_students: 使用された生徒インデックス
            verbose: 詳細モード

        Returns:
            結果辞書
        """
        metrics = calculate_f_value(
            score, len(answers), len(student_links), len(used_answers), len(used_students)
        )

        results: Dict[str, Any] = {
            ResultKeys.METHOD: "WLEA",
            "mode": "full_metrics",
            ResultKeys.RAW_SCORE: metrics["raw_score"],
            ResultKeys.MAX_POSSIBLE_SCORE: metrics["max_possible_score"],
            ResultKeys.SCORE_RATE: metrics["score_rate"],
            ResultKeys.RECALL: metrics["recall"],
            ResultKeys.PRECISION: metrics["precision"],
            ResultKeys.F_VALUE: metrics["f_value"],
            "matched_pairs": len(matching),
            "unmatched_answers": metrics["unmatched_answers"],
            "unmatched_students": metrics["unmatched_students"],
            "coverage_rate": metrics["coverage_rate"],
            "answer_count": len(answers),
            "student_count": len(student_links),
        }

        if verbose:
            results["matching_details"] = self._build_matching_details(
                answers, student_links, matching
            )

        return results

    def execute(self, master_file: str, student_file: str, **kwargs: Any) -> Dict[str, Any]:
        """
        WLEA方式で採点を実行

        Args:
            master_file: 模範解答のCSVファイル
            student_file: 生徒の回答のCSVファイル
            **kwargs: 追加のオプション（verbose, debug, simple_score_onlyなど）

        Returns:
            採点結果

        Raises:
            AlgorithmExecutionError: 採点中にエラーが発生した場合
        """
        self.validate_files(master_file, student_file)

        options = self._extract_execution_options(**kwargs)
        verbose = options["verbose"]
        debug = options["debug"]
        simple_score_only = kwargs.get("simple_score_only", False)

        try:
            # データ読み込み
            answers, student_links = self._load_links(master_file, student_file, debug)

            # マッチング計算
            score, matching, used_answers, used_students = calculate_optimal_matching_bruteforce(
                answers, student_links, verbose=debug
            )

            # 結果構築
            if simple_score_only:
                return self._build_simple_result(score, answers, student_links, matching, verbose)
            return self._build_full_result(
                score, answers, student_links, matching, used_answers, used_students, verbose
            )

        except LinkCSVError as e:
            msg = f"WLEA採点中のデータエラー: {e!s}"
            raise AlgorithmExecutionError(msg) from e
        except Exception as e:
            self.logger.exception("WLEA採点中に予期しないエラーが発生しました")
            msg = f"WLEA採点中に予期しないエラーが発生しました: {e!s}"
            raise AlgorithmExecutionError(msg) from e

    def get_supported_options(self) -> Dict[str, Dict[str, Any]]:
        """
        サポートされているオプションの定義を返す

        Returns:
            オプション定義
        """
        # 共通オプションを取得して拡張
        options = self.get_common_options()
        # verbose オプションの説明を上書き（より詳細な説明）
        options["verbose"]["help"] = "詳細な採点結果を表示（マッチング詳細を含む）"
        # 追加のオプション
        options["simple_score_only"] = {
            "type": bool,
            "default": False,
            "help": "素点のみを計算（F値などの指標を計算しない）",
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
        output.extend(create_title_block("【WLEA法 評価結果】"))

        mode = results.get("mode", "full_metrics")

        output.append(f"模範解答数: {results.get('answer_count', 0)}個")
        output.append(f"生徒の回答数: {results.get('student_count', 0)}個")
        output.append("")

        output.append(create_separator("-", constants.SEPARATOR_WIDTH_SHORT))
        output.append(
            f"スコア: {results.get('raw_score', 0)}/{results.get('max_possible_score', 0)} "
            f"({results.get('score_rate', 0) * 100:.1f}%)"
        )
        output.append(create_separator("-", constants.SEPARATOR_WIDTH_SHORT))
        output.append("")

        # 素点のみモードの場合は、F値などの詳細指標を表示しない
        if mode == "simple_score_only":
            output.append(f"マッチングペア数: {results.get('matched_pairs', 0)}")
        else:
            # 通常モード：詳細な評価指標を表示
            output.append("【評価指標】")
            output.append(f"F値: {results.get('f_value', 0):.3f}")
            output.append(f"再現率: {results.get('recall', 0):.3f}")
            output.append(f"適合率: {results.get('precision', 0):.3f}")
            output.append("")

            output.append(f"マッチングペア数: {results.get('matched_pairs', 0)}")
            output.append(f"未マッチ模範解答: {results.get('unmatched_answers', 0)}")
            output.append(f"未マッチ生徒解答: {results.get('unmatched_students', 0)}")
            output.append(f"カバレッジ率: {results.get('coverage_rate', 0):.3f}")

        return join_output(output)
