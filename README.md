# 概念マップ採点システム

概念マップ（CSV形式）を自動採点するPythonツール。McClure法、Novak法、LEA法など複数のアルゴリズムに対応。

## クイックスタート（3ステップ）

```bash
# 1. Pythonがインストールされていることを確認（3.8以降）
python3 --version

# 2. 単一サンプルを採点（LEA法）
python3 -m concept_map_system cli -a lea master.csv student.csv

# 3. 結果をJSONに保存
python3 -m concept_map_system cli -a lea -o result.json master.csv student.csv
```

**動作要件:** Python 3.8以降（標準ライブラリのみ、追加インストール不要）

---

## 📋 CSVフォーマット

**入力ファイルの例：**
```csv
id,text,antes,conq,type
0,rule-0,0 1,2,If
1,rule-1,2,3,Then
```

- `id`: 命題の識別子
- `antes`: 前件（複数可、スペース区切り）
- `conq`: 後件
- `type`: リンク種別（If, Then, Because等）

---

## 🎯 基本的な使い方

### 1つのアルゴリズムで採点

```bash
# McClure法で採点
python3 -m concept_map_system cli -a mcclure master.csv student.csv

# LEA法で採点
python3 -m concept_map_system cli -a lea master.csv student.csv
```

**出力例：**
```
スコア: 7/8 (87.5%)
F値: 0.875
再現率: 0.875
適合率: 0.875
✅ 採点完了 (0.00秒)
```

### 複数のアルゴリズムで比較

```bash
# McClureとLEAの両方で採点
python3 -m concept_map_system cli --algorithms mcclure,lea master.csv student.csv

# すべてのアルゴリズムで採点
python3 -m concept_map_system cli --all master.csv student.csv
```

### 結果をJSONファイルに保存

```bash
python3 -m concept_map_system cli -a lea -o result.json master.csv student.csv
```

**出力されるJSON例：**
```json
{
  "method": "LEA",
  "raw_score": 7,
  "max_possible_score": 8,
  "f_value": 0.875,
  "precision": 0.875,
  "recall": 0.875
}
```

---

## 🔬 採点アルゴリズム

### McClure法
McClure (1999) の基準に基づく採点。

**スコア基準：**
- **3点**: 完全一致（ノード、方向、ラベルすべて一致）
- **2点**: 向き不一致
- **1点**: ラベル不一致
- **0点**: 不一致

**出力指標:** F値、適合率、再現率

### Novak法
Novak の基準に基づく採点。限定構造に加点。

**スコア基準：**
- **3点**: 完全一致
- **0点**: 不一致
- **+4点**: 限定構造（多対一、一対多）ごと

**出力指標:** F値、適合率、再現率

### LEA法（Link Evaluation Algorithm）
最適マッチングによる因果関係リンク評価。

**スコア基準（0-4点）：**
- **4点**: 完全一致（位置とタイプ）
- **3点**: 位置一致、タイプ不一致または方向逆
- **2点**: 部分一致、タイプ一致
- **1点**: 部分一致、タイプ不一致
- **0点**: 一致なし

**出力指標:** F値、適合率、再現率、カバレッジ率

---

## 💻 よく使うコマンド

```bash
# 利用可能なアルゴリズム一覧を表示
python3 -m concept_map_system cli --list

# 詳細な結果を表示
python3 -m concept_map_system cli -a lea -v master.csv student.csv

# デバッグモード（開発者向け）
python3 -m concept_map_system cli -a lea -d master.csv student.csv

# GUIを起動
python3 -m concept_map_system gui
```

---

## 📁 ディレクトリ構成

```
concept_map_system/
├── concept_map_system/          # メインパッケージ
│   ├── algorithms/              # 採点アルゴリズム
│   │   ├── mcclure_algorithm.py # McClure法
│   │   ├── novak_algorithm.py   # Novak法
│   │   ├── lea_algorithm.py     # LEA法
│   │   └── lea_core.py          # LEAコアロジック
│   ├── core/                    # コアモジュール
│   ├── utils/                   # ユーティリティ
│   └── tests/                   # テスト
├── requirements.txt             # 依存ライブラリ
└── README.md                    # このファイル
```

---

## 🔧 高度な使い方

### 限定構造の展開モード

McClure法とNovak法では、複数の前件を持つ命題の処理方法を選択できます。

```bash
# Junction方式（デフォルト）
python3 -m concept_map_system cli -a mcclure master.csv student.csv

# Qualifier方式
python3 -m concept_map_system cli -a mcclure --expansion-mode qualifier master.csv student.csv

# 展開しない
python3 -m concept_map_system cli -a mcclure --expansion-mode none master.csv student.csv
```

### 並列実行

複数のアルゴリズムを同時に実行して時間を短縮。

```bash
# 並列実行（推奨）
python3 -m concept_map_system cli --algorithms mcclure,lea --parallel master.csv student.csv

# ワーカー数を指定
python3 -m concept_map_system cli --all --parallel --workers 4 master.csv student.csv
```

---

## 📊 研究での使用例

225サンプルを一括採点する場合：

```python
# run_scoring.py
import subprocess
from pathlib import Path

def score_sample(master_file, student_file, algorithm):
    cmd = [
        "python3", "-m", "concept_map_system", "cli",
        "-a", algorithm,
        "-o", "output.json",
        str(master_file),
        str(student_file)
    ]
    subprocess.run(cmd)

# 全サンプルをループ処理
for student_file in Path("student_answers").glob("*.csv"):
    score_sample("master.csv", student_file, "lea")
```

**実行時間（実測値）:**
- McClure法: 約0.16秒/サンプル
- LEA法: 約0.41秒/サンプル
- 225サンプル: 約2分（逐次実行）

---

## 🆘 トラブルシューティング

### エラー: `ModuleNotFoundError`
```bash
# concept_map_systemディレクトリから実行していることを確認
cd /path/to/concept_map_system
python3 -m concept_map_system cli --list
```

### エラー: `CSVLoadError`
- ファイルパスが正しいか確認
- CSVがUTF-8エンコーディングか確認
- 必須フィールド（id, antes, conq）が含まれているか確認

### デバッグモードで詳細を確認
```bash
python3 -m concept_map_system cli -a lea -d master.csv student.csv
```

---

## 📚 詳細ドキュメント

- **[CLI_QUICK_REFERENCE.md](CLI_QUICK_REFERENCE.md)** - コマンドラインリファレンス
- **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** - 詳細な使用例
- **[ACADEMIC_OUTPUT.md](ACADEMIC_OUTPUT.md)** - 研究論文での使用方法
- **[README_DEV.md](README_DEV.md)** - 開発者向け情報
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - カスタムアルゴリズムの追加方法

---

## 🎓 引用

このシステムを研究で使用する場合：

```bibtex
@software{concept_map_system,
  title={概念マップ採点統合システム},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/concept_map_system}
}
```

---

## 📄 ライセンス

教育・研究目的で自由に使用できます。

---

## 🤝 サポート

問題が発生した場合：
1. デバッグモード（`-d`）で詳細を確認
2. Pythonバージョンを確認（`python3 --version`）
3. CSVファイルのフォーマットを確認

---

**バージョン:** 1.1.0 | **最終更新:** 2025-02
