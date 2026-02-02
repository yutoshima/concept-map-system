# CLIクイックリファレンス

コマンドライン（CLI）で概念マップを採点する際のクイックリファレンス。

---

## 🚀 基本コマンド

### 最もシンプルな使い方

```bash
# LEA法で採点
python3 -m concept_map_system cli -a lea master.csv student.csv

# McClure法で採点
python3 -m concept_map_system cli -a mcclure master.csv student.csv

# Novak法で採点
python3 -m concept_map_system cli -a novak master.csv student.csv
```

### 利用可能なアルゴリズム一覧を表示

```bash
python3 -m concept_map_system cli --list
```

---

## 📊 複数アルゴリズムの実行

### 2つのアルゴリズムで比較

```bash
# McClureとLEAで採点（逐次実行）
python3 -m concept_map_system cli --algorithms mcclure,lea master.csv student.csv

# McClureとLEAで採点（並列実行・高速）
python3 -m concept_map_system cli --algorithms mcclure,lea --parallel master.csv student.csv
```

### すべてのアルゴリズムで採点

```bash
# すべて逐次実行
python3 -m concept_map_system cli --all master.csv student.csv

# すべて並列実行（推奨）
python3 -m concept_map_system cli --all --parallel master.csv student.csv
```

---

## 📁 結果の保存

### JSON形式で保存

```bash
# 結果をJSONファイルに保存
python3 -m concept_map_system cli -a lea -o result.json master.csv student.csv
```

**出力されるJSON例：**
```json
{
  "method": "LEA",
  "raw_score": 7,
  "max_possible_score": 8,
  "score_rate": 0.875,
  "f_value": 0.875,
  "precision": 0.875,
  "recall": 0.875,
  "matched_pairs": 2
}
```

---

## 🔍 詳細表示・デバッグ

### 詳細な結果を表示

```bash
python3 -m concept_map_system cli -a lea -v master.csv student.csv
```

**詳細表示の内容：**
- リンクごとのマッチング詳細
- スコアの内訳
- 未マッチリンクの一覧

### デバッグモード（開発者向け）

```bash
python3 -m concept_map_system cli -a lea -d master.csv student.csv
```

**デバッグ情報：**
- 内部処理の詳細ログ
- データ構造の表示
- エラーの詳細なトレース

---

## ⚙️ アルゴリズム固有のオプション

### McClure法：限定構造の展開モード

```bash
# Junction方式（デフォルト）
python3 -m concept_map_system cli -a mcclure master.csv student.csv

# Qualifier方式
python3 -m concept_map_system cli -a mcclure --expansion-mode qualifier master.csv student.csv

# 展開しない
python3 -m concept_map_system cli -a mcclure --expansion-mode none master.csv student.csv
```

**展開モードの説明：**
- **Junction**: 仮想ノードを使って限定構造を展開（推奨）
- **Qualifier**: Qualifierリンクで限定を分解
- **none**: 展開せずそのまま処理

### Novak法：交差リンクスコア

```bash
# Conflictリンクに2点を付与
python3 -m concept_map_system cli -a novak --cross-link-score 2 master.csv student.csv

# Conflictリンクに0点（デフォルト）
python3 -m concept_map_system cli -a novak --cross-link-score 0 master.csv student.csv
```

### LEA法：素点のみモード

```bash
# F値などの詳細指標を計算せず、素点のみ
python3 -m concept_map_system cli -a lea --simple-score-only master.csv student.csv
```

---

## 🔄 並列実行のオプション

### ワーカー数を指定

```bash
# 4つのワーカーで並列実行
python3 -m concept_map_system cli --all --parallel --workers 4 master.csv student.csv
```

### プロセスベースの並列実行

```bash
# デフォルトはスレッドベース、プロセスベースに変更
python3 -m concept_map_system cli --all --parallel --use-processes master.csv student.csv
```

**使い分け：**
- **スレッドベース**（デフォルト）: 軽量、I/O待ちが多い場合に有効
- **プロセスベース**: CPU負荷が高い場合に有効

---

## 💡 実践的な使用例

### 例1：単一サンプルをMcClure法で採点

```bash
python3 -m concept_map_system cli \
    -a mcclure \
    answers/L-01.csv \
    student_answers/pre/L-01/student_001.csv
```

### 例2：複数アルゴリズムで比較して結果を保存

