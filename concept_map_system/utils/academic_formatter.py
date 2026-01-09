#!/usr/bin/env python3

"""
アカデミック出力フォーマッター

論文掲載用の高品質な表とレポートを生成するユーティリティ
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..core.logging_config import get_logger

logger = get_logger(__name__)


class AcademicTableFormatter:
    """論文品質の表フォーマッター"""

    @staticmethod
    def format_ascii_table(
        headers: List[str],
        rows: List[List[str]],
        title: Optional[str] = None,
        align: Optional[List[str]] = None,
    ) -> str:
        """
        ASCII罫線を使った表を生成

        Args:
            headers: ヘッダー行
            rows: データ行のリスト
            title: 表のタイトル（オプション）
            align: 各列の配置 ('left', 'center', 'right')

        Returns:
            フォーマット済みの表文字列
        """
        if not rows:
            return ""

        # デフォルトの配置（数値は右寄せ、それ以外は左寄せ）
        if align is None:
            align = []
            for i, header in enumerate(headers):
                # 最初の列サンプルで判定
                if rows and i < len(rows[0]):
                    try:
                        float(rows[0][i])
                        align.append("right")
                    except (ValueError, TypeError):
                        align.append("left")
                else:
                    align.append("left")

        # 各列の最大幅を計算
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # 罫線文字
        top_line = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        mid_line = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        bottom_line = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
        header_line = "╞" + "╪".join("═" * (w + 2) for w in col_widths) + "╡"

        def format_row(cells: List[str], widths: List[int], alignments: List[str]) -> str:
            """行をフォーマット"""
            formatted = []
            for cell, width, align_type in zip(cells, widths, alignments):
                cell_str = str(cell)
                if align_type == "right":
                    formatted.append(cell_str.rjust(width))
                elif align_type == "center":
                    formatted.append(cell_str.center(width))
                else:
                    formatted.append(cell_str.ljust(width))
            return "│ " + " │ ".join(formatted) + " │"

        # 表を構築
        lines = []

        # タイトル
        if title:
            total_width = sum(col_widths) + len(col_widths) * 3 + 1
            lines.append("┌" + "─" * (total_width - 2) + "┐")
            lines.append("│ " + title.center(total_width - 4) + " │")
            lines.append("├" + "┬".join("─" * (w + 2) for w in col_widths) + "┤")
        else:
            lines.append(top_line)

        # ヘッダー
        lines.append(format_row(headers, col_widths, ["center"] * len(headers)))
        lines.append(header_line)

        # データ行
        for i, row in enumerate(rows):
            lines.append(format_row(row, col_widths, align))
            if i < len(rows) - 1:
                # 最後の行以外は区切り線を追加しない（オプション）
                pass

        lines.append(bottom_line)

        return "\n".join(lines)

    @staticmethod
    def format_latex_table(
        headers: List[str],
        rows: List[List[str]],
        caption: Optional[str] = None,
        label: Optional[str] = None,
    ) -> str:
        """
        LaTeX形式の表を生成

        Args:
            headers: ヘッダー行
            rows: データ行のリスト
            caption: 表のキャプション
            label: LaTeXラベル

        Returns:
            LaTeX形式の表文字列
        """
        # 列の配置（最初の列は左、数値列は右）
        alignments = []
        for i, header in enumerate(headers):
            if i == 0:
                alignments.append("l")
            else:
                # 数値かどうかチェック
                try:
                    if rows and i < len(rows[0]):
                        float(rows[0][i])
                        alignments.append("r")
                    else:
                        alignments.append("c")
                except (ValueError, TypeError):
                    alignments.append("c")

        col_spec = "|" + "|".join(alignments) + "|"

        lines = [
            "\\begin{table}[htbp]",
            "  \\centering",
        ]

        if caption:
            lines.append(f"  \\caption{{{caption}}}")

        if label:
            lines.append(f"  \\label{{{label}}}")

        lines.extend(
            [
                f"  \\begin{{tabular}}{{{col_spec}}}",
                "    \\hline",
                f"    {' & '.join(f'\\textbf{{{h}}}' for h in headers)} \\\\",
                "    \\hline",
            ]
        )

        for row in rows:
            lines.append(f"    {' & '.join(str(cell) for cell in row)} \\\\")

        lines.extend(
            [
                "    \\hline",
                "  \\end{tabular}",
                "\\end{table}",
            ]
        )

        return "\n".join(lines)

    @staticmethod
    def format_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
        """
        Markdown形式の表を生成

        Args:
            headers: ヘッダー行
            rows: データ行のリスト

        Returns:
            Markdown形式の表文字列
        """
        # 各列の最大幅を計算
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # ヘッダー
        header_line = (
            "| " + " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " |"
        )

        # 区切り線（数値列は右寄せ）
        separators = []
        for i, w in enumerate(col_widths):
            # 数値かどうかチェック
            try:
                if rows and i < len(rows[0]):
                    float(rows[0][i])
                    separators.append("-" * (w - 1) + ":")
                else:
                    separators.append("-" * w)
            except (ValueError, TypeError):
                separators.append("-" * w)

        separator_line = "| " + " | ".join(separators) + " |"

        # データ行
        data_lines = []
        for row in rows:
            line = (
                "| "
                + " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
                + " |"
            )
            data_lines.append(line)

        return "\n".join([header_line, separator_line] + data_lines)

    @staticmethod
    def format_csv(headers: List[str], rows: List[List[str]]) -> str:
        """
        CSV形式のデータを生成

        Args:
            headers: ヘッダー行
            rows: データ行のリスト

        Returns:
            CSV形式の文字列
        """
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        return output.getvalue()


class AcademicResultFormatter:
    """論文品質の結果フォーマッター"""

    @staticmethod
    def format_metadata(
        algorithm_name: str,
        master_file: str,
        student_file: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        実行メタデータをフォーマット

        Args:
            algorithm_name: アルゴリズム名
            master_file: 模範解答ファイル
            student_file: 生徒回答ファイル
            options: 実行オプション

        Returns:
            フォーマット済みメタデータ
        """
        import os
        from pathlib import Path

        lines = [
            "=" * 70,
            "概念マップ採点結果レポート".center(70),
            "=" * 70,
            "",
            "【実行情報】",
            f"  実行日時:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"  アルゴリズム: {algorithm_name}",
            f"  模範解答:     {Path(master_file).name}",
            f"  生徒回答:     {Path(student_file).name}",
        ]

        if options:
            lines.append("")
            lines.append("【実行パラメータ】")
            for key, value in sorted(options.items()):
                if value is not None and value is not False:
                    lines.append(f"  {key}: {value}")

        lines.append("")
        lines.append("-" * 70)
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_result_summary(result: Dict[str, Any], format_type: str = "ascii") -> str:
        """
        結果サマリーを表形式でフォーマット

        Args:
            result: 採点結果辞書
            format_type: 出力形式 ('ascii', 'latex', 'markdown', 'csv')

        Returns:
            フォーマット済み結果文字列
        """
        method = result.get("method", "Unknown")

        # メトリクステーブル
        metrics_headers = ["指標", "値"]
        metrics_rows = []

        # 基本スコア
        total_score = result.get("total_score", 0)
        max_score = result.get("max_score", 0)
        percentage = result.get("percentage", 0.0)

        metrics_rows.append(["合計得点", f"{total_score}/{max_score}"])
        metrics_rows.append(["正答率", f"{percentage:.1f}%"])

        # F値等の評価指標
        if "f_value" in result:
            metrics_rows.append(["F値", f"{result['f_value']:.3f}"])
        if "precision" in result:
            metrics_rows.append(["適合率", f"{result['precision']:.3f}"])
        if "recall" in result:
            metrics_rows.append(["再現率", f"{result['recall']:.3f}"])

        # 命題数
        if "total_props" in result:
            metrics_rows.append(["総命題数", str(result["total_props"])])

        formatter = AcademicTableFormatter()

        if format_type == "latex":
            return formatter.format_latex_table(
                metrics_headers,
                metrics_rows,
                caption=f"{method}方式 採点結果",
                label=f"tab:{method.lower()}_results",
            )
        elif format_type == "markdown":
            return formatter.format_markdown_table(metrics_headers, metrics_rows)
        elif format_type == "csv":
            return formatter.format_csv(metrics_headers, metrics_rows)
        else:  # ascii
            return formatter.format_ascii_table(
                metrics_headers, metrics_rows, title=f"{method}方式 採点結果"
            )

    @staticmethod
    def format_comparison_table(
        results: List[Tuple[str, Dict[str, Any]]], format_type: str = "ascii"
    ) -> str:
        """
        複数アルゴリズムの比較表を生成

        Args:
            results: (アルゴリズム名, 結果辞書) のタプルリスト
            format_type: 出力形式 ('ascii', 'latex', 'markdown', 'csv')

        Returns:
            フォーマット済み比較表
        """
        headers = ["アルゴリズム", "得点", "正答率", "F値", "適合率", "再現率"]
        rows = []

        for algo_name, result in results:
            if not result:
                continue

            row = [
                algo_name,
                f"{result.get('total_score', 0)}/{result.get('max_score', 0)}",
                f"{result.get('percentage', 0.0):.1f}%",
                f"{result.get('f_value', 0.0):.3f}" if "f_value" in result else "N/A",
                f"{result.get('precision', 0.0):.3f}"
                if "precision" in result
                else "N/A",
                f"{result.get('recall', 0.0):.3f}" if "recall" in result else "N/A",
            ]
            rows.append(row)

        formatter = AcademicTableFormatter()

        if format_type == "latex":
            return formatter.format_latex_table(
                headers,
                rows,
                caption="採点アルゴリズム比較",
                label="tab:algorithm_comparison",
            )
        elif format_type == "markdown":
            return formatter.format_markdown_table(headers, rows)
        elif format_type == "csv":
            return formatter.format_csv(headers, rows)
        else:  # ascii
            return formatter.format_ascii_table(headers, rows, title="アルゴリズム比較")


def export_to_file(content: str, filepath: str, encoding: str = "utf-8") -> None:
    """
    コンテンツをファイルにエクスポート

    Args:
        content: 出力内容
        filepath: 出力ファイルパス
        encoding: 文字エンコーディング
    """
    from pathlib import Path

    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding=encoding) as f:
        f.write(content)

    logger.info(f"結果をエクスポートしました: {filepath}")
