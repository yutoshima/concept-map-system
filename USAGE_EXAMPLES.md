# 概念マップ採点統合システム - 使用例

このドキュメントでは、統合システムの具体的な使用例を紹介します。

## 目次

1. [基本的な使い方](#基本的な使い方)
2. [CLIの使用例](#cliの使用例)
3. [GUIの使用例](#guiの使用例)
4. [並列実行の使用例](#並列実行の使用例)
5. [カスタムアルゴリズムの実装例](#カスタムアルゴリズムの実装例)

---

## 基本的な使い方

### 利用可能なアルゴリズムの確認

まず、システムに登録されているアルゴリズムを確認します。

```bash
python -m concept_map_system cli --list
```

**出力例:**
```
利用可能なアルゴリズム:
============================================================

mcclure:
  説明: McClure (1999) 概念マップ採点方式。完全一致、向き不一致、ラベル不一致を判定。
  オプション:
    --verbose: 詳細な採点結果を表示 (デフォルト: False)
    --debug: デバッグ情報を表示 (デフォルト: False)

novak:
  説明: Novak (ノバック) 概念マップ採点方式。完全一致のみ採点し、限定構造に加点。
  オプション:
    --verbose: 詳細な採点結果を表示 (デフォルト: False)
    --debug: デバッグ情報を表示 (デフォルト: False)

============================================================
```

---

## CLIの使用例

### 例1: 単一のアルゴリズムで採点

McClure方式で採点を実行します。

```bash
python -m concept_map_system cli \
  -a mcclure \
  path/to/master.csv \
  path/to/student.csv
```

**出力例:**
```
mcclure で採点を実行中...

✓ 採点完了 (0.15秒)
============================================================
【McClure方式 採点結果】
============================================================

総命題数: 10
✓ 完全一致 (3点): 5
↔ 向き不一致 (2点): 2
≠ ラベル不一致 (1点): 1
✗ 不一致 (0点): 2

----------------------------------------
合計得点: 20/30 (66.7%)
----------------------------------------
```

### 例2: 詳細表示モード

`-v`オプションで詳細な結果を表示します。

```bash
python -m concept_map_system cli \
  -a mcclure \
  -v \
  master.csv \
  student.csv
```

### 例3: 結果をJSONファイルに保存

`-o`オプションで結果をJSON形式で保存します。

```bash
python -m concept_map_system cli \
  -a mcclure \
  -o result.json \
  master.csv \
  student.csv
```

**生成されるJSONファイル (result.json):**
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

### 例4: 複数のアルゴリズムを逐次実行

McClureとNovakの両方で採点します。

```bash
python -m concept_map_system cli \
  --algorithms mcclure,novak \
  master.csv \
  student.csv
```

**出力例:**
```
2個のアルゴリズムを実行中...
逐次実行モード
  → mcclure: 完了
  → novak: 完了

============================================================
実行結果サマリー
============================================================

✓ mcclure: 成功 (0.15秒)
============================================================
【McClure方式 採点結果】
[...]

✓ novak: 成功 (0.12秒)
============================================================
【Novak方式 採点結果】
[...]

成功: 2/2
```

---

## 並列実行の使用例

### 例5: 並列実行で高速化

`--parallel`オプションで複数のアルゴリズムを同時に実行します。

```bash
python -m concept_map_system cli \
  --algorithms mcclure,novak \
  --parallel \
  master.csv \
  student.csv
```

**利点:**
- 複数のアルゴリズムを同時に実行することで、処理時間を短縮
- マルチコアCPUを効率的に利用

### 例6: ワーカー数を指定

`--workers`オプションで並列実行時のワーカー数を指定します。

```bash
python -m concept_map_system cli \
  --algorithms mcclure,novak,wlea \
  --parallel \
  --workers 4 \
  master.csv \
  student.csv
```

### 例7: すべてのアルゴリズムを並列実行

`--all`オプションですべてのアルゴリズムを並列実行します。

```bash
python -m concept_map_system cli \
  --all \
  --parallel \
  master.csv \
  student.csv
```

---

## GUIの使用例

### 起動方法

```bash
python -m concept_map_system gui
```

### GUI操作の流れ

1. **ファイル選択**
   - 「参照...」ボタンをクリックして模範解答CSVを選択
   - 「参照...」ボタンをクリックして生徒の回答CSVを選択

2. **アルゴリズム選択**
   - 実行したいアルゴリズムにチェックを入れる
   - 「すべて選択」ボタンですべてのアルゴリズムを選択
   - 「選択解除」ボタンですべての選択を解除

3. **実行設定**
   - 「詳細な結果を表示」: 詳細な採点情報を表示
   - 「デバッグ情報を表示」: デバッグ情報を表示
   - 「並列実行」: 複数のアルゴリズムを並列実行

4. **採点実行**
   - 「採点実行」ボタンをクリック
   - 結果が画面に表示される

5. **結果の保存**
   - 「結果をJSON保存」ボタンで結果をJSON形式で保存

---

## カスタムアルゴリズムの実装例

### 例: 簡易採点アルゴリズム

独自の採点アルゴリズムを実装します。

```python
# concept_map_system/algorithms/simple_algorithm.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Any
import csv
from ..core import BaseAlgorithm, register_algorithm


@register_algorithm
class SimpleAlgorithm(BaseAlgorithm):
    """簡易採点アルゴリズム - 命題数をカウントするだけ"""

    def __init__(self):
        super().__init__(
            name="simple",
            description="簡易採点アルゴリズム。生徒の命題数をカウントします。"
        )

    def execute(self, master_file: str, student_file: str, **kwargs) -> Dict[str, Any]:
        # ファイルの検証
        self.validate_files(master_file, student_file)

        # CSVファイルを読み込み
        with open(master_file, 'r', encoding='utf-8-sig') as f:
            master_rows = list(csv.DictReader(f))

        with open(student_file, 'r', encoding='utf-8-sig') as f:
            student_rows = list(csv.DictReader(f))

        # 命題数をカウント
        master_count = len(master_rows)
        student_count = len(student_rows)

        # スコアを計算（模範解答に対する生徒の回答の割合）
        percentage = (student_count / master_count * 100) if master_count > 0 else 0

        return {
            'method': 'Simple',
            'master_proposition_count': master_count,
            'student_proposition_count': student_count,
            'coverage_percentage': percentage
        }

    def get_supported_options(self) -> Dict[str, Dict[str, Any]]:
        return {
            'verbose': {
                'type': bool,
                'default': False,
                'help': '詳細な結果を表示'
            }
        }

    def format_results(self, results: Dict[str, Any]) -> str:
        output = []
        output.append("=" * 60)
        output.append("【簡易採点 結果】")
        output.append("=" * 60)
        output.append("")
        output.append(f"模範解答の命題数: {results.get('master_proposition_count', 0)}")
        output.append(f"生徒の回答の命題数: {results.get('student_proposition_count', 0)}")
        output.append(f"カバレッジ: {results.get('coverage_percentage', 0):.1f}%")
        return "\n".join(output)
```

### アルゴリズムを登録

```python
# concept_map_system/algorithms/__init__.py に追加

from .simple_algorithm import SimpleAlgorithm
```

### 使用方法

```bash
python -m concept_map_system cli -a simple master.csv student.csv
```

---

## デバッグとトラブルシューティング

### デバッグモード

`-d`オプションでデバッグ情報を表示します。

```bash
python -m concept_map_system cli \
  -a mcclure \
  -d \
  master.csv \
  student.csv
```

**デバッグ出力例:**
```
模範解答: 10行
生徒の回答: 8行
展開後の模範命題: 12個
展開後の生徒命題: 10個
```

### エラーハンドリング

ファイルが見つからない場合:
```bash
python -m concept_map_system cli -a mcclure nonexistent.csv student.csv
```

**エラー出力:**
```
✗ エラー: 模範解答ファイルが見つかりません: nonexistent.csv
```

---

## まとめ

この統合システムは以下の機能を提供します：

- **複数のアルゴリズム**: McClure、Novak、WLEAなど
- **並列実行**: 高速な採点処理
- **CLI & GUI**: 2つのインターフェース
- **拡張性**: カスタムアルゴリズムの追加が容易
- **柔軟な出力**: コンソール表示とJSON出力

さらに詳しい情報は[README.md](README.md)を参照してください。
