# 開発者向けREADME

このドキュメントは、概念マップ採点統合システムの開発者向けの情報を提供します。

## モダンな開発環境

このプロジェクトは、最新のPython開発ツールを使用しています。

### 使用しているツール

| ツール | 説明 | バージョン |
|--------|------|-----------|
| **Ruff** | 高速なリンター＆フォーマッター（Rust製） | >=0.1.0 |
| **MyPy** | 静的型チェッカー | >=1.0.0 |
| **Pytest** | テストフレームワーク | >=7.0.0 |
| **Pre-commit** | Gitフック管理 | >=3.0.0 |
| **Bandit** | セキュリティチェッカー | >=1.7.0 |

### クイックスタート

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/concept-map-system.git
cd concept-map-system

# 開発環境をセットアップ
make dev

# 利用可能なコマンドを確認
make help
```

## プロジェクト構成

```
concept_map_system/
├── .pre-commit-config.yaml  # Pre-commit設定
├── .gitignore               # Git無視設定
├── pyproject.toml           # プロジェクト設定（統一）
├── Makefile                 # タスクランナー
├── requirements.txt         # 本番依存関係
├── requirements-dev.txt     # 開発依存関係
├── README.md                # ユーザー向けREADME
├── README_DEV.md            # 開発者向けREADME
├── CONTRIBUTING.md          # 開発ガイド
├── USAGE_EXAMPLES.md        # 使用例
├── __init__.py              # パッケージ初期化
├── __main__.py              # メインエントリーポイント
├── cli.py                   # CLIインターフェース
├── gui.py                   # GUIインターフェース
├── core/                    # コアモジュール
│   ├── __init__.py
│   ├── base_algorithm.py
│   ├── algorithm_registry.py
│   ├── executor.py
│   ├── constants.py
│   ├── types.py
│   ├── exceptions.py
│   └── logging_config.py
├── algorithms/              # アルゴリズム実装
│   ├── __init__.py
│   ├── concept_map_core.py
│   ├── mcclure_algorithm.py
│   ├── novak_algorithm.py
│   ├── lea_algorithm.py
│   ├── lea_core.py
│   └── custom_algorithm_template.py
├── utils/                   # ユーティリティ
│   ├── __init__.py
│   ├── csv_loader.py
│   ├── formatting.py
│   ├── proposition_processor.py
│   ├── result_formatter.py
│   └── validation.py
└── tests/                   # テスト
    ├── __init__.py
    ├── test_algorithm_registry.py
    ├── test_base_algorithm.py
    └── test_formatting.py
```

## 開発ワークフロー

### 1. 機能開発

```bash
# ブランチを作成
git checkout -b feature/new-algorithm

# コードを編集
vim concept_map_system/algorithms/my_algorithm.py

# フォーマット
make format

# リントチェック
make lint

# 型チェック
make type-check

# テストを追加
vim tests/test_my_algorithm.py

# テスト実行
make test

# すべてのチェック
make check
```

### 2. コミット

Pre-commitフックが自動的に実行されます：

```bash
git add .
git commit -m "feat: add new algorithm"
# → 自動的にruff、mypy、その他のチェックが実行される
```

フックをスキップする場合（推奨しません）：

```bash
git commit -m "message" --no-verify
```

### 3. プルリクエスト

```bash
# すべてのチェックが通ることを確認
make ci

# プッシュ
git push origin feature/new-algorithm

# GitHubでプルリクエストを作成
```

## 開発ツールの詳細

### Ruff

高速なリンター＆フォーマッター。Rustで書かれており、従来のツール（pylint、flake8、black）より大幅に高速です。

```bash
# コードをフォーマット
make format

# フォーマットチェック（変更なし）
make format-check

# リントチェック
make lint

# リントエラーを自動修正
make lint-fix
```

**設定:** `pyproject.toml`の`[tool.ruff]`セクション

**有効なルール:**
- E, W: pycodestyle
- F: pyflakes
- I: isort
- N: pep8-naming
- UP: pyupgrade
- B: flake8-bugbear
- その他多数

### MyPy

静的型チェッカー。型ヒントの誤りを検出します。

```bash
# 型チェック
make type-check
```

**設定:** `pyproject.toml`の`[tool.mypy]`セクション

**型ヒントの例:**

```python
from typing import Dict, List, Optional

