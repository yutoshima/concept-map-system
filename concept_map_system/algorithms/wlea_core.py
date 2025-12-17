#!/usr/bin/env python3

"""
WLEA (Weighted Link Evaluation Algorithm) コアロジック

因果関係リンクの評価システムの中核機能を提供します。
最適マッチングアルゴリズムにより、模範解答と学習者解答を比較します。

主な機能：
- リンクの比較とスコアリング (0-4点)
- 最適マッチングアルゴリズム (総当たり方式)
- 評価指標の計算 (F値、Recall、Precision)
- CSVファイルの読み込み
"""

from itertools import combinations, permutations
from typing import Dict, List, Set, Tuple

from ..core import constants, get_logger
from ..core.exceptions import LinkCSVError
from ..utils import CSVLoader

# ロガーの取得
logger = get_logger(__name__)

# 型エイリアス
Link = Tuple[Set[str], Set[str], str]  # (antes_set, conq_set, link_type)

# スコア定数（定数から取得）
MAX_LINK_SCORE = constants.ScoringConstants.LINK_EVAL_MAX_SCORE  # リンクの最大スコア（完全一致）


# ============================================================================
# スコアリング関数
# ============================================================================


def compare_links(answer: Link, student: Link) -> int:
    """
    模範解答リンクと学習者リンクを比較し、スコアを返す

    採点基準:
        - 4点: 完全一致（位置とタイプが同じ）
        - 3点: 位置一致だがタイプ違い、または方向が逆
        - 2点: 部分一致でタイプも同じ
        - 1点: 部分一致だがタイプ違い、または方向が逆
        - 0点: 一致なし

    Args:
        answer: 模範解答のリンク (antes_set, conq_set, type)
        student: 学習者解答のリンク (antes_set, conq_set, type)

    Returns:
        スコア (0-4点)

    Examples:
        >>> answer = ({'A', 'B'}, {'C'}, 'causes')
        >>> student = ({'A', 'B'}, {'C'}, 'causes')
        >>> compare_links(answer, student)
        4
    """
    answer_antes, answer_conq, answer_type = answer
    student_antes, student_conq, student_type = student

    # 両端完全一致 - 向きが同じ場合
    if answer_antes == student_antes and answer_conq == student_conq:
        return 4 if answer_type == student_type else 3

    # 両端完全一致 - 向きが逆の場合
    if answer_antes == student_conq and answer_conq == student_antes:
        return 3

    # 両端部分一致 - 向きが同じ場合
    if answer_antes.intersection(student_antes) and answer_conq.intersection(student_conq):
        return 2 if answer_type == student_type else 1

    # 両端部分一致 - 向きが逆の場合
    if answer_antes.intersection(student_conq) and answer_conq.intersection(student_antes):
        return 1

    return 0


# ============================================================================
# マッチングアルゴリズム
# ============================================================================


def calculate_optimal_matching_bruteforce(
    answers: List[Link], students: List[Link], verbose: bool = False
) -> Tuple[int, List[Tuple[int, int]], List[int], List[int]]:
    """
    総当たり（全順列探索）による最適マッチング

    可能な全ての組み合わせと順列を試して、最高スコアを達成する
    マッチングを見つけます。

    計算量:
        - 模範解答n個、学習者解答m個の場合
        - min(n,m) = k として、C(max(n,m), k) * k! 通りを試行

    Args:
        answers: 模範解答のリンクリスト
        students: 学習者解答のリンクリスト
        verbose: デバッグ情報を表示するかどうか

    Returns:
        Tuple containing:
            - best_score: 最高合計スコア
            - best_matching: 最適マッチング [(answer_idx, student_idx), ...]
            - best_answer_indices: 使用された模範解答のインデックス
            - best_student_indices: 使用された学習者解答のインデックス

    Examples:
        >>> answers = [({'A'}, {'B'}, 'causes')]
        >>> students = [({'A'}, {'B'}, 'causes')]
        >>> score, matching, _, _ = calculate_optimal_matching_bruteforce(answers, students)
        >>> score
        4
    """
    n_answers = len(answers)
    n_students = len(students)

    if n_answers == 0 or n_students == 0:
        return 0, [], [], []

    best_score = 0
    best_matching: List[Tuple[int, int]] = []
    best_answer_indices: List[int] = []
    best_student_indices: List[int] = []

    if n_answers <= n_students:
        # Case 1: 模範解答数 ≤ 学習者解答数
        # 学習者解答から n_answers 個を選択
        if verbose:
            logger.debug(f"ケース1: 学習者解答{n_students}個から{n_answers}個を選択")

        answer_range = list(range(n_answers))
        best_score, best_matching, best_answer_indices, best_student_indices = (
            _find_best_matching_case1(answers, students, n_answers, answer_range, best_score)
        )
    else:
        # Case 2: 模範解答数 > 学習者解答数
        # 模範解答から n_students 個を選択
        if verbose:
            logger.debug(f"ケース2: 模範解答{n_answers}個から{n_students}個を選択")

        student_range = list(range(n_students))
        best_score, best_matching, best_answer_indices, best_student_indices = (
            _find_best_matching_case2(answers, students, n_students, student_range, best_score)
        )

    return best_score, best_matching, best_answer_indices, best_student_indices


