#!/usr/bin/env python3

"""
命題データの処理ユーティリティ

このモジュールは、命題データの変換や分解などの処理機能を提供します。
"""

from typing import Any, Dict, List

from ..core.logging_config import get_logger

# ロガーの取得
logger = get_logger(__name__)


def decompose_qualifiers(propositions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    限定を分解する

    複数のantesノードを持つ命題を、基準リンクとQualifierリンクに分解します。

    分解ルール:
        - 「0 1 2 If」→「0 2 If」「0 1 Qualifier」「0 2 Qualifier」
          (antes: "0 1", conq: "2", type: "If")
          → antes: "0", conq: "2", type: "If"
          → antes: "0", conq: "1", type: "Qualifier"

        - 「0 1 2 3 Because」→「0 3 Because」「0 1 Qualifier」「0 2 Qualifier」
          (antes: "0 1 2", conq: "3", type: "Because")
          → antes: "0", conq: "3", type: "Because"
          → antes: "0", conq: "1", type: "Qualifier"
          → antes: "0", conq: "2", type: "Qualifier"

    一般化:
        - antesが複数ノード（スペース区切り）の場合:
          1. 最初のノード（基準ノード）とconqを元のtypeで結ぶ
          2. 残りの各antesノードについて、基準ノードとQualifierで結ぶ

    Args:
        propositions: 命題データのリスト

    Returns:
        分解後の命題データのリスト

    Examples:
        >>> props = [
        ...     {"id": "1", "antes": "0 1", "conq": "2", "type": "If"},
        ...     {"id": "2", "antes": "A", "conq": "B", "type": "Because"}
        ... ]
        >>> result = decompose_qualifiers(props)
        >>> len(result)
        4
        >>> result[0]  # メインリンク
        {'id': '1_main', 'antes': '0', 'conq': '2', 'type': 'If', 'original_id': '1', 'is_decomposed': True}
        >>> result[1]  # Qualifier
        {'id': '1_q_1', 'antes': '0', 'conq': '1', 'type': 'Qualifier', 'original_id': '1', 'is_decomposed': True}
    """
    result: List[Dict[str, Any]] = []

    for prop in propositions:
        decomposed = _decompose_single_proposition(prop)
        result.extend(decomposed)

    return result


def _decompose_single_proposition(prop: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    単一の命題を分解する

    Args:
        prop: 命題データ

    Returns:
        分解後の命題リスト
    """
    antes_str = str(prop.get("antes", "")).strip()
    conq_str = str(prop.get("conq", "")).strip()

    # antesまたはconqが空の場合はスキップ
    if not antes_str or not conq_str:
        logger.debug(f"空のantes/conqを持つ命題をスキップ: {prop.get('id')}")
        return []

    # antesノードをスペースで分割
    antes_nodes = antes_str.split()

    # 単一antesノードの場合はそのまま返す
    if len(antes_nodes) <= 1:
        return [prop.copy()]

    # 複数antesノードの場合は分解
    return _create_decomposed_links(prop, antes_nodes, conq_str)


def _create_decomposed_links(
    prop: Dict[str, Any], antes_nodes: List[str], conq_str: str
) -> List[Dict[str, Any]]:
    """
    分解されたリンクを作成する

    Args:
        prop: 元の命題データ
        antes_nodes: antesノードのリスト
        conq_str: conqノード

    Returns:
        分解後の命題リスト
    """
    link_type = str(prop.get("type", ""))
    prop_id = str(prop.get("id", ""))
    base_node = antes_nodes[0]
    qualifier_nodes = antes_nodes[1:]

    result: List[Dict[str, Any]] = []

    # メインリンク: 基準ノード → conq (元のtype)
    main_link = {
        "id": f"{prop_id}_main",
        "antes": base_node,
        "conq": conq_str,
        "type": link_type,
        "original_id": prop_id,
        "is_decomposed": True,
    }
    result.append(main_link)

    # Qualifierリンク: 基準ノード → 各限定ノード (Qualifier)
    for idx, qualifier_node in enumerate(qualifier_nodes, start=1):
        qualifier_link = {
            "id": f"{prop_id}_q_{idx}",
            "antes": base_node,
            "conq": qualifier_node,
            "type": "Qualifier",
            "original_id": prop_id,
            "is_decomposed": True,
        }
        result.append(qualifier_link)

    return result