def process_data(
    input_list: List[str],
    options: Optional[Dict[str, bool]] = None
) -> Dict[str, int]:
    """Process data with type hints."""
    result: Dict[str, int] = {}
    # ...
    return result
```

### Pytest

テストフレームワーク。シンプルで強力なテスト機能を提供します。

```bash
# テスト実行
make test

# カバレッジ付きテスト
make test-cov

# 詳細モード
make test-verbose

# HTMLカバレッジレポートを開く
make coverage-html
```

**設定:** `pyproject.toml`の`[tool.pytest.ini_options]`セクション

**テストの例:**

```python
import pytest

class TestMyAlgorithm:
    """Test cases for MyAlgorithm."""

    def test_execute_success(self):
        """Test successful execution."""
        algo = MyAlgorithm()
        result = algo.execute("master.csv", "student.csv")
        assert result["method"] == "MyAlgorithm"

    def test_execute_with_invalid_file(self):
        """Test execution with invalid file."""
        algo = MyAlgorithm()
        with pytest.raises(FileNotFoundError):
            algo.execute("nonexistent.csv", "student.csv")
```

### Pre-commit

Gitコミット前に自動的にチェックを実行します。

```bash
# Pre-commitフックをインストール
make pre-commit-install

# すべてのファイルに対して手動実行
make pre-commit-run
```

**設定:** `.pre-commit-config.yaml`

**有効なフック:**
- ruff（リント＆フォーマット）
- mypy（型チェック）
- 標準チェック（trailing-whitespace、end-of-file-fixerなど）
- bandit（セキュリティチェック）

### Bandit

セキュリティ脆弱性を検出します。

```bash
# セキュリティチェック
make security
```

## pyproject.toml

すべての設定を`pyproject.toml`に統一しています。

```toml
[tool.ruff]
# Ruff設定

[tool.mypy]
# MyPy設定

[tool.pytest.ini_options]
# Pytest設定

[tool.coverage.run]
# カバレッジ設定
```

## CI/CD

### GitHub Actions（例）

`.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
        pip install -r requirements-dev.txt

    - name: Run CI checks
      run: make ci
```

## ベストプラクティス

### コーディングスタイル

1. **型ヒントを使用**
   ```python
   def process(data: List[str]) -> Dict[str, int]:
       pass
   ```

2. **Docstringを記述**
   ```python
   def function(arg: str) -> bool:
       """関数の簡潔な説明.

       Args:
           arg: 引数の説明

       Returns:
           戻り値の説明
       """
       pass
   ```

3. **適切な例外処理**
   ```python
   try:
       result = risky_operation()
   except SpecificError as e:
       logger.error(f"Error: {e}")
       raise
   ```

### テスト

1. **各機能にテストを追加**
2. **エッジケースをテスト**
3. **カバレッジ80%以上を維持**

### コミット

1. **小さく、論理的なコミット**
2. **明確なコミットメッセージ**
3. **pre-commitチェックをパス**

## トラブルシューティング

### Ruffのエラー

```bash
# 自動修正を試す
make lint-fix

# 特定のルールを無視（コメント）
# ruff: noqa: E501
```

### MyPyのエラー

```bash
# 特定の行を無視
result = function()  # type: ignore

# モジュール全体を無視（pyproject.toml）
[[tool.mypy.overrides]]
module = "problematic_module.*"
ignore_missing_imports = true
```

### テストの失敗

```bash
# 詳細モードで実行
make test-verbose

# 特定のテストを実行
pytest tests/test_specific.py::TestClass::test_method

# デバッグ出力を有効化
pytest -s tests/
```

## リリースプロセス

1. バージョン番号を更新（`pyproject.toml`）
2. CHANGELOG.mdを更新
3. すべてのチェックをパス: `make ci`
4. タグを作成: `git tag v1.0.0`
5. ビルド: `make build`
6. PyPIに公開: `make publish`（またはTestPyPI: `make publish-test`）

## 参考リンク

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [PEP 8](https://peps.python.org/pep-0008/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## サポート

質問や問題がある場合は、以下の方法でお問い合わせください：

- GitHub Issues
- GitHub Discussions
- メンテナーへの直接連絡
