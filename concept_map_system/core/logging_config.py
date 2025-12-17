#!/usr/bin/env python3

"""
ロギング設定モジュール

プロジェクト全体で使用する統一されたロギング設定を提供します。
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    verbose: bool = False,
    debug: bool = False,
) -> logging.Logger:
    """
    ロギングを設定

    Args:
        level: ログレベル（デフォルト: INFO）
        log_file: ログファイルのパス（Noneの場合は標準出力のみ）
        verbose: 詳細モード（Trueの場合はINFOレベル）
        debug: デバッグモード（Trueの場合はDEBUGレベル）

    Returns:
        logging.Logger: 設定されたロガー
    """
    # デバッグモードが優先
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO

    # ルートロガーを取得
    logger = logging.getLogger("concept_map_system")
    logger.setLevel(level)

    # 既存のハンドラーをクリア
    logger.handlers.clear()

    # フォーマッターの設定
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ファイルハンドラーの設定（指定された場合）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "concept_map_system") -> logging.Logger:
    """
    ロガーを取得

    Args:
        name: ロガー名

    Returns:
        logging.Logger: ロガーインスタンス
    """
    return logging.getLogger(name)
