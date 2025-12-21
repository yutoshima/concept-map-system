# 概念マップ採点統合システム

McClure、Novak、LEA、data_validation、および独自アルゴリズムを統合した採点システムです。

## 特徴

- **複数のアルゴリズム対応**: McClure、Novak、LEAなど複数の採点方式をサポート
- **並列実行**: 複数のアルゴリズムを同時に実行可能
- **拡張可能**: 独自のアルゴリズムを簡単に追加できる
- **CLI & GUI**: コマンドラインとGUIの両方をサポート
- **柔軟な設定**: 詳細表示、デバッグモードなど豊富なオプション

## ディレクトリ構造

```
concept_map_system/
├── __init__.py              # パッケージ初期化
├── __main__.py              # メインエントリーポイント
├── cli.py                   # CLI インターフェース
├── gui.py                   # GUI インターフェース
├── core/                    # コアモジュール
│   ├── __init__.py
│   ├── base_algorithm.py    # 基底アルゴリズムクラス
│   ├── algorithm_registry.py # アルゴリズムレジストリ
│   ├── executor.py          # 並列実行エンジン
│   ├── constants.py         # 定数定義
│   ├── types.py             # 型定義
│   ├── exceptions.py        # カスタム例外
│   └── logging_config.py    # ログ設定
├── algorithms/              # アルゴリズム実装
│   ├── __init__.py
│   ├── concept_map_core.py  # 基底スコアラークラス
│   ├── mcclure_algorithm.py # McClure方式
│   ├── novak_algorithm.py   # Novak方式
│   ├── lea_algorithm.py     # LEA (Link Evaluation Algorithm)
│   ├── lea_core.py          # LEAコアロジック
│   └── custom_algorithm_template.py # カスタムアルゴリズムテンプレート
├── utils/                   # ユーティリティ
│   ├── __init__.py
│   ├── csv_loader.py        # CSVデータ読み込み
│   ├── formatting.py        # 出力フォーマット
│   ├── proposition_processor.py # 命題処理
│   ├── result_formatter.py  # 結果フォーマット
│   └── validation.py        # データ検証
└── tests/                   # テスト
    ├── __init__.py
    ├── test_algorithm_registry.py
    ├── test_base_algorithm.py
    └── test_formatting.py
```

## インストール

### 依存パッケージ

このシステムはPython標準ライブラリで動作しますが、一部の機能には追加パッケージが必要です：

**コア機能（必須）:**
- Python 3.8以降の標準ライブラリのみ

**オプション:**
- `pandas` - LEAアルゴリズムの一部機能で使用（必須ではありません）

```bash
# オプション: pandasをインストールする場合
pip install pandas
```

## 使用方法

### 1. CLI（コマンドライン）

#### 基本的な使い方

```bash
# 単一のアルゴリズムを実行
python -m concept_map_system cli -a mcclure master.csv student.csv

# 複数のアルゴリズムを逐次実行
python -m concept_map_system cli --algorithms mcclure,novak master.csv student.csv

# 複数のアルゴリズムを並列実行
python -m concept_map_system cli --algorithms mcclure,novak --parallel master.csv student.csv

# すべてのアルゴリズムを並列実行
python -m concept_map_system cli --all --parallel master.csv student.csv

# 詳細表示モード
python -m concept_map_system cli -a mcclure -v master.csv student.csv

# 結果をJSONファイルに保存
python -m concept_map_system cli -a mcclure -o result.json master.csv student.csv
```

#### 利用可能なアルゴリズムの一覧表示

```bash
python -m concept_map_system cli --list
```

#### CLIオプション

- `-a, --algorithm`: 実行するアルゴリズム名
- `--algorithms`: 実行するアルゴリズム名（カンマ区切り）
- `--all`: すべてのアルゴリズムを実行
- `--list`: 利用可能なアルゴリズムの一覧を表示
- `--parallel`: 並列実行モードを使用
- `--workers N`: 並列実行時のワーカー数
- `--use-processes`: スレッドではなくプロセスベースの並列実行を使用
- `-v, --verbose`: 詳細な結果を表示
- `-d, --debug`: デバッグ情報を表示
- `-o, --output`: 結果をJSONファイルに出力

### 2. GUI（グラフィカルインターフェース）

```bash
# GUIを起動
python -m concept_map_system gui
```

GUIでは以下の操作が可能です：

