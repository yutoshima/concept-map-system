# CLI クイックリファレンス

## 🚀 よく使うコマンド

### McClure方式で採点（推奨）
```bash
python -m concept_map_system cli -a mcclure master.csv student.csv
```

### LEA方式で採点
```bash
python -m concept_map_system cli -a lea master.csv student.csv
```

---

## 📸 論文用の出力

### ASCII表形式（スクリーンショット向け）
```bash
python -m concept_map_system cli -a mcclure --format ascii master.csv student.csv
```

**出力例:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 MCCLURE方式 で採点開始
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────┐
│ McClure方式 採点結果 │
├──────┬───────┤
│  指標  │   値   │
╞══════╪═══════╡
│ 合計得点 │ 20/30 │
│ 正答率  │ 66.7% │
│ F値   │ 0.800 │
│ 適合率  │ 0.875 │
│ 再現率  │ 0.737 │
└──────┴───────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 採点完了 (0.15秒)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📊 複数アルゴリズム比較

### McClureとLEAを比較（表形式）
```bash
python -m concept_map_system cli --algorithms mcclure,lea --format ascii master.csv student.csv
```

**出力例:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 2個のアルゴリズムで採点
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────┐
│                   アルゴリズム比較                    │
├─────────┬───────┬───────┬───────┬───────┬───────┤
│  アルゴリズム │   得点  │  正答率  │   F値  │  適合率  │  再現率  │
╞═════════╪═══════╪═══════╪═══════╪═══════╪═══════╡
│ mcclure │ 20/30 │ 66.7% │ 0.800 │ 0.875 │ 0.737 │
│ lea     │ 22/30 │ 73.3% │ 0.850 │ 0.900 │ 0.805 │
└─────────┴───────┴───────┴───────┴───────┴───────┘
```

### 並列実行で高速化
```bash
python -m concept_map_system cli --algorithms mcclure,lea --parallel master.csv student.csv
```

---

## 📄 ファイル出力

### LaTeX形式で出力（論文埋め込み用）
```bash
python -m concept_map_system cli -a mcclure --format latex --export table.tex master.csv student.csv
```

### Markdown形式で出力（GitHub用）
```bash
python -m concept_map_system cli -a mcclure --format markdown --export results.md master.csv student.csv
```

### CSV形式で出力（Excel分析用）
```bash
python -m concept_map_system cli -a mcclure --format csv --export data.csv master.csv student.csv
```

---

## 🔧 オプション

### 詳細表示
```bash
python -m concept_map_system cli -a mcclure -v master.csv student.csv
```

### デバッグモード
```bash
python -m concept_map_system cli -a mcclure -d master.csv student.csv
```

### JSON出力
```bash
python -m concept_map_system cli -a mcclure -o result.json master.csv student.csv
```

---

## 📋 アルゴリズム一覧

```bash
python -m concept_map_system cli --list
```

**出力:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
利用可能なアルゴリズム
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【推奨アルゴリズム】

● MCCLURE
  McClure (1999) 概念マップ採点方式

● LEA
  LEA法: 因果関係リンク評価システム

【その他のアルゴリズム】

● novak
  Novak方式
```

---

## 🎯 アルゴリズム固有のオプション

### McClure - 展開モード
```bash
# Junction方式（デフォルト）
python -m concept_map_system cli -a mcclure --expansion-mode junction master.csv student.csv

# Qualifier方式
python -m concept_map_system cli -a mcclure --expansion-mode qualifier master.csv student.csv

# 展開しない
python -m concept_map_system cli -a mcclure --expansion-mode none master.csv student.csv
```

### LEA - 素点のみモード
```bash
python -m concept_map_system cli -a lea --simple-score-only master.csv student.csv
```

### Novak - 交差リンクスコア
```bash
python -m concept_map_system cli -a novak --cross-link-score 2 master.csv student.csv
```

---

## 💡 実践例

### 1. 論文用の図表作成
```bash
# ASCII表形式でスクリーンショット
python -m concept_map_system cli \
  --algorithms mcclure,lea \
  --format ascii \
  master.csv student.csv

# または LaTeX形式で直接埋め込み
python -m concept_map_system cli \
  --algorithms mcclure,lea \
  --format latex \
  --export comparison_table.tex \
  master.csv student.csv
```

### 2. 複数の生徒を一括評価
```bash
#!/bin/bash
for student in data/students/*.csv; do
    name=$(basename "$student" .csv)
    python -m concept_map_system cli \
      -a mcclure \
      --format ascii \
      master.csv "$student" > "results/${name}.txt"
done
```

### 3. Excel分析用データ作成
```bash
python -m concept_map_system cli \
  --algorithms mcclure,lea \
  --format csv \
  --export analysis.csv \
  master.csv student.csv
```

---

## ❓ ヘルプ

### 全体のヘルプ
```bash
python -m concept_map_system cli --help
```

### クイックヘルプ
```bash
python -m concept_map_system cli -h
```

---

## 🔗 関連ドキュメント

- [README.md](README.md) - 概要と基本的な使い方
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - 詳細な使用例
- [ACADEMIC_OUTPUT.md](ACADEMIC_OUTPUT.md) - 論文品質出力の詳細
- [README_DEV.md](README_DEV.md) - 開発者向け情報
