# 環境別デバッグログ機能

このドキュメントでは、開発環境と本番環境で異なるログレベルを設定する機能について説明します。

## 概要

このアプリケーションは、環境変数に基づいてログレベルと形式を自動的に設定します：

- **開発環境**: 詳細なデバッグログを出力（関数名、行番号を含む）
- **本番環境**: 必要な情報のみを出力（INFO以上）

## 環境変数

以下の環境変数で環境を設定できます：

- `ENVIRONMENT`: 主要な環境変数（優先）
- `ENV`: `ENVIRONMENT`が設定されていない場合の代替

### 設定可能な値

**開発環境として認識される値:**
- `development`
- `dev`
- `local`

**本番環境として認識される値:**
- `production`
- その他の値（デフォルト）

## ログ形式

### 開発環境のログ形式
```
%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s
```

**例:**
```
2025-11-14 03:41:57 - __main__ - DEBUG - main:56 - Processing file: example.txt
```

### 本番環境のログ形式
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**例:**
```
2025-11-14 03:42:05 - __main__ - INFO - File processing started
```

## 使用方法

### Docker環境での設定

`docker-compose.yml`や`Dockerfile`で環境変数を設定：

```yaml
environment:
  - ENVIRONMENT=development
```

または

```dockerfile
ENV ENVIRONMENT=development
```

### ローカル実行時の設定

```bash
# 開発モードで実行
ENVIRONMENT=development poetry run uvicorn src.main:app --reload

# 本番モードで実行
ENVIRONMENT=production poetry run uvicorn src.main:app
```

### Kubernetes/App Serviceでの設定

環境変数として`ENVIRONMENT`を設定：

```yaml
env:
  - name: ENVIRONMENT
    value: production
```

## コード例

### ログの出力

```python
import logging

logger = logging.getLogger(__name__)

# 開発環境でのみ表示される詳細ログ
logger.debug("ファイルの詳細情報: サイズ=1024バイト, 作成日時=2025-11-14")

# 両環境で表示される重要な情報
logger.info("ファイル処理が完了しました")

# エラー情報（常に表示）
logger.error("ファイル処理中にエラーが発生しました")
```

## デモ

デモスクリプトを実行して、環境ごとのログの違いを確認できます：

```bash
# 開発環境での実行
ENVIRONMENT=development python /tmp/demo_logging.py

# 本番環境での実行
ENVIRONMENT=production python /tmp/demo_logging.py
```

## テスト

ログ設定のテストは`tests/test_logging.py`に含まれています：

```bash
poetry run pytest tests/test_logging.py -v
```

## 追加されたデバッグログ

以下の箇所に詳細なデバッグログが追加されました：

### Controller (`controller.py`)
- ファイルアップロード開始/完了時のログ
- リクエスト処理の開始/完了時のログ
- エラー発生時の詳細情報

### Services
- **FileUploadService**: ファイル保存の詳細
- **CodeInterpreterService**: 各処理ステップの詳細
  - ファイルアップロード
  - エージェント作成
  - スレッド作成
  - メッセージ送信
  - 実行結果の処理

## 利点

1. **開発効率の向上**: 開発中は詳細なログで問題を素早く特定
2. **本番環境のパフォーマンス**: 不要なログを削減してパフォーマンスを最適化
3. **セキュリティ**: 本番環境で機密情報を含む可能性のあるデバッグログを非表示
4. **柔軟性**: 環境変数で簡単に切り替え可能
