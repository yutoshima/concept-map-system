#!/usr/bin/env python3

"""
定数定義モジュール

プロジェクト全体で使用する定数を一元管理します。
"""

# アプリケーション情報
APP_NAME = "概念マップ採点統合システム"
APP_TITLE = "概念マップ採点統合システム"

# ファイル関連
CSV_EXTENSION = ".csv"
JSON_EXTENSION = ".json"
CSV_FILE_TYPES = [("CSV files", "*.csv"), ("All files", "*.*")]
JSON_FILE_TYPES = [("JSON files", "*.json"), ("All files", "*.*")]

# UI関連のメッセージ
UI_MASTER_FILE_LABEL = "模範解答 CSV:"
UI_STUDENT_FILE_LABEL = "生徒の回答 CSV:"
UI_BROWSE_BUTTON = "参照..."
UI_ALGORITHM_SELECTION = "アルゴリズム選択"
UI_EXECUTION_SETTINGS = "実行設定"
UI_VERBOSE_OPTION = "詳細な結果を表示"
UI_DEBUG_OPTION = "デバッグ情報を表示"
UI_PARALLEL_OPTION = "並列実行"
UI_RUN_BUTTON = "採点実行"
UI_SAVE_JSON_BUTTON = "結果をJSON保存"
UI_CLEAR_BUTTON = "クリア"
UI_RESULTS_LABEL = "採点結果"
UI_SELECT_ALL_BUTTON = "すべて選択"
UI_DESELECT_ALL_BUTTON = "選択解除"

# ステータスメッセージ
STATUS_READY = "準備完了"
STATUS_RUNNING = "採点中..."
STATUS_COMPLETED = "採点完了"
STATUS_ERROR = "エラー"

# エラーメッセージ
ERROR_NO_FILES = "模範解答と生徒の回答のCSVファイルを選択してください"
ERROR_NO_ALGORITHM = "少なくとも1つのアルゴリズムを選択してください"
ERROR_FILE_NOT_FOUND = "ファイルが見つかりません: {}"
ERROR_NO_RESULTS = "まず採点を実行してください"
ERROR_DURING_SCORING = "採点中にエラーが発生しました: {}"
ERROR_DURING_SAVE = "保存中にエラーが発生しました: {}"

# 成功メッセージ
SUCCESS_SCORING_COMPLETE = "採点が完了しました\n成功: {}/{}"
SUCCESS_FILE_SAVED = "結果を {} に保存しました"

# 色定義（CLI用）
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_MAGENTA = "\033[95m"
COLOR_CYAN = "\033[96m"
COLOR_DEFAULT = "\033[0m"
COLOR_BOLD = "\033[1m"

# フォーマット関連
SEPARATOR_LONG = "=" * 60
SEPARATOR_SHORT = "-" * 40
SEPARATOR_EXTRA_LONG = "=" * 80
SEPARATOR_WIDTH_SHORT = 40
SEPARATOR_WIDTH_LONG = 60
SEPARATOR_WIDTH_EXTRA_LONG = 80

# ファイル処理関連
FILE_ENCODING = "utf-8-sig"

# UI レイアウト関連
UI_PADDING = 5
UI_PADDING_LARGE = 10
UI_ENTRY_WIDTH = 60
UI_TEXT_WIDTH = 90
UI_TEXT_HEIGHT = 25

# 命題ID関連
NODE_ID_SEPARATOR = "_"
JUNCTION_PREFIX_FROM = "t_from_"
JUNCTION_PREFIX_TO = "t_to_"


# アルゴリズム名定数
class AlgorithmNames:
    """アルゴリズム名の定数（今後の変更に対応）"""

    MCCLURE = "McClure"
    NOVAK = "Novak"
    LEA = "LEA"  # Link Evaluation Algorithm（旧称: WLEA）


# 展開モード定数
class ExpansionModes:
    """展開モードの定数"""

    NONE = "none"  # 展開しない
    QUALIFIER = "qualifier"  # Qualifier方式
    JUNCTION = "junction"  # Junction方式（デフォルト）


# スコアリングシステム定数
class ScoringConstants:
    """採点システムの定数"""

    # McClure方式のスコア
    MCCLURE_PERFECT_MATCH = 3
    MCCLURE_DIRECTION_MISMATCH = 2
    MCCLURE_LABEL_MISMATCH = 1
    MCCLURE_NO_MATCH = 0

    # Novak方式のスコア
    NOVAK_PERFECT_MATCH = 3
    NOVAK_NO_MATCH = 0
    NOVAK_LIMITATION_BONUS = 4

    # 交差リンク（Conflict）スコア範囲
    CROSS_LINK_MIN_SCORE = 0
    CROSS_LINK_MAX_SCORE = 4

    # LEA (Link Evaluation Algorithm) のスコア
    LEA_MAX_SCORE = 4
    LEA_PERFECT_MATCH = 4
    LEA_TYPE_MISMATCH = 3
    LEA_PARTIAL_MATCH = 2
    LEA_PARTIAL_TYPE_MISMATCH = 1
    LEA_NO_MATCH = 0

    # 特殊なリンクタイプ
    CONFLICT_LINK_TYPE = "conflict"
    JUNCTION_TYPE = "Junction"


# 結果辞書のキー名
class ResultKeys:
    """結果辞書の標準キー名（エイリアス付き）"""

    # 基本キー
    METHOD = "method"
    RESULTS = "results"
    SCORE_COUNTS = "score_counts"

    # スコアリングキー（標準）
    TOTAL_SCORE = "total_score"
    RAW_SCORE = "raw_score"  # TOTAL_SCOREのエイリアス（主にLEA用）
    MAX_SCORE = "max_score"
    MAX_POSSIBLE_SCORE = "max_possible_score"  # MAX_SCOREのエイリアス（主にLEA用）
    PERCENTAGE = "percentage"
    SCORE_RATE = "score_rate"  # PERCENTAGEのエイリアス（0.0-1.0形式）

    # マッチングキー（標準）
    MATCHED_COUNT = "matched_count"
    MATCHED_PAIRS = "matched_pairs"  # MATCHED_COUNTのエイリアス（主にLEA用）

    # カウントキー
    TOTAL_PROPS = "total_props"
    MASTER_PROPS = "master_props"
    STUDENT_PROPS = "student_props"

    # 評価指標
    PRECISION = "precision"
    RECALL = "recall"
    F_VALUE = "f_value"


# ============================================================================
# ドメイン用語の用語集
# ============================================================================
"""
概念マップ採点システムのドメイン用語:

antes (ポルトガル語: "before") - 命題の始点/原因ノード
    英語相当: antecedent, prerequisite, cause
    例: 「A causes B」において、Aが'antes'

conq (ポルトガル語: "consequence") - 命題の終点/結果ノード
    英語相当: consequent, result, effect
    例: 「A causes B」において、Bが'conq'

これらの用語は元の研究文献とデータフォーマット仕様から引き継がれています。
"""


# ログメッセージ
LOG_ALGORITHM_REGISTERED = "アルゴリズムが登録されました: {}"
LOG_ALGORITHM_EXECUTION_START = "アルゴリズム実行開始: {}"
LOG_ALGORITHM_EXECUTION_SUCCESS = "アルゴリズム実行成功: {} ({:.2f}秒)"
LOG_ALGORITHM_EXECUTION_FAILURE = "アルゴリズム実行失敗: {} - {}"
LOG_FILES_VALIDATED = "ファイルの検証が完了しました"
LOG_LOADING_DATA = "データを読み込み中: {}"