1. ファイル選択（模範解答と生徒の回答）
2. アルゴリズムの選択（複数選択可能）
3. 実行設定（詳細表示、デバッグ、並列実行）
4. 採点実行
5. 結果の表示
6. 結果のJSON保存

### 3. 利用可能なアルゴリズム

#### McClure方式

McClure (1999) の採点基準に基づく採点方式。

- **完全一致 (3点)**: ノード、方向、ラベルがすべて一致
- **向き不一致 (2点)**: ノードとラベルは一致、方向のみ不一致
- **ラベル不一致 (1点)**: ノードは一致、ラベルのみ不一致
- **不一致 (0点)**: 上記のいずれにも該当しない

**評価指標:**
- F値、適合率（Precision）、再現率（Recall）を自動計算

**展開モードオプション (`expansion_mode`):**
- `junction` (デフォルト): Junction方式で限定構造を展開
- `qualifier`: Qualifierリンクを使用して限定を分解
- `none`: 展開しない

```bash
# デフォルト（Junction方式）
python -m concept_map_system cli -a mcclure master.csv student.csv

# Qualifier方式で限定を分解
python -m concept_map_system cli -a mcclure --expansion-mode qualifier master.csv student.csv

# 展開しない
python -m concept_map_system cli -a mcclure --expansion-mode none master.csv student.csv
```

#### Novak方式

Novak (ノバック) の採点基準に基づく採点方式。

- **完全一致 (3点)**: ノード、方向、ラベルがすべて一致
- **不一致 (0点)**: 一致しない、またはConflictリンク
- **限定加点 (+4点/個)**: 多対一、一対多の構造ごとに加点

**評価指標:**
- F値、適合率（Precision）、再現率（Recall）を自動計算

**展開モードオプション (`expansion_mode`):**
- `junction` (デフォルト): Junction方式で限定構造を展開
- `qualifier`: Qualifierリンクを使用して限定を分解
- `none`: 展開しない

**交差リンクオプション (`cross_link_score`):**
- 交差リンク（Conflict）1つあたりの点数を指定（0-4点、デフォルト: 0）
- Conflictリンクに点数を付与する場合に使用

```bash
# デフォルト（Junction方式）
python -m concept_map_system cli -a novak master.csv student.csv

# Qualifier方式で限定を分解
python -m concept_map_system cli -a novak --expansion-mode qualifier master.csv student.csv

# 展開しない
python -m concept_map_system cli -a novak --expansion-mode none master.csv student.csv

# 交差リンク（Conflict）に2点を付与
python -m concept_map_system cli -a novak --cross-link-score 2 master.csv student.csv
```

#### LEA (Link Evaluation Algorithm)

因果関係リンク評価システム。最適マッチングによりF値、再現率、適合率を計算。

- **スコア**: 0-4点で各リンクを評価
- **F値**: 再現率と適合率の調和平均
- **カバレッジ率**: マッチング済みの割合

**オプション:**
- `simple_score_only`: F値などの詳細指標を計算せず、素点のみを計算するモード

```bash
# 通常モード（F値などを計算）
python -m concept_map_system cli -a lea master.csv student.csv

# 素点のみモード
python -m concept_map_system cli -a lea --simple-score-only master.csv student.csv
```

### 4. 展開モードについて

McClureとNovakアルゴリズムでは、限定構造（複数のantesノードを持つ命題）の処理方法を選択できます。

#### Junction方式（デフォルト）

Junctionノード（仮想ノード）を使用して限定構造を展開します。

**例:** `0 1 2 If`（antes: "0 1", conq: "2", type: "If"）
- `0 → t_to_2` (Junction)
- `1 → t_to_2` (Junction)
- `t_from_0_1 → 2` (If)

#### Qualifier方式

Qualifierリンクを使用して限定を分解します。

**例:** `0 1 2 If`（antes: "0 1", conq: "2", type: "If"）
- `0 → 2` (If) - メインリンク
- `0 → 1` (Qualifier) - 限定リンク

**例:** `0 1 2 3 Because`（antes: "0 1 2", conq: "3", type: "Because"）
- `0 → 3` (Because) - メインリンク
- `0 → 1` (Qualifier) - 限定リンク
- `0 → 2` (Qualifier) - 限定リンク

#### 展開なし

限定構造をそのまま扱います。antesに複数のノードが含まれていてもそのまま採点に使用されます。

## カスタムアルゴリズムの追加

独自のアルゴリズムを簡単に追加できます。

### 1. テンプレートをコピー

```bash
cp concept_map_system/algorithms/custom_algorithm_template.py \
   concept_map_system/algorithms/my_algorithm.py
```

