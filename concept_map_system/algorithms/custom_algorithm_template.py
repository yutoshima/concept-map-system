#!/usr/bin/env python3

"""
カスタムアルゴリズムのテンプレート

このテンプレートをコピーして独自のアルゴリズムを実装してください。
"""

from pathlib import Path
from typing import Any, Dict

from ..core import BaseAlgorithm, constants
from ..core.constants import ResultKeys
from ..core.exceptions import AlgorithmExecutionError
from ..utils.formatting import create_separator, create_title_block, join_output


# @register_algorithm デコレータを使用すると自動的に登録されます
# 実際に使用する際はコメントを外してください
# @register_algorithm
class CustomAlgorithm(BaseAlgorithm):
    """カスタムアルゴリズムのテンプレート"""

    def __init__(self):
        super().__init__(
            name="custom_algorithm",  # ← アルゴリズムの名前を変更してください
            description="カスタムアルゴリズムの説明",  # ← 説明を変更してください
        )

    def execute(self, master_file: str, student_file: str, **kwargs) -> Dict[str, Any]:
        """
        アルゴリズムを実行

        Args:
            master_file: 模範解答のファイルパス
            student_file: 生徒の回答のファイルパス
            **kwargs: 追加のオプション

        Returns:
            Dict[str, Any]: 実行結果
        """
        # ファイルの検証
        self.validate_files(master_file, student_file)

        # オプションの取得
        options = self._extract_execution_options(**kwargs)
        verbose = options["verbose"]
        debug = options["debug"]

        try:
            # ここにアルゴリズムの実装を記述してください

            # 例: ファイルを読み込む
            master_path = Path(master_file)
            with master_path.open(encoding=constants.FILE_ENCODING) as f:
                master_data = f.read()

            student_path = Path(student_file)
            with student_path.open(encoding=constants.FILE_ENCODING) as f:
                student_data = f.read()

            if debug:
                self.logger.debug(f"模範解答ファイルサイズ: {len(master_data)} bytes")
                self.logger.debug(f"生徒の回答ファイルサイズ: {len(student_data)} bytes")

            # 採点ロジックを実装
            # ...

            # 結果を返す
            results = {
                ResultKeys.METHOD: "CustomAlgorithm",
                ResultKeys.TOTAL_SCORE: 0,  # ← 計算した点数
                ResultKeys.MAX_SCORE: 100,  # ← 最大点数
                ResultKeys.PERCENTAGE: 0.0,  # ← パーセンテージ
                # 必要に応じて他の情報を追加
            }

            if verbose:
                results["verbose_info"] = {
                    "master_size": len(master_data),
                    "student_size": len(student_data),
                }

            return results

        except Exception as e:
            msg = f"カスタムアルゴリズム実行中にエラーが発生しました: {e!s}"
            raise AlgorithmExecutionError(msg) from e

    def get_supported_options(self) -> Dict[str, Dict[str, Any]]:
        """
        サポートされているオプションの定義を返す

        Returns:
            Dict[str, Dict[str, Any]]: オプション定義
        """
        # 共通オプションを取得
        options = self.get_common_options()

        # 必要に応じて独自のオプションを追加
        # options['custom_option'] = {
        #     'type': str,
        #     'default': 'default_value',
        #     'help': 'カスタムオプションの説明'
        # }

        return options

    def format_results(self, results: Dict[str, Any]) -> str:
        """
        結果を人間が読みやすい形式にフォーマット

        Args:
            results: 実行結果

        Returns:
            str: フォーマットされた結果
        """
        output = []
        output.extend(create_title_block("【カスタムアルゴリズム 採点結果】"))

        output.append(
            f"合計点数: {results.get('total_score', 0)}/{results.get('max_score', 0)} "
            f"({results.get('percentage', 0):.1f}%)"
        )

        # 必要に応じて他の情報を追加

        output.append("")
        output.append(create_separator("-", constants.SEPARATOR_WIDTH_LONG))

        return join_output(output)


# 使用方法:
# 1. このファイルをコピーして新しいファイルを作成
# 2. クラス名とアルゴリズム名を変更
# 3. execute() メソッドにアルゴリズムのロジックを実装
# 4. @register_algorithm デコレータのコメントを外す
# 5. algorithms/__init__.py で新しいモジュールをインポート
#
# 例:
#   from .custom_algorithm_template import CustomAlgorithm
