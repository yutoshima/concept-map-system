#!/usr/bin/env python3

"""
結果フォーマッティングユーティリティ

ExecutionResultのリストを処理し、フォーマットされた結果を提供する
"""

from typing import Any, Dict, List

from ..core.algorithm_registry import AlgorithmRegistry
from ..core.executor import ExecutionResult


class ResultFormatter:
    """採点結果のフォーマッティングユーティリティ"""

    @staticmethod
    def process_results(results: List[ExecutionResult]) -> Dict[str, Any]:
        """
        実行結果をprocessして統計情報を返す

        Args:
            results: ExecutionResultのリスト

        Returns:
            処理された結果の辞書
                - success_count: 成功した数
                - total_count: 総数
                - formatted_results: フォーマット済み結果のリスト
                - all_results: 全結果の辞書
        """
        success_count = 0
        all_results = {}
        formatted_results = []

        for result in results:
            formatted_entry = ResultFormatter._format_single_result(result)
            formatted_results.append(formatted_entry)

            if result.success:
                success_count += 1
                if result.result:
                    all_results[result.algorithm_name] = result.result

        return {
            "success_count": success_count,
            "total_count": len(results),
            "formatted_results": formatted_results,
            "all_results": all_results,
        }

    @staticmethod
    def _format_single_result(result: ExecutionResult) -> Dict[str, Any]:
        """
        単一の実行結果をフォーマット

        Args:
            result: ExecutionResult

        Returns:
            フォーマット済み結果の辞書
        """
        formatted_entry = {
            "algorithm_name": result.algorithm_name,
            "success": result.success,
            "execution_time": result.execution_time,
            "formatted_output": None,
            "error": result.error,
        }

        if result.success:
            algo = AlgorithmRegistry.get_algorithm(result.algorithm_name)
            if algo and result.result:
                formatted_entry["formatted_output"] = algo.format_results(result.result)

        return formatted_entry

    @staticmethod
    def format_success_summary(success_count: int, total_count: int) -> str:
        """
        成功数のサマリーをフォーマット

        Args:
            success_count: 成功数
            total_count: 総数

        Returns:
            フォーマットされたサマリー文字列
        """
        return f"成功: {success_count}/{total_count}"

    @staticmethod
    def _format_result_base(
        formatted_entry: Dict[str, Any],
        separator: str = "",
        prefix: str = "",
        include_error_prefix: bool = True,
    ) -> str:
        """
        結果フォーマットの共通ロジック

        Args:
            formatted_entry: フォーマット済みエントリ
            separator: セパレータ文字列（空の場合は追加しない）
            prefix: 行の先頭プレフィックス
            include_error_prefix: エラー行にプレフィックスを含めるか

        Returns:
            フォーマット済み文字列
        """
        lines = []
        algo_name = formatted_entry["algorithm_name"]
        exec_time = formatted_entry["execution_time"]

        if formatted_entry["success"]:
            lines.append(f"{prefix}✓ {algo_name}: 成功 ({exec_time:.2f}秒)")
            if separator:
                lines.append(separator)
            if formatted_entry["formatted_output"]:
                lines.append(formatted_entry["formatted_output"])
        else:
            error = formatted_entry["error"]
            if include_error_prefix:
                lines.append(f"{prefix}✗ {algo_name}: 失敗 - {error}")
            else:
                lines.append(f"{prefix}✗ {algo_name}: 失敗")
                lines.append(f"エラー: {error}")

        return "\n".join(lines)

    @staticmethod
    def format_result_for_cli(formatted_entry: Dict[str, Any]) -> str:
        """
        CLI用に結果をフォーマット

        Args:
            formatted_entry: フォーマット済みエントリ

        Returns:
            CLI表示用の文字列
        """
        return ResultFormatter._format_result_base(
            formatted_entry, separator="", prefix="", include_error_prefix=True
        )

    @staticmethod
    def format_result_for_gui(formatted_entry: Dict[str, Any], separator: str) -> str:
        """
        GUI用に結果をフォーマット

        Args:
            formatted_entry: フォーマット済みエントリ
            separator: セパレータ文字列

        Returns:
            GUI表示用の文字列
        """
        result = ResultFormatter._format_result_base(
            formatted_entry, separator=separator, prefix="\n", include_error_prefix=False
        )
        return result + "\n"  # 末尾に空行
