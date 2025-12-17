#!/usr/bin/env python3

"""
概念マップ採点統合システム - メインエントリーポイント

python -m concept_map_system で実行可能
"""

import argparse
import sys

from .cli import main as cli_main
from .gui import main as gui_main


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="概念マップ採点統合システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方法:
  # CLIを起動
  python -m concept_map_system cli [options]

  # GUIを起動
  python -m concept_map_system gui

詳細なヘルプ:
  python -m concept_map_system cli --help
        """,
    )

    parser.add_argument(
        "mode", nargs="?", default="cli", choices=["cli", "gui"], help="実行モード (cli または gui)"
    )

    # CLIのオプションを取得するため、unknownを許可
    args, remaining = parser.parse_known_args()

    if args.mode == "gui":
        # GUIを起動
        gui_main()
    else:
        # CLIを起動
        # remainingをsys.argvに設定してCLIに渡す
        sys.argv = [sys.argv[0], *remaining]
        sys.exit(cli_main())


if __name__ == "__main__":
    main()
