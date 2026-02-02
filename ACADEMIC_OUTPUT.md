# 研究論文での使用ガイド

概念マップ採点システムを学術研究で使用する際のガイド。データ収集、分析、論文執筆のワークフローを解説します。

---

## 🎯 研究での典型的なワークフロー

```
1. データ収集（CSV形式）
   ↓
2. 一括採点（このシステム）
   ↓
3. 結果の集計・分析（Python/Excel）
   ↓
4. 論文執筆（統計値、図表作成）
```

---

## 📊 ステップ1：データ準備

### ディレクトリ構成

```
research_project/
├── data/
│   ├── answers/              # 模範解答
│   │   ├── L-01.csv
│   │   ├── L-02.csv
│   │   └── ...
│   └── student_answers/      # 学習者データ
│       ├── pre/              # 事前テスト
│       │   ├── L-01/
│       │   │   ├── student_001.csv
│       │   │   ├── student_002.csv
│       │   │   └── ...
│       │   └── ...
│       ├── post/             # 事後テスト
│       └── ...
├── results/                  # 採点結果（JSON）
├── analysis/                 # 分析結果
└── scripts/
    ├── run_scoring.py        # 一括採点スクリプト
    └── analyze_results.py    # 分析スクリプト
```

### CSVデータ形式

**模範解答の例（L-01.csv）：**
```csv
id,text,antes,conq,type
0,rule-0,0 1,2,If
1,rule-1,2,3,Then
```

**学習者解答も同じ形式。**

---

## 🔬 ステップ2：一括採点

### 方法1：シェルスクリプトで一括採点

```bash
#!/bin/bash
# score_all.sh - 全サンプルを採点

MASTER_DIR="data/answers"
STUDENT_DIR="data/student_answers/pre"
OUTPUT_DIR="results/pre"
ALGORITHMS="mcclure,lea"  # 使用するアルゴリズム

mkdir -p "$OUTPUT_DIR"

# 各タスク（L-01〜L-05）をループ
for task in L-01 L-02 L-03 L-04 L-05; do
    echo "タスク $task を処理中..."
    master_file="$MASTER_DIR/$task.csv"
    task_output_dir="$OUTPUT_DIR/$task"
    mkdir -p "$task_output_dir"

    # 各学習者をループ
    for student_file in "$STUDENT_DIR/$task"/*.csv; do
        student_name=$(basename "$student_file" .csv)
        output_file="$task_output_dir/${student_name}.json"

        echo "  採点中: $student_name"
        python3 -m concept_map_system cli \
            --algorithms "$ALGORITHMS" \
            --parallel \
            -o "$output_file" \
            "$master_file" \
            "$student_file"
    done
done

echo "✅ すべての採点が完了しました"
```

**実行：**
```bash
chmod +x score_all.sh
./score_all.sh
```

### 方法2：Pythonスクリプトで一括採点