def _calculate_matching_score(
    answers: List[Link],
    students: List[Link],
    answer_indices: List[int],
    student_indices: List[int],
) -> Tuple[int, List[Tuple[int, int]]]:
    """
    マッチングのスコアを計算

    Args:
        answers: 模範解答リンクのリスト
        students: 学習者解答リンクのリスト
        answer_indices: 使用する模範解答のインデックスリスト
        student_indices: 使用する学習者解答のインデックスリスト

    Returns:
        (合計スコア, マッチングのリスト)のタプル
    """
    total_score = 0
    matching = []

    for ans_idx, stu_idx in zip(answer_indices, student_indices):
        score = compare_links(answers[ans_idx], students[stu_idx])
        total_score += score
        matching.append((ans_idx, stu_idx))

    return total_score, matching


def _find_best_matching_case1(
    answers: List[Link],
    students: List[Link],
    n_answers: int,
    answer_range: List[int],
    initial_best_score: int,
) -> Tuple[int, List[Tuple[int, int]], List[int], List[int]]:
    """
    Case 1: 模範解答数 ≤ 学習者解答数の最適マッチングを探索

    Args:
        answers: 模範解答リンクのリスト
        students: 学習者解答リンクのリスト
        n_answers: 模範解答の数
        answer_range: 模範解答のインデックス範囲
        initial_best_score: 初期の最良スコア

    Returns:
        (最良スコア, 最良マッチング, 模範解答インデックス, 学習者解答インデックス)
    """
    best_score = initial_best_score
    best_matching: List[Tuple[int, int]] = []
    best_answer_indices: List[int] = []
    best_student_indices: List[int] = []
    n_students = len(students)

    for selected_student_indices in combinations(range(n_students), n_answers):
        for student_perm in permutations(selected_student_indices):
            total_score, current_matching = _calculate_matching_score(
                answers, students, answer_range, list(student_perm)
            )

            if total_score > best_score:
                best_score = total_score
                best_matching = current_matching
                best_answer_indices = answer_range
                best_student_indices = list(student_perm)

    return best_score, best_matching, best_answer_indices, best_student_indices


def _find_best_matching_case2(
    answers: List[Link],
    students: List[Link],
    n_students: int,
    student_range: List[int],
    initial_best_score: int,
) -> Tuple[int, List[Tuple[int, int]], List[int], List[int]]:
    """
    Case 2: 模範解答数 > 学習者解答数の最適マッチングを探索

    Args:
        answers: 模範解答リンクのリスト
        students: 学習者解答リンクのリスト
        n_students: 学習者解答の数
        student_range: 学習者解答のインデックス範囲
        initial_best_score: 初期の最良スコア

    Returns:
        (最良スコア, 最良マッチング, 模範解答インデックス, 学習者解答インデックス)
    """
    best_score = initial_best_score
    best_matching: List[Tuple[int, int]] = []
    best_answer_indices: List[int] = []
    best_student_indices: List[int] = []
    n_answers = len(answers)

    for selected_answer_indices in combinations(range(n_answers), n_students):
        for answer_perm in permutations(selected_answer_indices):
            total_score, current_matching = _calculate_matching_score(
                answers, students, list(answer_perm), student_range
            )

            if total_score > best_score:
                best_score = total_score
                best_matching = current_matching
                best_answer_indices = list(answer_perm)
                best_student_indices = student_range

    return best_score, best_matching, best_answer_indices, best_student_indices