### 2. アルゴリズムを実装

```python
from typing import Dict, Any
from ..core import BaseAlgorithm, register_algorithm

@register_algorithm
class MyAlgorithm(BaseAlgorithm):
    def __init__(self):
        super().__init__(
            name="my_algorithm",
            description="My custom scoring algorithm"
        )

    def execute(self, master_file: str, student_file: str, **kwargs) -> Dict[str, Any]:
        # アルゴリズムのロジックを実装
        # ...
        return {
            'method': 'MyAlgorithm',
            'total_score': 100,
            'max_score': 100,
            'percentage': 100.0
        }

    def get_supported_options(self) -> Dict[str, Dict[str, Any]]:
        return {
            'verbose': {
                'type': bool,
                'default': False,
                'help': '詳細な結果を表示'
            }
        }
```

### 3. アルゴリズムを登録

`concept_map_system/algorithms/__init__.py` に追加：

```python
from .my_algorithm import MyAlgorithm
```

### 4. 使用

```bash
python -m concept_map_system cli -a my_algorithm master.csv student.csv
```

## 並列実行の仕組み

システムは2つの実行モードをサポートしています：

### 逐次実行（デフォルト）

アルゴリズムを順番に実行します。

```bash
python -m concept_map_system cli --algorithms mcclure,novak master.csv student.csv
```

### 並列実行

複数のアルゴリズムを同時に実行します。

```bash
python -m concept_map_system cli --algorithms mcclure,novak --parallel master.csv student.csv
```

**オプション:**

- `--workers N`: 並列実行時のワーカー数を指定
- `--use-processes`: スレッドベースではなくプロセスベースの並列実行を使用

## 結果の出力

### コンソール出力

採点結果はコンソールに表示されます。`-v`オプションで詳細な情報を表示できます。

### JSON出力

`-o`オプションで結果をJSONファイルに保存できます。

```bash
python -m concept_map_system cli -a mcclure -o result.json master.csv student.csv
```

**出力例:**

```json
{
  "method": "McClure",
  "total_props": 10,
  "score_counts": {
    "3": 5,
    "2": 2,
    "1": 1,
    "0": 2
  },
  "total_score": 20,
  "max_score": 30,
  "percentage": 66.7
}
```

## トラブルシューティング

### アルゴリズムが見つからない

```bash
# 利用可能なアルゴリズムを確認
python -m concept_map_system cli --list
```

### ファイルが読み込めない

- ファイルパスが正しいか確認してください
- ファイルのエンコーディングがUTF-8（BOM付き可）であることを確認してください
- CSVファイルが必須フィールド（id, antes, conq）を含んでいることを確認してください

### デバッグモード

`-d`オプションでデバッグ情報を表示できます。

```bash
python -m concept_map_system cli -a mcclure -d master.csv student.csv
```

## 技術仕様

### アーキテクチャ

- **基底クラス**: すべてのアルゴリズムは`BaseAlgorithm`を継承
- **レジストリパターン**: アルゴリズムは`AlgorithmRegistry`に自動登録
- **並列実行**: `concurrent.futures`を使用したスレッド/プロセスベースの並列実行
- **拡張性**: デコレータ`@register_algorithm`で簡単にアルゴリズムを追加

### サポートするPythonバージョン

Python 3.8以降

### 依存パッケージ

**必須:**
- Python 3.8以降の標準ライブラリ
- tkinter (GUI用、通常はPythonに同梱)

**オプション:**
- pandas (LEAアルゴリズムの一部機能で使用)

## ライセンス

このプロジェクトは教育目的で作成されています。

## 貢献

バグ報告や機能追加の提案は歓迎します。

## サポート

問題が発生した場合は、以下を確認してください：

1. Pythonバージョン (3.8以降)
2. 依存パッケージのインストール状況
3. CSVファイルのフォーマット

## バージョン履歴

### v1.1.0 (2025)

- **新機能**: McClureとNovakアルゴリズムにF値、適合率、再現率の計算を追加
- **新機能**: LEAに素点のみモード（simple_score_only）を追加
- **改善**: アルゴリズム結果の表示フォーマットを更新
- **変更**: WLEAをLEA (Link Evaluation Algorithm) に名称変更

### v1.0.0 (2025)

- 初回リリース
- McClure、Novak、LEAアルゴリズムをサポート
- CLI & GUIインターフェース
- 並列実行サポート
- カスタムアルゴリズムのサポート