```python
#!/usr/bin/env python3
"""
run_scoring.py - 全サンプルを一括採点
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

# 設定
BASE_DIR = Path(__file__).parent
MASTER_DIR = BASE_DIR / "data/answers"
STUDENT_BASE_DIR = BASE_DIR / "data/student_answers"
OUTPUT_DIR = BASE_DIR / "results"
ALGORITHMS = ["mcclure", "lea"]

# タスクとフェーズの定義
TASKS = ["L-01", "L-02", "L-03", "L-04", "L-05"]
PHASES = ["pre", "post", "delay"]

def score_sample(master_file, student_file, algorithms):
    """単一サンプルを採点してJSON結果を返す"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_file = f.name

    cmd = [
        "python3", "-m", "concept_map_system", "cli",
        "--algorithms", ",".join(algorithms),
        "--parallel",
        "-o", output_file,
        str(master_file),
        str(student_file)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and Path(output_file).exists():
            with open(output_file, 'r') as f:
                data = json.load(f)
            Path(output_file).unlink()
            return data
        else:
            return {"error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "Timeout"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if Path(output_file).exists():
            Path(output_file).unlink()

def main():
    print("=" * 60)
    print("概念マップ一括採点システム")
    print("=" * 60)
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    total_samples = 0
    success_count = 0
    error_count = 0

    # 各フェーズを処理
    for phase in PHASES:
        phase_dir = STUDENT_BASE_DIR / phase
        if not phase_dir.exists():
            print(f"⚠️  スキップ: {phase} (ディレクトリが存在しません)")
            continue

        print(f"\n📂 フェーズ: {phase}")
        phase_output_dir = OUTPUT_DIR / phase
        phase_output_dir.mkdir(parents=True, exist_ok=True)

        # 各タスクを処理
        for task in TASKS:
            task_dir = phase_dir / task
            master_file = MASTER_DIR / f"{task}.csv"

            if not task_dir.exists() or not master_file.exists():
                continue

            print(f"  タスク: {task}")
            task_output_dir = phase_output_dir / task
            task_output_dir.mkdir(parents=True, exist_ok=True)

            # 各学習者を処理
            for student_file in sorted(task_dir.glob("*.csv")):
                total_samples += 1
                student_name = student_file.stem
                output_file = task_output_dir / f"{student_name}.json"

                # 採点実行
                result = score_sample(master_file, student_file, ALGORITHMS)

                # 結果を保存
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "phase": phase,
                        "task": task,
                        "student": student_name,
                        "master_file": str(master_file),
                        "student_file": str(student_file),
                        "results": result,
                        "timestamp": datetime.now().isoformat()
                    }, f, ensure_ascii=False, indent=2)

                if "error" not in result:
                    success_count += 1
                    print(f"    ✅ {student_name}")
                else:
                    error_count += 1
                    print(f"    ❌ {student_name}: {result['error']}")

    # サマリー表示
    print("\n" + "=" * 60)
    print("採点完了")
    print("=" * 60)
    print(f"総サンプル数: {total_samples}")
    print(f"成功: {success_count}")
    print(f"失敗: {error_count}")
    print(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
```

**実行：**
```bash
python3 run_scoring.py
```

**実行時間の目安：**
- McClure法: 約0.16秒/サンプル
- LEA法: 約0.41秒/サンプル
- 225サンプル（2アルゴリズム）: 約2分

---

## 📈 ステップ3：結果の分析

### 採点結果の集計スクリプト

