# 開発ガイド

概念マップ採点統合システムへの貢献を歓迎します！このドキュメントでは、開発環境のセットアップと開発ワークフローについて説明します。

## 目次

- [開発環境のセットアップ](#開発環境のセットアップ)
- [開発ワークフロー](#開発ワークフロー)
- [コーディング規約](#コーディング規約)
- [テスト](#テスト)
- [ドキュメント](#ドキュメント)
- [プルリクエスト](#プルリクエスト)

## 開発環境のセットアップ

### 前提条件

- Python 3.8以降
- Git
- make（オプション、推奨）

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/concept-map-system.git
cd concept-map-system
```

### 2. 開発環境のセットアップ

#### Makefileを使用する場合（推奨）

```bash
make dev
```

これにより以下が自動的に実行されます：
- 開発用依存関係のインストール
- pre-commitフックのインストール

#### 手動でセットアップする場合

```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Linux/macOS
# または
venv\Scripts\activate  # Windows

# 開発用依存関係のインストール
pip install -e ".[dev]"
pip install -r requirements-dev.txt

# pre-commitフックのインストール
pre-commit install
```

### 3. セットアップの確認

```bash
# 利用可能なコマンドを確認
make help

# すべてのチェックを実行
make check
```

## 開発ワークフロー

### ブランチ戦略

1. `main`ブランチから新しいブランチを作成
2. 機能開発またはバグ修正を実施
3. コミット前に品質チェックを実行
4. プルリクエストを作成

```bash
# 新しいブランチを作成
git checkout -b feature/your-feature-name

# 変更を実装
# ...

# 品質チェックを実行
make check

# コミット
git add .
git commit -m "feat: your feature description"

# プッシュ
git push origin feature/your-feature-name
```

### コミットメッセージ

コミットメッセージは以下の形式に従ってください：

```
<type>: <subject>

<body>

<footer>
```

**Type:**
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメントの変更
- `style`: コードの意味に影響しない変更（フォーマットなど）
- `refactor`: リファクタリング
- `test`: テストの追加・修正
- `chore`: ビルドプロセスやツールの変更

**例:**
```
feat: add custom algorithm template

カスタムアルゴリズムを簡単に作成できるテンプレートを追加。
BaseAlgorithmクラスを継承し、必要なメソッドを実装するだけで
新しいアルゴリズムを追加できる。

Closes #123
```

## コーディング規約

### Pythonコーディングスタイル

このプロジェクトは以下のツールを使用してコーディングスタイルを統一しています：

#### Ruff（リンター＆フォーマッター）

```bash
# コードのフォーマット
make format

# リントチェック
make lint

# 自動修正
make lint-fix
```

#### MyPy（型チェック）

```bash
# 型チェック
make type-check
```

#### Bandit（セキュリティチェック）

```bash
# セキュリティチェック
make security
```

### コーディングガイドライン

1. **PEP 8準拠**: Pythonの標準コーディング規約に従う
2. **型ヒント**: 可能な限り型ヒントを使用
3. **Docstring**: すべての公開API、関数、クラスにdocstringを記述
4. **命名規則**:
   - クラス: `PascalCase`
   - 関数/メソッド: `snake_case`
   - 定数: `UPPER_SNAKE_CASE`
5. **行の長さ**: 最大100文字
6. **インポート順序**: 標準ライブラリ → サードパーティ → ローカル

### Docstringの形式

Google形式のdocstringを使用します：

```python
def example_function(arg1: str, arg2: int) -> bool:
    """関数の簡潔な説明。

    より詳細な説明（必要な場合）。

    Args:
        arg1: 第一引数の説明
        arg2: 第二引数の説明

    Returns:
        戻り値の説明

    Raises:
        ValueError: 例外が発生する条件の説明
    """
    pass
```

## テスト

### テストの実行

```bash
# すべてのテストを実行
make test

# カバレッジ付きでテストを実行
make test-cov

# 詳細モードでテストを実行
make test-verbose
```

### テストの作成

1. `tests/`ディレクトリにテストファイルを作成
2. ファイル名は`test_*.py`または`*_test.py`
3. テストクラスは`Test*`で始める
4. テストメソッドは`test_*`で始める

**例:**

```python
import pytest
from concept_map_system.core import AlgorithmRegistry


class TestAlgorithmRegistry:
    """Test cases for AlgorithmRegistry."""

    def test_list_algorithms(self):
        """Test listing registered algorithms."""
        algorithms = AlgorithmRegistry.list_algorithms()
        assert isinstance(algorithms, list)
        assert len(algorithms) > 0

    def test_get_algorithm(self):
        """Test getting an algorithm by name."""
        algo = AlgorithmRegistry.get_algorithm("mcclure")
        assert algo is not None
```

### テストカバレッジ

- 新しいコードには必ずテストを追加
- カバレッジは80%以上を目標
- カバレッジレポートを確認: `make coverage-html`

## ドキュメント

### ドキュメントの更新

コードの変更に伴い、以下のドキュメントを更新してください：

- `README.md`: 機能の追加・変更
- `USAGE_EXAMPLES.md`: 新しい使用例
- `CONTRIBUTING.md`: 開発プロセスの変更
- コード内のdocstring

## プルリクエスト

### プルリクエストを作成する前に

1. すべての品質チェックが通ることを確認
   ```bash
   make check
   ```

2. テストを追加・更新
   ```bash
   make test
   ```

3. ドキュメントを更新

### プルリクエストのテンプレート

```markdown
## 概要
変更の簡潔な説明

## 変更内容
- 変更点1
- 変更点2

## 動機と背景
なぜこの変更が必要か

## テスト方法
変更をテストする方法

## チェックリスト
- [ ] コードフォーマットを実行 (`make format`)
- [ ] リントチェックを実行 (`make lint`)
- [ ] 型チェックを実行 (`make type-check`)
- [ ] テストを追加・更新 (`make test`)
- [ ] ドキュメントを更新
- [ ] CHANGELOG.mdを更新（必要な場合）

## 関連Issue
Closes #(issue番号)
```

## 便利なMakeコマンド

| コマンド | 説明 |
|---------|------|
| `make help` | すべてのコマンドを表示 |
| `make dev` | 開発環境をセットアップ |
| `make clean` | ビルドアーティファクトをクリーンアップ |
| `make format` | コードをフォーマット |
| `make lint` | リントチェック |
| `make lint-fix` | リントエラーを自動修正 |
| `make type-check` | 型チェック |
| `make test` | テストを実行 |
| `make test-cov` | カバレッジ付きでテストを実行 |
| `make check` | すべてのチェックを実行 |
| `make ci` | CI環境でのチェック |
| `make pre-commit-run` | pre-commitフックを実行 |

## トラブルシューティング

### pre-commitフックが失敗する

```bash
# pre-commitフックを手動で実行
pre-commit run --all-files

# 特定のフックをスキップ
SKIP=mypy git commit -m "message"
```

### 依存関係の問題

```bash
# 依存関係を再インストール
pip install -e ".[dev]" --force-reinstall

# キャッシュをクリア
make clean
```

### テストの失敗

```bash
# 詳細モードでテストを実行
make test-verbose

# 特定のテストを実行
pytest tests/test_algorithm_registry.py::TestAlgorithmRegistry::test_list_algorithms
```

## サポート

質問や提案がある場合は、以下の方法でお問い合わせください：

- Issueを作成
- ディスカッションに投稿
- メンテナーに連絡

## ライセンス

このプロジェクトに貢献することで、あなたの貢献がプロジェクトと同じライセンス（MIT License）の下でライセンスされることに同意したものとみなされます。