# ============================================================================
# 評価指標計算
# ============================================================================


def calculate_f_value(
    raw_score: int, num_answers: int, num_students: int, used_answers: int, used_students: int
) -> Dict[str, float]:
    """
    数の不一致を考慮したF値計算（全体分母版）

    評価指標:
        - 再現率 (Recall): 全模範解答に対する達成度（未評価は0点扱い）
        - 適合率 (Precision): 全学習者解答に対する正確度（未評価は0点扱い）
        - F値: 再現率と適合率の調和平均
        - カバレッジ率: 全体のうち評価できた割合

    Args:
        raw_score: マッチングで得られた合計スコア
        num_answers: 模範解答の総数
        num_students: 学習者解答の総数
        used_answers: マッチングに使用された模範解答の数
        used_students: マッチングに使用された学習者解答の数

    Returns:
        各種評価指標を含む辞書

    Examples:
        >>> metrics = calculate_f_value(12, 3, 3, 3, 3)
        >>> metrics['f_value']
        1.0
    """
    if num_answers == 0 or num_students == 0:
        return {
            "raw_score": raw_score,
            "max_possible_score": 0,
            "score_rate": 0.0,
            "recall": 0.0,
            "precision": 0.0,
            "f_value": 0.0,
            "matched_pairs": 0,
            "unmatched_answers": num_answers,
            "unmatched_students": num_students,
            "coverage_rate": 0.0,
        }

    matched_count = min(used_answers, used_students)
    max_possible_score = num_answers * MAX_LINK_SCORE

    # 再現率:全模範解答に対する達成度（未評価は0点扱い）
    recall = raw_score / (num_answers * MAX_LINK_SCORE)

    # 適合率:全学習者解答に対する正確度（未評価は0点扱い）
    precision = raw_score / (num_students * MAX_LINK_SCORE)

    # F値
    f_value = 0.0
    if (recall + precision) > 0:
        f_value = (2 * recall * precision) / (recall + precision)

    # カバレッジ率:全体のうち評価できた割合
    total_items = max(num_answers, num_students)
    coverage_rate = matched_count / total_items if total_items > 0 else 0.0

    # スコア達成率
    score_rate = raw_score / max_possible_score if max_possible_score > 0 else 0.0

    return {
        "raw_score": raw_score,
        "max_possible_score": max_possible_score,
        "score_rate": score_rate,
        "recall": recall,
        "precision": precision,
        "f_value": f_value,
        "matched_pairs": matched_count,
        "unmatched_answers": max(0, num_answers - used_answers),
        "unmatched_students": max(0, num_students - used_students),
        "coverage_rate": coverage_rate,
    }


# ============================================================================
# CSV読み込み
# ============================================================================


def create_links_from_csv(file_path: str) -> List[Link]:
    """
    CSVファイルを読み込み、Linkのリストを生成

    CSVフォーマット:
        - antes: 原因となるオブジェクト（スペース区切りで複数可）
        - conq: 結果となるオブジェクト
        - type: 関係タイプ

    例:
        antes,conq,type
        1 3,0,Because
        3,2,Because

    Args:
        file_path: CSVファイルのパス

    Returns:
        リンクのリスト

    Raises:
        LinkCSVError: ファイルの読み込みに失敗した場合
    """
    # CSVLoaderを使用して読み込み（エラーはLinkCSVErrorに変換）
    try:
        # 行フィルタ: antes と conq が空でない行のみ
        def row_filter(row: Dict) -> bool:
            if not (row.get("antes") and row.get("conq")):
                logger.warning("空のデータ行をスキップしました")
                return False
            return True

        csv_data = CSVLoader.load_csv(
            file_path, required_fields=["antes", "conq", "type"], row_filter=row_filter
        )

        # CSVデータをLinkに変換
        links: List[Link] = []
        for row in csv_data:
            antes_set = set(str(row["antes"]).split())
            conq_set = {str(row["conq"])}
            link_type = str(row.get("type", ""))
            links.append((antes_set, conq_set, link_type))

        return links

    except Exception as e:
        # CSVLoaderからの例外をLinkCSVErrorに変換
        if isinstance(e, LinkCSVError):
            raise
        msg = f"リンクデータの読み込みに失敗しました: {file_path}\n詳細: {e!s}"
        raise LinkCSVError(msg) from e