```python
#!/usr/bin/env python3
"""
analyze_results.py - 採点結果を集計して統計を出力
"""

import json
import pandas as pd
from pathlib import Path

# 結果ディレクトリ
RESULTS_DIR = Path("results")
OUTPUT_DIR = Path("analysis")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_all_results():
    """全結果JSONを読み込み"""
    results = []
    for json_file in RESULTS_DIR.rglob("*.json"):
        with open(json_file, 'r') as f:
            data = json.load(f)
            results.append(data)
    return results

def extract_scores(results):
    """スコアデータを抽出してDataFrameに変換"""
    rows = []
    for result in results:
        phase = result.get("phase", "unknown")
        task = result.get("task", "unknown")
        student = result.get("student", "unknown")

        for algo_name, algo_result in result.get("results", {}).items():
            if "error" in algo_result:
                continue

            row = {
                "phase": phase,
                "task": task,
                "student": student,
                "algorithm": algo_name,
                "f_value": algo_result.get("f_value", None),
                "precision": algo_result.get("precision", None),
                "recall": algo_result.get("recall", None),
            }

            # アルゴリズム固有のスコア
            if algo_name == "mcclure":
                row["score"] = algo_result.get("total_score", 0)
                row["max_score"] = algo_result.get("max_score", 0)
                row["percentage"] = algo_result.get("percentage", 0)
            elif algo_name == "lea":
                row["score"] = algo_result.get("raw_score", 0)
                row["max_score"] = algo_result.get("max_possible_score", 0)
                row["percentage"] = algo_result.get("score_rate", 0) * 100

            rows.append(row)

    return pd.DataFrame(rows)

def main():
    print("📊 結果分析を開始します...")

    # 全結果を読み込み
    results = load_all_results()
    print(f"✅ {len(results)}個のJSONファイルを読み込みました")

    # DataFrameに変換
    df = extract_scores(results)
    print(f"✅ {len(df)}行のデータを抽出しました")

    # 統計計算
    print("\n" + "=" * 60)
    print("📈 アルゴリズム別統計")
    print("=" * 60)

    for algo in df['algorithm'].unique():
        algo_df = df[df['algorithm'] == algo]
        print(f"\n{algo.upper()}:")
        print(f"  サンプル数: {len(algo_df)}")
        print(f"  F値 - 平均: {algo_df['f_value'].mean():.3f}, "
              f"標準偏差: {algo_df['f_value'].std():.3f}")
        print(f"  適合率 - 平均: {algo_df['precision'].mean():.3f}")
        print(f"  再現率 - 平均: {algo_df['recall'].mean():.3f}")

    # CSV出力
    output_csv = OUTPUT_DIR / "all_scores.csv"
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n✅ 全スコアを保存: {output_csv}")

    # ピボットテーブル（フェーズ×アルゴリズム）
    pivot = df.pivot_table(
        values='f_value',
        index='phase',
        columns='algorithm',
        aggfunc='mean'
    )
    output_pivot = OUTPUT_DIR / "phase_algorithm_fvalue.csv"
    pivot.to_csv(output_pivot, encoding='utf-8-sig')
    print(f"✅ ピボットテーブルを保存: {output_pivot}")

    # タスク別統計
    task_stats = df.groupby(['task', 'algorithm']).agg({
        'f_value': ['mean', 'std', 'count']
    }).round(3)
    output_task = OUTPUT_DIR / "task_statistics.csv"
    task_stats.to_csv(output_task, encoding='utf-8-sig')
    print(f"✅ タスク別統計を保存: {output_task}")

    print("\n✅ 分析完了！")

if __name__ == "__main__":
    main()
```

**実行：**
```bash
python3 analyze_results.py
```

**出力ファイル：**
- `analysis/all_scores.csv` - 全スコア一覧
- `analysis/phase_algorithm_fvalue.csv` - フェーズ×アルゴリズムのF値平均
- `analysis/task_statistics.csv` - タスク別統計

---

## 📝 ステップ4：論文執筆

### 記述統計の報告

```latex
\section{実験結果}

\subsection{採点アルゴリズムの比較}

225サンプルに対して、McClure法とLEA法の2つのアルゴリズムで採点を行った。
各アルゴリズムのF値、適合率、再現率の平均値と標準偏差を表\ref{tab:algo_comparison}に示す。

\begin{table}[htbp]
  \centering
  \caption{採点アルゴリズムの評価指標}
  \label{tab:algo_comparison}
  \begin{tabular}{lccc}
    \hline
    アルゴリズム & F値 & 適合率 & 再現率 \\
    \hline
    McClure & $0.756 \pm 0.123$ & $0.812 \pm 0.145$ & $0.721 \pm 0.132$ \\
    LEA & $0.821 \pm 0.098$ & $0.865 \pm 0.112$ & $0.793 \pm 0.109$ \\
    \hline
  \end{tabular}
\end{table}

LEA法はMcClure法よりも高いF値を示し（$t(224) = 5.34, p < .001$）、
より正確な採点が可能であることが示唆された。
```

### 図の作成（Python + Matplotlib）

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# データ読み込み
df = pd.read_csv("analysis/all_scores.csv")

# フェーズごとのF値の箱ひげ図
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='phase', y='f_value', hue='algorithm')
plt.title('F値の分布（フェーズ×アルゴリズム）')
plt.xlabel('実験フェーズ')
plt.ylabel('F値')
plt.legend(title='アルゴリズム')
plt.tight_layout()
plt.savefig('analysis/fvalue_by_phase.png', dpi=300)
plt.close()

# アルゴリズム間の相関（散布図）
mcclure_df = df[df['algorithm'] == 'mcclure'][['student', 'task', 'f_value']]
lea_df = df[df['algorithm'] == 'lea'][['student', 'task', 'f_value']]
merged = pd.merge(mcclure_df, lea_df, on=['student', 'task'],
                  suffixes=('_mcclure', '_lea'))

