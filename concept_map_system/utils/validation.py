#!/usr/bin/env python3

"""
データ検証ユーティリティ

概念マップデータの妥当性をチェックするための検証関数を提供します。
"""

from typing import Any, Dict, List, Optional, cast

from ..core.exceptions import ValidationError
from ..core.types import PropositionData


def _normalize_string(value: Any) -> str:
    """
    値を正規化された文字列に変換

    Args:
        value: 変換する値

    Returns:
        トリムされた文字列
    """
    return str(value).strip()


def _is_empty_string(value: Any) -> bool:
    """
    値が空文字列かチェック

    Args:
        value: チェックする値

    Returns:
        空または空白のみの場合True
    """
    return not _normalize_string(value)


def validate_proposition_fields(
    prop: Dict[str, Any], required_fields: Optional[List[str]] = None
) -> None:
    """
    命題データの必須フィールドを検証

    Args:
        prop: 命題データ
        required_fields: 必須フィールドのリスト（デフォルト: ["id", "antes", "conq"]）

    Raises:
        ValidationError: 必須フィールドが不足している場合
    """
    if required_fields is None:
        required_fields = ["id", "antes", "conq"]

    missing_fields = [field for field in required_fields if field not in prop or not prop[field]]

    if missing_fields:
        msg = f"必須フィールドが不足しています: {missing_fields}, データ: {prop}"
        raise ValidationError(msg)


def validate_proposition_data(prop: PropositionData) -> None:
    """
    命題データの完全性を検証

    Args:
        prop: 命題データ

    Raises:
        ValidationError: データが不正な場合
    """
    # 必須フィールドの存在チェック
    validate_proposition_fields(cast(Dict[str, Any], prop), ["id", "antes", "conq"])

    # IDの形式チェック（空でないこと）
    if _is_empty_string(prop["id"]):
        msg = f"IDが空です: {prop}"
        raise ValidationError(msg)

    # ノードIDの形式チェック（空でないこと）
    if _is_empty_string(prop["antes"]):
        msg = f"antesノードが空です: {prop}"
        raise ValidationError(msg)

    if _is_empty_string(prop["conq"]):
        msg = f"conqノードが空です: {prop}"
        raise ValidationError(msg)


def validate_node_ids(node_ids: str) -> bool:
    """
    ノードIDの文字列が有効かチェック

    Args:
        node_ids: ノードID文字列（スペース区切り）

    Returns:
        有効な場合True、無効な場合False

    Examples:
        >>> validate_node_ids("A B C")
        True
        >>> validate_node_ids("A")
        True
        >>> validate_node_ids("")
        False
        >>> validate_node_ids("   ")
        False
    """
    if _is_empty_string(node_ids):
        return False

    # スペース区切りで分割し、各IDが空でないことを確認
    ids = _normalize_string(node_ids).split()
    return all(id_str for id_str in ids)


def validate_link_type(link_type: str, allowed_types: Optional[List[str]] = None) -> bool:
    """
    リンクタイプが許可されたタイプに含まれるかチェック

    Args:
        link_type: リンクタイプ
        allowed_types: 許可されたタイプのリスト（Noneの場合は任意のタイプを許可）

    Returns:
        有効な場合True、無効な場合False

    Examples:
        >>> validate_link_type("causes")
        True
        >>> validate_link_type("causes", ["causes", "leads_to"])
        True
        >>> validate_link_type("CAUSES", ["causes", "leads_to"])
        True
        >>> validate_link_type("unknown", ["causes", "leads_to"])
        False
        >>> validate_link_type("")
        False
    """
    if allowed_types is None:
        # 任意のタイプを許可（空でなければOK）
        return not _is_empty_string(link_type)

    # 大文字小文字を区別せずに比較
    normalized_type = _normalize_string(link_type).lower()
    normalized_allowed = [_normalize_string(t).lower() for t in allowed_types]

    return normalized_type in normalized_allowed


def validate_propositions_list(
    propositions: List[PropositionData], strict: bool = False
) -> List[str]:
    """
    命題リスト全体を検証し、問題のある命題のリストを返す

    Args:
        propositions: 命題データのリスト
        strict: Trueの場合、最初のエラーで例外を発生させる

    Returns:
        問題のある命題のIDリスト

    Raises:
        ValidationError: strict=Trueで検証エラーが発生した場合
    """
    invalid_prop_ids: List[str] = []

    for prop in propositions:
        try:
            validate_proposition_data(prop)
        except ValidationError:
            prop_id = prop.get("id", "N/A")
            invalid_prop_ids.append(str(prop_id))

            if strict:
                raise

    return invalid_prop_ids
