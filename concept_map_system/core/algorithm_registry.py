#!/usr/bin/env python3

"""
アルゴリズムレジストリ
アルゴリズムの登録と管理を行う
"""

from typing import ClassVar, Dict, List, Optional, Type

from .base_algorithm import BaseAlgorithm
from .logging_config import get_logger

# ロガーの取得
logger = get_logger(__name__)


class AlgorithmRegistry:
    """アルゴリズムレジストリ（シングルトン）"""

    _instance: ClassVar[Optional["AlgorithmRegistry"]] = None
    _algorithms: ClassVar[Dict[str, Type[BaseAlgorithm]]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, algorithm_class: Type[BaseAlgorithm]) -> None:
        """
        アルゴリズムを登録

        Args:
            algorithm_class: アルゴリズムクラス
        """
        # インスタンスを作成して名前を取得
        instance = algorithm_class()  # type: ignore[call-arg]
        name = instance.name

        if name in cls._algorithms:
            logger.warning(f"アルゴリズム '{name}' は既に登録されています。上書きします。")

        cls._algorithms[name] = algorithm_class
        logger.info(f"アルゴリズム '{name}' を登録しました")

    @classmethod
    def unregister(cls, name: str) -> bool:
        """
        アルゴリズムの登録を解除

        Args:
            name: アルゴリズム名

        Returns:
            bool: 解除に成功した場合True
        """
        if name in cls._algorithms:
            del cls._algorithms[name]
            return True
        return False

    @classmethod
    def get_algorithm(cls, name: str) -> Optional[BaseAlgorithm]:
        """
        アルゴリズムを取得

        Args:
            name: アルゴリズム名

        Returns:
            Optional[BaseAlgorithm]: アルゴリズムのインスタンス
        """
        if name not in cls._algorithms:
            return None

        algorithm_class = cls._algorithms[name]
        return algorithm_class()  # type: ignore[call-arg]

    @classmethod
    def list_algorithms(cls) -> List[str]:
        """
        登録されているアルゴリズムの名前のリストを返す

        Returns:
            List[str]: アルゴリズム名のリスト
        """
        return list(cls._algorithms)

    @classmethod
    def get_all_algorithms(cls) -> Dict[str, BaseAlgorithm]:
        """
        すべてのアルゴリズムのインスタンスを返す

        Returns:
            Dict[str, BaseAlgorithm]: アルゴリズム名とインスタンスの辞書
        """
        return {name: cls._algorithms[name]() for name in cls._algorithms}  # type: ignore[call-arg]

    @classmethod
    def get_algorithm_info(cls, name: str) -> Optional[Dict]:
        """
        アルゴリズムの情報を取得

        Args:
            name: アルゴリズム名

        Returns:
            Optional[Dict]: アルゴリズムの情報
        """
        algorithm = cls.get_algorithm(name)
        if algorithm:
            return algorithm.get_info()
        return None

    @classmethod
    def clear(cls) -> None:
        """すべてのアルゴリズムを登録解除"""
        cls._algorithms.clear()


def register_algorithm(algorithm_class: Type[BaseAlgorithm]) -> Type[BaseAlgorithm]:
    """
    アルゴリズムを登録するデコレータ

    Args:
        algorithm_class: アルゴリズムクラス

    Returns:
        Type[BaseAlgorithm]: 登録されたアルゴリズムクラス
    """
    AlgorithmRegistry.register(algorithm_class)
    return algorithm_class