plt.figure(figsize=(8, 8))
plt.scatter(merged['f_value_mcclure'], merged['f_value_lea'], alpha=0.5)
plt.plot([0, 1], [0, 1], 'r--', label='y=x')
plt.xlabel('McClure法のF値')
plt.ylabel('LEA法のF値')
plt.title('McClure法とLEA法のF値の相関')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('analysis/mcclure_lea_correlation.png', dpi=300)
plt.close()

print("✅ 図を保存しました")
```

---

## 🔬 再現性の確保

### 実験環境の記録

```python
import sys
import subprocess

def record_environment():
    """実験環境を記録"""
    env_info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "concept_map_system_version": "1.1.0",
        "execution_date": datetime.now().isoformat(),
    }

    with open("analysis/environment.json", 'w') as f:
        json.dump(env_info, f, indent=2)

    print("✅ 実験環境を記録しました")
```

### 論文での記載例

```latex
\subsection{実験環境}

概念マップの採点には、概念マップ採点統合システム（バージョン1.1.0）を使用した。
Python 3.10環境で、McClure法\cite{mcclure1999}とLEA（Link Evaluation Algorithm）の
2つのアルゴリズムを用いて評価を行った。各サンプルの処理時間は、McClure法で平均0.16秒、
LEA法で平均0.41秒であった。
```

---

## 📊 統計分析の例

### 対応のあるt検定（Python）

```python
from scipy import stats

# McClure法とLEA法のF値を比較
mcclure_scores = df[df['algorithm'] == 'mcclure']['f_value'].values
lea_scores = df[df['algorithm'] == 'lea']['f_value'].values

# 対応のあるt検定
t_stat, p_value = stats.ttest_rel(mcclure_scores, lea_scores)

print(f"t値: {t_stat:.3f}")
print(f"p値: {p_value:.4f}")
print(f"効果量（Cohen's d）: {(lea_scores.mean() - mcclure_scores.mean()) / lea_scores.std():.3f}")
```

### 相関分析

```python
from scipy.stats import pearsonr, spearmanr

# McClure法とLEA法の相関
r, p = pearsonr(merged['f_value_mcclure'], merged['f_value_lea'])
print(f"Pearson相関係数: r={r:.3f}, p={p:.4f}")

rho, p = spearmanr(merged['f_value_mcclure'], merged['f_value_lea'])
print(f"Spearman相関係数: ρ={rho:.3f}, p={p:.4f}")
```

---

## 📖 引用方法

### BibTeX

```bibtex
@software{concept_map_system,
  title={概念マップ採点統合システム},
  version={1.1.0},
  year={2025},
  note={McClure法、Novak法、LEA法を実装した概念マップ自動採点ツール},
  url={https://github.com/yourusername/concept_map_system}
}
```

### 本文での言及

```
概念マップの採点には、概念マップ採点統合システム（バージョン1.1.0）を使用した。
このシステムは、McClure (1999) の基準に基づくMcClure法と、
最適マッチングによるLEA（Link Evaluation Algorithm）法を実装しており、
F値、適合率、再現率を自動計算する。
```

---

## ✅ チェックリスト

論文投稿前に確認すべき事項：

- [ ] 全サンプルが正常に採点されている（エラー0件）
- [ ] 実行環境（Pythonバージョン、OSなど）を記録している
- [ ] 使用したアルゴリズムとパラメータを明記している
- [ ] 統計分析の手法を明記している（t検定、相関分析など）
- [ ] 図表に適切なキャプションと参照番号がついている
- [ ] 生データ（JSON）とスクリプトを保存している
- [ ] 再現可能性のため、スクリプトとREADMEを用意している

---

## 🔗 関連ドキュメント

- **[README.md](README.md)** - システム概要
- **[CLI_QUICK_REFERENCE.md](CLI_QUICK_REFERENCE.md)** - CLIコマンドリファレンス
- **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** - 詳細な使用例

---

**更新日:** 2025-02
