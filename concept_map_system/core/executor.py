#!/usr/bin/env python3

"""
並列実行エンジン
複数のアルゴリズムを並列に実行する
"""

import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional

from .algorithm_registry import AlgorithmRegistry
from .base_algorithm import BaseAlgorithm


class ExecutionResult:
    """実行結果を表すクラス"""

    def __init__(
        self,
        algorithm_name: str,
        success: bool,
        result: Any = None,
        error: Optional[str] = None,
        execution_time: float = 0.0,
    ):
        self.algorithm_name = algorithm_name
        self.success = success
        self.result = result
        self.error = error
        self.execution_time = execution_time

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "algorithm_name": self.algorithm_name,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
        }

    def __repr__(self):
        status = "成功" if self.success else "失敗"
        return f"<ExecutionResult: {self.algorithm_name} - {status} ({self.execution_time:.2f}s)>"

    @staticmethod
    def create_algorithm_not_found(name: str) -> "ExecutionResult":
        """
        アルゴリズムが見つからない場合のExecutionResultを作成

        Args:
            name: アルゴリズム名

        Returns:
            ExecutionResult: 失敗結果
        """
        return ExecutionResult(
            algorithm_name=name,
            success=False,
            error=f"アルゴリズム '{name}' が見つかりません",
        )


def _report_progress(
    callback: Optional[Callable[[str], None]], algo_name: str, status: str
) -> None:
    """
    進捗をコールバックで報告

    Args:
        callback: 進捗コールバック関数
        algo_name: アルゴリズム名
        status: ステータスメッセージ
    """
    if callback:
        callback(f"{algo_name}: {status}")


class ParallelExecutor:
    """並列実行エンジン"""

    def __init__(self, max_workers: Optional[int] = None, use_processes: bool = False):
        """
        Args:
            max_workers: 最大ワーカー数（Noneの場合は自動）
            use_processes: Trueの場合プロセスベース、Falseの場合スレッドベース
        """
        self.max_workers = max_workers
        self.use_processes = use_processes

    def execute_single(
        self, algorithm: BaseAlgorithm, master_file: str, student_file: str, **kwargs
    ) -> ExecutionResult:
        """
        単一のアルゴリズムを実行

        Args:
            algorithm: アルゴリズムインスタンス
            master_file: 模範解答ファイル
            student_file: 生徒の回答ファイル
            **kwargs: 追加のオプション

        Returns:
            ExecutionResult: 実行結果
        """
        start_time = time.time()

        try:
            # ファイルの検証
            algorithm.validate_files(master_file, student_file)

            # アルゴリズムの実行
            result = algorithm.execute(master_file, student_file, **kwargs)

            execution_time = time.time() - start_time

            return ExecutionResult(
                algorithm_name=algorithm.name,
                success=True,
                result=result,
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                algorithm_name=algorithm.name,
                success=False,
                error=str(e),
                execution_time=execution_time,
            )

    def execute_multiple(
        self,
        algorithm_names: List[str],
        master_file: str,
        student_file: str,
        progress_callback: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> List[ExecutionResult]:
        """
        複数のアルゴリズムを並列に実行

        Args:
            algorithm_names: アルゴリズム名のリスト
            master_file: 模範解答ファイル
            student_file: 生徒の回答ファイル
            progress_callback: 進捗コールバック関数
            **kwargs: 追加のオプション

        Returns:
            List[ExecutionResult]: 実行結果のリスト
        """
        results = []

        # アルゴリズムを取得
        algorithms = []
        for name in algorithm_names:
            algo = AlgorithmRegistry.get_algorithm(name)
            if algo is None:
                results.append(ExecutionResult.create_algorithm_not_found(name))
            else:
                algorithms.append(algo)

        if not algorithms:
            return results

        # 並列実行
        executor_class = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor

        with executor_class(max_workers=self.max_workers) as executor:
            # タスクを送信
            future_to_algo = {
                executor.submit(
                    self.execute_single, algo, master_file, student_file, **kwargs
                ): algo
                for algo in algorithms
            }

            # 完了したタスクを処理
            for future in as_completed(future_to_algo):
                algo = future_to_algo[future]

                try:
                    result = future.result()
                    results.append(result)
                    status = "完了" if result.success else "失敗"
                    _report_progress(progress_callback, algo.name, status)

                except Exception as e:
                    results.append(
                        ExecutionResult(algorithm_name=algo.name, success=False, error=str(e))
                    )
                    _report_progress(progress_callback, algo.name, f"エラー - {e!s}")

        return results

    def execute_all(
        self,
        master_file: str,
        student_file: str,
        progress_callback: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> List[ExecutionResult]:
        """
        すべての登録されたアルゴリズムを並列に実行

        Args:
            master_file: 模範解答ファイル
            student_file: 生徒の回答ファイル
            progress_callback: 進捗コールバック関数
            **kwargs: 追加のオプション

        Returns:
            List[ExecutionResult]: 実行結果のリスト
        """
        algorithm_names = AlgorithmRegistry.list_algorithms()
        return self.execute_multiple(
            algorithm_names, master_file, student_file, progress_callback, **kwargs
        )


class SequentialExecutor:
    """逐次実行エンジン"""

    def execute_single(
        self, algorithm: BaseAlgorithm, master_file: str, student_file: str, **kwargs
    ) -> ExecutionResult:
        """
        単一のアルゴリズムを実行

        Args:
            algorithm: アルゴリズムインスタンス
            master_file: 模範解答ファイル
            student_file: 生徒の回答ファイル
            **kwargs: 追加のオプション

        Returns:
            ExecutionResult: 実行結果
        """
        executor = ParallelExecutor(max_workers=1)
        return executor.execute_single(algorithm, master_file, student_file, **kwargs)

    def execute_multiple(
        self,
        algorithm_names: List[str],
        master_file: str,
        student_file: str,
        progress_callback: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> List[ExecutionResult]:
        """
        複数のアルゴリズムを逐次実行

        Args:
            algorithm_names: アルゴリズム名のリスト
            master_file: 模範解答ファイル
            student_file: 生徒の回答ファイル
            progress_callback: 進捗コールバック関数
            **kwargs: 追加のオプション

        Returns:
            List[ExecutionResult]: 実行結果のリスト
        """
        results = []

        for name in algorithm_names:
            algo = AlgorithmRegistry.get_algorithm(name)

            if algo is None:
                results.append(ExecutionResult.create_algorithm_not_found(name))
                _report_progress(progress_callback, name, "エラー - アルゴリズムが見つかりません")
                continue

            result = self.execute_single(algo, master_file, student_file, **kwargs)
            results.append(result)
            status = "完了" if result.success else "失敗"
            _report_progress(progress_callback, algo.name, status)

        return results
