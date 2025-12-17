#!/usr/bin/env python3

"""
概念マップ採点統合システム - CLI

すべてのアルゴリズムを統合したコマンドラインインターフェース
"""

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Union

# アルゴリズムをインポート（自動登録）
from .core import (
    AlgorithmRegistry,
    ParallelExecutor,
    SequentialExecutor,
    constants,
    setup_logging,
)
from .core.constants import ResultKeys
from .utils import ResultFormatter

# アルゴリズムをインポートして登録
from . import algorithms  # noqa: F401


def save_json_output(output_path: str, data: Dict[str, Any]) -> None:
    """
    JSON形式で結果を保存

    Args:
        output_path: 出力ファイルパス
        data: 保存するデータ
    """
    path = Path(output_path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n結果を {output_path} に保存しました")


def print_colored(text: str, color: str = "default") -> None:
    """色付きテキストを出力"""
    if sys.platform == "win32":
        print(text)
        return

    colors = {
        "red": constants.COLOR_RED,
        "green": constants.COLOR_GREEN,
        "yellow": constants.COLOR_YELLOW,
        "blue": constants.COLOR_BLUE,
        "magenta": constants.COLOR_MAGENTA,
        "cyan": constants.COLOR_CYAN,
        "default": constants.COLOR_DEFAULT,
        "bold": constants.COLOR_BOLD,
    }
    print(f"{colors.get(color, '')}{text}{colors['default']}")


def list_algorithms() -> None:
    """登録されているアルゴリズムの一覧を表示"""
    algorithms = AlgorithmRegistry.list_algorithms()

    if not algorithms:
        print_colored("登録されているアルゴリズムはありません", "yellow")
        return

    print_colored("\n利用可能なアルゴリズム:", "bold")
    print_colored(constants.SEPARATOR_LONG, "cyan")

    for name in algorithms:
        info = AlgorithmRegistry.get_algorithm_info(name)
        if info:
            print(f"\n{name}:")
            print(f"  説明: {info['description']}")
            print("  オプション:")
            for opt_name, opt_def in info["supported_options"].items():
                print(f"    --{opt_name}: {opt_def['help']} (デフォルト: {opt_def['default']})")

    print_colored("\n" + constants.SEPARATOR_LONG, "cyan")


def run_single_algorithm(args: argparse.Namespace) -> int:
    """単一のアルゴリズムを実行"""
    algorithm = AlgorithmRegistry.get_algorithm(args.algorithm)

    if not algorithm:
        print_colored(f"エラー: アルゴリズム '{args.algorithm}' が見つかりません", "red")
        print("\n利用可能なアルゴリズムを表示するには: --list を使用してください")
        return 1

    print_colored(f"\n{algorithm.name} で採点を実行中...", "cyan")

    try:
        # オプションの準備
        options = {"verbose": args.verbose, "debug": args.debug}

        # アルゴリズム固有のオプションを追加
        if hasattr(args, "cross_link_score") and args.cross_link_score is not None:
            options["cross_link_score"] = args.cross_link_score

        # 実行
        executor = SequentialExecutor()
        result = executor.execute_single(algorithm, args.master_file, args.student_file, **options)

        if result.success:
            print_colored(f"\n✓ 採点完了 ({result.execution_time:.2f}秒)", "green")

            # 結果を表示
            if result.result:
                formatted = algorithm.format_results(result.result)
                print(formatted)

            # JSON出力
            if args.output:
                save_json_output(args.output, result.result)

            return 0
        print_colored(f"\n✗ エラー: {result.error}", "red")
        return 1

    except Exception as e:
        print_colored(f"\n✗ エラー: {e!s}", "red")
        if args.debug:
            traceback.print_exc()
        return 1


def run_multiple_algorithms(args: argparse.Namespace) -> int:
    """複数のアルゴリズムを実行"""
    algorithm_names = args.algorithms.split(",")
    algorithm_names = [name.strip() for name in algorithm_names]

    print_colored(f"\n{len(algorithm_names)}個のアルゴリズムを実行中...", "cyan")

    # 並列実行の選択
    executor: Union[ParallelExecutor, SequentialExecutor]
    if args.parallel:
        print_colored("並列実行モード", "cyan")
        executor = ParallelExecutor(max_workers=args.workers, use_processes=args.use_processes)
    else:
        print_colored("逐次実行モード", "cyan")
        executor = SequentialExecutor()

    try:
        # 進捗コールバック
        def progress_callback(message: str) -> None:
            print(f"  → {message}")

        # オプションの準備
        options = {"verbose": args.verbose, "debug": args.debug}

        # アルゴリズム固有のオプションを追加
        if hasattr(args, "cross_link_score") and args.cross_link_score is not None:
            options["cross_link_score"] = args.cross_link_score

        # 実行
        results = executor.execute_multiple(
            algorithm_names,
            args.master_file,
            args.student_file,
            progress_callback=progress_callback,
            **options,
        )

        # 結果の表示
        print_colored("\n" + constants.SEPARATOR_LONG, "cyan")
        print_colored("実行結果サマリー", "bold")
        print_colored(constants.SEPARATOR_LONG, "cyan")

        # ResultFormatterを使用して結果を処理
        processed = ResultFormatter.process_results(results)
        success_count = processed["success_count"]
        all_results = processed["all_results"]

        # 各結果を表示
        for formatted_entry in processed["formatted_results"]:
            cli_output = ResultFormatter.format_result_for_cli(formatted_entry)
            if formatted_entry["success"]:
                print_colored(f"\n{cli_output}", "green")
            else:
                print_colored(f"\n{cli_output}", "red")

        # サマリーを表示
        summary = ResultFormatter.format_success_summary(success_count, processed["total_count"])
        print_colored(f"\n{summary}", "bold")

        # JSON出力
        if args.output and all_results:
            output_data = {
                "algorithms": algorithm_names,
                "success_count": success_count,
                "total_count": len(results),
                ResultKeys.RESULTS: all_results,
            }
            save_json_output(args.output, output_data)

        return 0 if success_count == len(results) else 1

    except Exception as e:
        print_colored(f"\n✗ エラー: {e!s}", "red")
        if args.debug:
            traceback.print_exc()
        return 1


def run_all_algorithms(args: argparse.Namespace) -> int:
    """すべてのアルゴリズムを実行"""
    algorithm_names = AlgorithmRegistry.list_algorithms()

    if not algorithm_names:
        print_colored("登録されているアルゴリズムはありません", "yellow")
        return 1

    print_colored(f"\nすべてのアルゴリズム ({len(algorithm_names)}個) を実行中...", "cyan")

    # argsを更新
    args.algorithms = ",".join(algorithm_names)

    return run_multiple_algorithms(args)


def _create_argument_parser() -> argparse.ArgumentParser:
    """
    コマンドライン引数パーサーを作成

    Returns:
        設定済みのArgumentParser
    """
    parser = argparse.ArgumentParser(
        description=constants.APP_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 単一のアルゴリズムを実行
  python -m concept_map_system.cli -a mcclure master.csv student.csv

  # 複数のアルゴリズムを逐次実行
  python -m concept_map_system.cli --algorithms mcclure,novak master.csv student.csv

  # 複数のアルゴリズムを並列実行
  python -m concept_map_system.cli --algorithms mcclure,novak --parallel master.csv student.csv

  # すべてのアルゴリズムを並列実行
  python -m concept_map_system.cli --all --parallel master.csv student.csv

  # 利用可能なアルゴリズムの一覧を表示
  python -m concept_map_system.cli --list
        """,
    )

    # ファイル引数
    parser.add_argument("master_file", nargs="?", help="模範解答のCSVファイル")
    parser.add_argument("student_file", nargs="?", help="生徒の回答のCSVファイル")

    # アルゴリズム選択
    parser.add_argument("-a", "--algorithm", help="実行するアルゴリズム名")
    parser.add_argument("--algorithms", help="実行するアルゴリズム名（カンマ区切り）")
    parser.add_argument("--all", action="store_true", help="すべてのアルゴリズムを実行")
    parser.add_argument("--list", action="store_true", help="利用可能なアルゴリズムの一覧を表示")

    # 実行オプション
    parser.add_argument("--parallel", action="store_true", help="並列実行モードを使用")
    parser.add_argument("--workers", type=int, help="並列実行時のワーカー数")
    parser.add_argument(
        "--use-processes",
        action="store_true",
        help="スレッドではなくプロセスベースの並列実行を使用",
    )

    # 出力オプション
    parser.add_argument("-v", "--verbose", action="store_true", help="詳細な結果を表示")
    parser.add_argument("-d", "--debug", action="store_true", help="デバッグ情報を表示")
    parser.add_argument("-o", "--output", help="結果をJSONファイルに出力")

    # アルゴリズム固有のオプション
    parser.add_argument(
        "--cross-link-score",
        type=int,
        default=None,
        help="[Novak専用] 交差リンク（Conflict）1つあたりの点数 (0-4点)",
    )

    return parser


def _handle_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    """
    コマンドを処理

    Args:
        args: パース済みの引数
        parser: 引数パーサー（ヘルプ表示用）

    Returns:
        終了コード
    """
    # アルゴリズム一覧表示
    if args.list:
        list_algorithms()
        return 0

    # ファイルチェック
    if not args.master_file or not args.student_file:
        parser.print_help()
        print_colored("\nエラー: 模範解答と生徒の回答のファイルを指定してください", "red")
        return 1

    # すべてのアルゴリズムを実行
    if args.all:
        return run_all_algorithms(args)

    # 複数のアルゴリズムを実行
    if args.algorithms:
        return run_multiple_algorithms(args)

    # 単一のアルゴリズムを実行
    if args.algorithm:
        return run_single_algorithm(args)

    # アルゴリズムが指定されていない場合
    parser.print_help()
    print_colored(
        "\nエラー: アルゴリズムを指定してください (-a, --algorithms, または --all)", "red"
    )
    return 1


def main() -> int:
    """メイン関数"""
    parser = _create_argument_parser()
    args = parser.parse_args()

    # ロギングのセットアップ
    setup_logging(verbose=getattr(args, "verbose", False), debug=getattr(args, "debug", False))

    return _handle_command(args, parser)


if __name__ == "__main__":
    sys.exit(main())