```bash
python3 -m concept_map_system cli \
    --algorithms mcclure,lea \
    --parallel \
    -o comparison.json \
    answers/L-01.csv \
    student_answers/pre/L-01/student_001.csv
```

### 例3：詳細情報を含めて保存

```bash
python3 -m concept_map_system cli \
    -a lea \
    -v \
    -o detailed_result.json \
    answers/L-01.csv \
    student_answers/pre/L-01/student_001.csv
```

### 例4：複数学習者を一括採点（Bashスクリプト）

```bash
#!/bin/bash
# score_all.sh

MASTER="answers/L-01.csv"
STUDENT_DIR="student_answers/pre/L-01"
OUTPUT_DIR="results"

mkdir -p "$OUTPUT_DIR"

for student_file in "$STUDENT_DIR"/*.csv; do
    student_name=$(basename "$student_file" .csv)
    echo "採点中: $student_name"

    python3 -m concept_map_system cli \
        --algorithms mcclure,lea \
        --parallel \
        -o "$OUTPUT_DIR/${student_name}.json" \
        "$MASTER" \
        "$student_file"
done

echo "すべての採点が完了しました"
```

**実行：**
```bash
chmod +x score_all.sh
./score_all.sh
```

### 例5：研究用の一括採点（Pythonスクリプト）

```python
# batch_scoring.py
import subprocess
from pathlib import Path
import json

def score_sample(master_file, student_file, algorithm):
    """単一サンプルを採点"""
    output_file = "temp_result.json"

    cmd = [
        "python3", "-m", "concept_map_system", "cli",
        "-a", algorithm,
        "-o", output_file,
        str(master_file),
        str(student_file)
    ]

    subprocess.run(cmd, check=True)

    with open(output_file, 'r') as f:
        result = json.load(f)

    Path(output_file).unlink()
    return result

# 使用例
master = Path("answers/L-01.csv")
students = Path("student_answers/pre/L-01").glob("*.csv")

results = []
for student_file in students:
    result = score_sample(master, student_file, "lea")
    results.append({
        "student": student_file.name,
        "score": result["raw_score"],
        "f_value": result["f_value"]
    })

# 結果をまとめて保存
with open("batch_results.json", 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"✅ {len(results)}名の採点が完了しました")
```

---

## 🎮 GUIの起動

```bash
# グラフィカルインターフェースを起動
python3 -m concept_map_system gui
```

**GUIでできること：**
- ファイル選択（ドラッグ&ドロップ対応）
- アルゴリズムの選択（複数選択可）
- 実行設定（並列実行、詳細表示など）
- 結果の表示
- 結果のJSON保存

---

## ❓ ヘルプの表示

### 全般的なヘルプ

```bash
python3 -m concept_map_system cli --help
```

### 簡易ヘルプ

```bash
python3 -m concept_map_system cli -h
```

---

## 📋 全オプション一覧

| オプション | 短縮形 | 説明 | 例 |
|----------|--------|------|-----|
| `--algorithm` | `-a` | 実行するアルゴリズム | `-a lea` |
| `--algorithms` | なし | 複数アルゴリズム（カンマ区切り） | `--algorithms mcclure,lea` |
| `--all` | なし | すべてのアルゴリズムを実行 | `--all` |
| `--list` | なし | 利用可能なアルゴリズム一覧 | `--list` |
| `--parallel` | なし | 並列実行モード | `--parallel` |
| `--workers` | なし | ワーカー数 | `--workers 4` |
| `--use-processes` | なし | プロセスベース並列実行 | `--use-processes` |
| `--verbose` | `-v` | 詳細な結果を表示 | `-v` |
| `--debug` | `-d` | デバッグ情報を表示 | `-d` |
| `--output` | `-o` | JSON出力ファイル | `-o result.json` |
| `--expansion-mode` | なし | 限定構造の展開モード | `--expansion-mode qualifier` |
| `--cross-link-score` | なし | 交差リンクスコア（Novak） | `--cross-link-score 2` |
| `--simple-score-only` | なし | 素点のみモード（LEA） | `--simple-score-only` |

---

## 🔗 関連ドキュメント

- **[README.md](README.md)** - システム概要と基本的な使い方
- **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** - より詳細な使用例
- **[ACADEMIC_OUTPUT.md](ACADEMIC_OUTPUT.md)** - 研究論文での使用方法
- **[README_DEV.md](README_DEV.md)** - 開発者向け情報

---

**更新日:** 2025-02
