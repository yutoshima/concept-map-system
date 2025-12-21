#!/usr/bin/env python3

"""
基底アルゴリズムクラス
すべてのアルゴリズムはこのクラスを継承して実装する
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, cast

from .constants import ResultKeys
from .logging_config import get_logger


class BaseAlgorithm(ABC):
    """アルゴリズムの基底クラス"""

    def __init__(self, name: str, description: str):
        """
        Args:
            name: アルゴリズムの名前
            description: アルゴリズムの説明
        """
        self.name = name
        self.description = description
        self.master_file = None
        self.student_file = None
        self.options: Dict[str, Any] = {}
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
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

    @abstractmethod
    def get_supported_options(self) -> Dict[str, Dict[str, Any]]:
        """
        サポートされているオプションの定義を返す

        Returns:
            Dict[str, Dict[str, Any]]: オプション名とその定義の辞書
                例: {
                    'verbose': {
                        'type': bool,
                        'default': False,
                        'help': '詳細な結果を表示'
                    }
                }
        """

    def validate_files(self, master_file: str, student_file: str) -> bool:
        """
        ファイルが存在するか検証

        Args:
            master_file: 模範解答のファイルパス
            student_file: 生徒の回答のファイルパス

        Returns:
            bool: ファイルが存在する場合True
        """
        master_path = Path(master_file)
        student_path = Path(student_file)

        if not master_path.exists():
            msg = f"模範解答ファイルが見つかりません: {master_file}"
            raise FileNotFoundError(msg)

        if not student_path.exists():
            msg = f"生徒の回答ファイルが見つかりません: {student_file}"
            raise FileNotFoundError(msg)

        return True

    def _extract_execution_options(self, **kwargs: Any) -> Dict[str, bool]:
        """
        実行オプションを抽出

        共通の実行オプション（verbose, debug）を抽出し、
        デフォルト値を適用します。

        Args:
            **kwargs: 実行時に渡されたキーワード引数

        Returns:
            Dict[str, bool]: 抽出されたオプション
        """
        return {
            "verbose": kwargs.get("verbose", False),
            "debug": kwargs.get("debug", False),
        }

    def _has_data_attributes(self, scorer: Any) -> bool:
        """
        scorerがdata属性を持つかチェック

        Args:
            scorer: scorerオブジェクト

        Returns:
            master_dataとstudent_dataの両方を持つ場合True
        """
        return hasattr(scorer, "master_data") and hasattr(scorer, "student_data")

    def _has_map_attributes(self, scorer: Any) -> bool:
        """
        scorerがmap属性を持つかチェック

        Args:
            scorer: scorerオブジェクト

        Returns:
            master_mapとstudent_mapの両方を持つ場合True
        """
        return hasattr(scorer, "master_map") and hasattr(scorer, "student_map")

    def _log_data_info(self, scorer: Any, debug: bool) -> None:
        """
        データ読み込み情報をログに記録

        Args:
            scorer: scorerオブジェクト（master_data, student_data等の属性を持つ）
            debug: デバッグモードが有効な場合True
        """
        if debug and self._has_data_attributes(scorer):
            self.logger.debug(f"模範解答: {len(scorer.master_data)}行")
            self.logger.debug(f"生徒の回答: {len(scorer.student_data)}行")

            if self._has_map_attributes(scorer):
                self.logger.debug(f"展開後の模範命題: {len(scorer.master_map)}個")
                self.logger.debug(f"展開後の生徒命題: {len(scorer.student_map)}個")

    def _add_verbose_info(self, results: Dict[str, Any], scorer: Any, verbose: bool) -> None:
        """
        詳細情報を結果に追加

        Args:
            results: 採点結果の辞書（この辞書が直接変更されます）
            scorer: scorerオブジェクト
            verbose: verboseモードが有効な場合True
        """
        if verbose and self._has_data_attributes(scorer):
            verbose_info = {
                "master_data_count": len(scorer.master_data),
                "student_data_count": len(scorer.student_data),
            }

            if self._has_map_attributes(scorer):
                verbose_info["master_map_count"] = len(scorer.master_map)
                verbose_info["student_map_count"] = len(scorer.student_map)

            results["verbose_info"] = verbose_info

    def _execute_scoring_with_error_handling(
        self,
        scorer: Any,
        master_file: str,
        student_file: str,
        algorithm_name: str,
        verbose: bool,
        debug: bool,
        decompose_qualifiers: bool = False,
        expansion_mode: str = "",  # 空文字列の場合はデフォルト値を使用
    ) -> Dict[str, Any]:
        """
        共通の採点実行ロジックとエラーハンドリング

        Args:
            scorer: scorerオブジェクト
            master_file: 模範解答ファイルパス
            student_file: 生徒の回答ファイルパス
            algorithm_name: アルゴリズム名（エラーメッセージ用）
            verbose: verboseモードフラグ
            debug: debugモードフラグ
            decompose_qualifiers: 限定分解モードフラグ（後方互換性のため）
            expansion_mode: 展開モード ('none', 'qualifier', 'junction')

        Returns:
            Dict[str, Any]: 採点結果

        Raises:
            AlgorithmExecutionError: データエラーまたは実行エラー
        """
        from ..core.exceptions import (
            AlgorithmExecutionError,
            CSVLoadError,
            InvalidPropositionError,
            UnsupportedStructureError,
        )

        try:
            # 展開モードを設定
            expansion_mode = self._configure_scorer_expansion(scorer, expansion_mode, decompose_qualifiers)

            self.logger.info(f"データを読み込み中: master={master_file}, student={student_file}")
            scorer.load_data(master_file, student_file)
            self._log_data_info(scorer, debug)
            results = scorer.score_all()
            self._add_verbose_info(cast(Dict[str, Any], results), scorer, verbose)
            return cast(Dict[str, Any], results)

        except (CSVLoadError, InvalidPropositionError, UnsupportedStructureError) as e:
            msg = f"{algorithm_name}採点中のデータエラー: {e!s}"
            raise AlgorithmExecutionError(msg) from e

        except Exception as e:
            self.logger.exception(f"{algorithm_name}採点中に予期しないエラーが発生しました")
            msg = f"{algorithm_name}採点中に予期しないエラーが発生しました: {e!s}"
            raise AlgorithmExecutionError(msg) from e

    def _configure_scorer_expansion(
        self, scorer: Any, expansion_mode: str, decompose_qualifiers: bool = False
    ) -> str:
        """
        scorerの展開モードを設定

        Args:
            scorer: scorerインスタンス
            expansion_mode: 展開モード設定
            decompose_qualifiers: 後方互換性のための限定分解フラグ

        Returns:
            str: 実際に設定された展開モード
        """
        # 展開モードのデフォルト値を設定
        if not expansion_mode:
            from . import constants

            expansion_mode = constants.ExpansionModes.JUNCTION

        # 展開モードを設定（scorerがサポートしている場合）
        if hasattr(scorer, "set_expansion_mode"):
            scorer.set_expansion_mode(expansion_mode)
        elif hasattr(scorer, "set_decompose_qualifiers"):
            # 後方互換性のため
            scorer.set_decompose_qualifiers(decompose_qualifiers)

        return expansion_mode

    def _extract_scorer_parameters(self, **kwargs: Any) -> Dict[str, Any]:
        """
        kwargsからscorer固有のパラメータを抽出

        サブクラスでオーバーライドして、アルゴリズム固有のパラメータを抽出します。

        Args:
            **kwargs: 実行時に渡されたキーワード引数

        Returns:
            Dict[str, Any]: scorerのコンストラクタに渡すパラメータ
        """
        return {}

    def execute_with_scorer(
        self,
        master_file: str,
        student_file: str,
        scorer_factory: type,
        algorithm_name: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        scorerインスタンスを使用した採点実行のテンプレートメソッド

        共通の実行パターンを提供し、アルゴリズム間のコード重複を削減します。

        Args:
            master_file: 模範解答ファイルパス
            student_file: 生徒の回答ファイルパス
            scorer_factory: scorerクラス（インスタンス化に使用）
            algorithm_name: アルゴリズム名（エラーメッセージ用）
            **kwargs: 追加のオプション

        Returns:
            Dict[str, Any]: 採点結果
        """
        # ファイルの検証
        self.validate_files(master_file, student_file)

        # 共通オプションの抽出
        options = self._extract_execution_options(**kwargs)
        verbose = options["verbose"]
        debug = options["debug"]

        # 展開モードの取得
        from . import constants

        expansion_mode = kwargs.get("expansion_mode", constants.ExpansionModes.JUNCTION)

        # アルゴリズム固有のパラメータを抽出してscorerを作成
        scorer_params = self._extract_scorer_parameters(**kwargs)
        scorer = scorer_factory(**scorer_params)

        # 共通の実行ロジックとエラーハンドリング
        return self._execute_scoring_with_error_handling(
            scorer, master_file, student_file, algorithm_name, verbose, debug, False, expansion_mode
        )

    def format_results(self, results: Dict[str, Any]) -> str:
        """
        結果を人間が読みやすい形式にフォーマット

        Args:
            results: 実行結果

        Returns:
            str: フォーマットされた結果
        """
        from ..utils.formatting import create_title_block, join_output

        output = []
        output.extend(create_title_block(f"アルゴリズム: {self.name}"))

        for key, value in results.items():
            if key not in [ResultKeys.METHOD, ResultKeys.RESULTS]:
                output.append(f"{key}: {value}")

        return join_output(output)

    def get_info(self) -> Dict[str, Any]:
        """
        アルゴリズムの情報を返す

        Returns:
            Dict[str, Any]: アルゴリズムの情報
        """
        return {
            "name": self.name,
            "description": self.description,
            "supported_options": self.get_supported_options(),
        }

    @staticmethod
    def get_common_options() -> Dict[str, Dict[str, Any]]:
        """
        すべてのアルゴリズムに共通するオプションの定義を返す

        Returns:
            Dict[str, Dict[str, Any]]: 共通オプション定義
        """
        return {
            "verbose": {"type": bool, "default": False, "help": "詳細な採点結果を表示"},
            "debug": {"type": bool, "default": False, "help": "デバッグ情報を表示"},
        }
