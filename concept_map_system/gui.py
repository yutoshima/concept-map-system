#!/usr/bin/env python3

"""
概念マップ採点統合システム - GUI

すべてのアルゴリズムを統合したGUIインターフェース
"""

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

# アルゴリズムをインポート（自動登録）
from .core import (
    AlgorithmRegistry,
    ParallelExecutor,
    SequentialExecutor,
    constants,
    get_logger,
    setup_logging,
)
from .utils import ResultFormatter

# ロガーの取得
logger = get_logger(__name__)


class ConceptMapSystemGUI:
    """概念マップ採点統合システムGUIアプリケーション"""

    def __init__(self, root):
        self.root = root
        self.root.title(constants.APP_TITLE)
        self.root.geometry("1000x800")

        # 変数
        self.master_file = tk.StringVar()
        self.student_file = tk.StringVar()
        self.verbose = tk.BooleanVar(value=False)
        self.debug = tk.BooleanVar(value=False)
        self.parallel = tk.BooleanVar(value=False)

        # アルゴリズム選択用の変数
        self.algorithm_vars = {}

        # 結果
        self.results = {}

        self.setup_ui()
        self.load_algorithms()

    def setup_ui(self):
        """UIをセットアップ"""
        main_frame = self._setup_main_frame()
        self._setup_file_selection_frame(main_frame)
        self._setup_algorithm_selection_frame(main_frame)
        self._setup_settings_frame(main_frame)
        self._setup_action_buttons(main_frame)
        self._setup_results_frame(main_frame)
        self._setup_status_bar(main_frame)

    def _setup_main_frame(self) -> ttk.Frame:
        """メインフレームとタイトルをセットアップ"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore[arg-type]
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        title_label = ttk.Label(
            main_frame, text="概念マップ採点統合システム", font=("", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        return main_frame

    def _setup_file_selection_frame(self, parent: ttk.Frame) -> None:
        """ファイル選択セクションをセットアップ"""
        file_frame = ttk.LabelFrame(parent, text="ファイル選択", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)  # type: ignore[arg-type]

        # 模範解答ファイル
        ttk.Label(file_frame, text="模範解答 CSV:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.master_file, width=60).grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Button(file_frame, text="参照...", command=self.browse_master_file).grid(
            row=0, column=2, pady=5
        )

        # 生徒の回答ファイル
        ttk.Label(file_frame, text="生徒の回答 CSV:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.student_file, width=60).grid(
            row=1, column=1, padx=5, pady=5
        )
        ttk.Button(file_frame, text="参照...", command=self.browse_student_file).grid(
            row=1, column=2, pady=5
        )

    def _setup_algorithm_selection_frame(self, parent: ttk.Frame) -> None:
        """アルゴリズム選択セクションをセットアップ"""
        algo_frame = ttk.LabelFrame(parent, text="アルゴリズム選択", padding="10")
        algo_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)  # type: ignore[arg-type]

        self.algo_container = ttk.Frame(algo_frame)
        self.algo_container.grid(row=0, column=0, sticky=(tk.W, tk.E))  # type: ignore[arg-type]

        # 選択ボタン
        button_frame = ttk.Frame(algo_frame)
        button_frame.grid(row=1, column=0, pady=5)
        ttk.Button(button_frame, text="すべて選択", command=self.select_all_algorithms).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="選択解除", command=self.deselect_all_algorithms).pack(
            side=tk.LEFT, padx=5
        )

    def _setup_settings_frame(self, parent: ttk.Frame) -> None:
        """実行設定セクションをセットアップ"""
        settings_frame = ttk.LabelFrame(parent, text="実行設定", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)  # type: ignore[arg-type]

        ttk.Checkbutton(settings_frame, text="詳細な結果を表示", variable=self.verbose).grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        ttk.Checkbutton(settings_frame, text="デバッグ情報を表示", variable=self.debug).grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        ttk.Checkbutton(settings_frame, text="並列実行", variable=self.parallel).grid(
            row=2, column=0, sticky=tk.W, pady=2
        )

    def _setup_action_buttons(self, parent: ttk.Frame) -> None:
        """実行ボタンをセットアップ"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)

        ttk.Button(
            button_frame, text="採点実行", command=self.run_scoring, style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="結果をJSON保存", command=self.save_json).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="クリア", command=self.clear_results).pack(
            side=tk.LEFT, padx=5
        )

    def _setup_results_frame(self, parent: ttk.Frame) -> None:
        """結果表示エリアをセットアップ"""
        result_frame = ttk.LabelFrame(parent, text="採点結果", padding="10")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)  # type: ignore[arg-type]
        parent.rowconfigure(5, weight=1)

        self.result_text = scrolledtext.ScrolledText(
            result_frame, wrap=tk.WORD, width=90, height=25
        )
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore[arg-type]
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

    def _setup_status_bar(self, parent: ttk.Frame) -> None:
        """ステータスバーとプログレスバーをセットアップ"""
        self.status_var = tk.StringVar(value=constants.STATUS_READY)
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)  # type: ignore[arg-type]

        self.progress = ttk.Progressbar(parent, mode="indeterminate")
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)  # type: ignore[arg-type]

    def _handle_error(self, error_msg: str, log_msg: str, exception: bool = False) -> None:
        """
        エラー処理の共通ロジック

        Args:
            error_msg: ユーザーに表示するエラーメッセージ
            log_msg: ログに記録するメッセージ
            exception: Trueの場合、例外のスタックトレースをログに記録
        """
        self.progress.stop()
        self.status_var.set(constants.STATUS_ERROR)
        messagebox.showerror("エラー", error_msg)
        if exception:
            logger.exception(log_msg)
        else:
            logger.error(log_msg)

    def load_algorithms(self) -> None:
        """登録されているアルゴリズムを読み込み"""
        algorithms = AlgorithmRegistry.list_algorithms()

        # 既存のチェックボックスをクリア
        for widget in self.algo_container.winfo_children():
            widget.destroy()
        self.algorithm_vars.clear()

        # チェックボックスを作成
        for i, name in enumerate(algorithms):
            var = tk.BooleanVar(value=True)
            self.algorithm_vars[name] = var

            info = AlgorithmRegistry.get_algorithm_info(name)
            description = info["description"] if info else name

            cb = ttk.Checkbutton(self.algo_container, text=f"{name}: {description}", variable=var)
            cb.grid(row=i, column=0, sticky=tk.W, pady=2)

    def select_all_algorithms(self) -> None:
        """すべてのアルゴリズムを選択"""
        for var in self.algorithm_vars.values():
            var.set(True)

    def deselect_all_algorithms(self) -> None:
        """すべてのアルゴリズムの選択を解除"""
        for var in self.algorithm_vars.values():
            var.set(False)

    def browse_master_file(self) -> None:
        """模範解答ファイルを選択"""
        filename = filedialog.askopenfilename(
            title="模範解答CSVを選択", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.master_file.set(filename)

    def browse_student_file(self) -> None:
        """生徒の回答ファイルを選択"""
        filename = filedialog.askopenfilename(
            title="生徒の回答CSVを選択", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.student_file.set(filename)

    def run_scoring(self) -> None:
        """採点を実行"""
        # ファイルチェック
        if not self.master_file.get() or not self.student_file.get():
            messagebox.showerror("エラー", constants.ERROR_NO_FILES)
            logger.warning("ファイルが選択されていません")
            return

        # 選択されたアルゴリズムを取得
        selected_algorithms = [name for name, var in self.algorithm_vars.items() if var.get()]

        if not selected_algorithms:
            messagebox.showerror("エラー", constants.ERROR_NO_ALGORITHM)
            logger.warning("アルゴリズムが選択されていません")
            return

        # スレッドで実行
        thread = threading.Thread(target=self._run_scoring_thread, args=(selected_algorithms,))
        thread.start()

    def _run_scoring_thread(self, selected_algorithms: list) -> None:
        """採点をバックグラウンドで実行"""
        try:
            self.status_var.set(constants.STATUS_RUNNING)
            self.progress.start()
            self.result_text.delete(1.0, tk.END)
            self.root.update()
            logger.info(f"採点を開始: {len(selected_algorithms)}個のアルゴリズム")

            # 実行エンジンの選択
            executor = ParallelExecutor() if self.parallel.get() else SequentialExecutor()

            # 進捗コールバック
            def progress_callback(message: str) -> None:
                self.result_text.insert(tk.END, f"{message}\n")
                self.result_text.see(tk.END)
                self.root.update()

            # オプション
            options = {"verbose": self.verbose.get(), "debug": self.debug.get()}

            # 実行
            results = executor.execute_multiple(
                selected_algorithms,
                self.master_file.get(),
                self.student_file.get(),
                progress_callback=progress_callback,
                **options,
            )

            # 結果を保存
            self.results = {}
            for result in results:
                if result.success:
                    self.results[result.algorithm_name] = result.result

            # 結果を表示
            self.display_results(results)

            self.progress.stop()
            self.status_var.set(constants.STATUS_COMPLETED)
            success_msg = constants.SUCCESS_SCORING_COMPLETE.format(len(self.results), len(results))
            messagebox.showinfo("完了", success_msg)
            logger.info(f"採点が完了しました: 成功 {len(self.results)}/{len(results)}")

        except FileNotFoundError as e:
            error_msg = constants.ERROR_FILE_NOT_FOUND.format(str(e))
            self._handle_error(error_msg, f"ファイルが見つかりません: {e!s}")
        except ImportError as e:
            self._handle_error(
                f"必要なモジュールが見つかりません:\n{e!s}",
                f"インポートエラー: {e!s}",
            )
        except Exception as e:
            error_msg = constants.ERROR_DURING_SCORING.format(str(e))
            self._handle_error(error_msg, "採点中に予期しないエラーが発生しました", exception=True)

    def display_results(self, results: list) -> None:
        """結果を表示"""
        self.result_text.insert(tk.END, "\n" + constants.SEPARATOR_EXTRA_LONG + "\n")
        self.result_text.insert(tk.END, "採点結果サマリー\n")
        self.result_text.insert(tk.END, constants.SEPARATOR_EXTRA_LONG + "\n\n")

        # ResultFormatterを使用して結果を処理
        processed = ResultFormatter.process_results(results)

        # 各結果を表示
        for formatted_entry in processed["formatted_results"]:
            gui_output = ResultFormatter.format_result_for_gui(
                formatted_entry, constants.SEPARATOR_EXTRA_LONG
            )
            self.result_text.insert(tk.END, gui_output)

        self.result_text.see(tk.END)

    def save_json(self) -> None:
        """結果をJSON形式で保存"""
        if not self.results:
            messagebox.showwarning("警告", constants.ERROR_NO_RESULTS)
            logger.warning("保存する結果がありません")
            return

        filename = filedialog.asksaveasfilename(
            title="結果を保存",
            defaultextension=constants.JSON_EXTENSION,
            filetypes=constants.JSON_FILE_TYPES,
        )

        if filename:
            try:
                output_path = Path(filename)
                with output_path.open("w", encoding="utf-8") as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False)
                success_msg = constants.SUCCESS_FILE_SAVED.format(filename)
                messagebox.showinfo("完了", success_msg)
                logger.info(f"結果を保存しました: {filename}")
            except Exception as e:
                error_msg = constants.ERROR_DURING_SAVE.format(str(e))
                messagebox.showerror("エラー", error_msg)
                logger.exception(f"保存中にエラーが発生しました: {filename}")

    def clear_results(self) -> None:
        """結果をクリア"""
        self.result_text.delete(1.0, tk.END)
        self.results = {}
        self.status_var.set(constants.STATUS_READY)
        logger.info("結果をクリアしました")


def main() -> None:
    """GUIアプリケーションを起動"""
    # ロギングのセットアップ
    setup_logging()
    logger.info("GUIアプリケーションを起動します")

    root = tk.Tk()
    # GUIオブジェクトを作成（rootに紐付けられるため変数保持は不要）
    ConceptMapSystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
