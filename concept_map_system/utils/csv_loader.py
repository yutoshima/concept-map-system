#!/usr/bin/env python3

"""
CSV読み込みユーティリティ

CSVファイルの読み込みと検証を統一的に処理します。
"""

import csv
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..core import constants
from ..core.exceptions import CSVLoadError


class CSVLoader:
    """CSV読み込み共通クラス"""

    @staticmethod
    def load_csv(
        filepath: str,
        required_fields: Optional[List[str]] = None,
        row_validator: Optional[Callable[[Dict[str, Any], int], None]] = None,
        row_filter: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[Dict[str, Any]]:
        """
        CSVファイルを安全に読み込む

        Args:
            filepath: CSVファイルのパス
            required_fields: 必須フィールドのリスト
            row_validator: 各行を検証する関数 (row, row_number) -> None
            row_filter: 行をフィルタする関数 (row) -> bool (Trueで含める)

        Returns:
            読み込まれたデータのリスト

        Raises:
            CSVLoadError: ファイル読み込みエラー

        Examples:
            >>> data = CSVLoader.load_csv(
            ...     "data.csv",
            ...     required_fields=["id", "antes", "conq"],
            ...     row_filter=lambda row: row.get("antes") and row.get("conq")
            ... )
        """
        file_path = Path(filepath)

        # ファイル存在確認
        if not file_path.exists():
            msg = f"ファイルが見つかりません: {filepath}"
            raise CSVLoadError(msg)

        data: List[Dict[str, Any]] = []

        try:
            with file_path.open(encoding=constants.FILE_ENCODING) as f:
                print(f"DEBUG: Reading first line of {filepath}:")
                print(f.readline())
                f.seek(0)  # Reset file pointer after reading the first line
                reader = csv.DictReader(f)

                # ヘッダー確認
                if reader.fieldnames is None:
                    msg = f"CSVファイルが空です: {filepath}"
                    raise CSVLoadError(msg)

                # 必須フィールド確認
                if required_fields:
                    missing_fields = [
                        field for field in required_fields if field not in reader.fieldnames
                    ]
                    if missing_fields:
                        msg = f"必要な列が見つかりません: {missing_fields}\nファイル: {filepath}"
                        raise CSVLoadError(msg)

                # データ読み込み
                for row_num, row in enumerate(reader, start=1):
                    # バリデーション実行
                    if row_validator:
                        try:
                            row_validator(row, row_num)
                        except Exception as e:
                            msg = f"行{row_num}の検証エラー: {e!s}"
                            raise CSVLoadError(msg) from e

                    # フィルタ適用
                    if row_filter and not row_filter(row):
                        continue

                    data.append(row)

                # データが空の場合
                if not data:
                    msg = f"有効なデータが見つかりません: {filepath}"
                    raise CSVLoadError(msg)

                return data

        except UnicodeDecodeError as e:
            msg = (
                f"ファイルのエンコーディングエラー: {filepath}\n"
                "UTF-8またはUTF-8 with BOMで保存されているか確認してください。"
            )
            raise CSVLoadError(msg) from e
        except CSVLoadError:
            # 既にCSVLoadErrorの場合は再送出
            raise
        except Exception as e:
            msg = f"CSVファイル読み込みエラー: {filepath}\n詳細: {e!s}"
            raise CSVLoadError(msg) from e

    @staticmethod
    def create_field_validator(required_nonempty: List[str]) -> Callable:
        """
        必須フィールドが空でないことを確認するバリデータを作成

        Args:
            required_nonempty: 空であってはいけないフィールドのリスト

        Returns:
            バリデータ関数

        Examples:
            >>> validator = CSVLoader.create_field_validator(["id", "antes"])
            >>> validator({"id": "1", "antes": "A"}, 1)  # OK
            >>> validator({"id": "", "antes": "A"}, 2)  # Raises ValueError
        """

        def validator(row: Dict[str, Any], _row_num: int) -> None:
            for field in required_nonempty:
                if not row.get(field, "").strip():
                    msg = f"フィールド '{field}' が空です"
                    raise ValueError(msg)

        return validator
