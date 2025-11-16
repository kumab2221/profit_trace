# CI/CD 設定コマンド（Jenkinsfile / GitHub Actions）

## 目的:
- プロジェクトの CI/CD 設定ファイル（Jenkinsfile, GitHub Actions Workflow）を
プロジェクト方針に合わせて自動生成する。

## 前提
- プロジェクトは Python（uv）を利用
- ruff / mypy / pytest / lizard を使った品質チェックを CI で回す
- main ブランチへの push / PR をトリガーとする

## 手順（共通）

1. プロジェクトルート構成（src, tests, uv, ruff, mypy 設定）を確認する。
2. Jenkins 用の `Jenkinsfile`（パイプライン）を生成する。
3. GitHub Actions 用の `.github/workflows/ci.yml` を生成する。
4. どのツールで何を行うかをコメントとして明記する。

## Jenkinsfile の要件

- パイプライン構成:
- Checkout
- Python / uv セットアップ
- 依存関係インストール
- ruff 実行
- mypy 実行
- lizard 実行
- pytest 実行
- main ブランチ向けのパイプライン定義
- 将来の拡張（デプロイステージ）のためのコメントを残すこと

## GitHub Actions ci.yml の要件

- トリガー:
- push: main
- pull_request: main
- ジョブ:
- ubuntu-latest で実行
- Python バージョン 3.x
- uv インストール
- 依存関係インストール
- ruff / mypy / pytest 実行
- キャッシュ（pip or uv）を可能なら利用

## 出力

- プロジェクトルートに以下のファイルを生成する Markdown or パッチを出力する:
- `Jenkinsfile`
- `.github/workflows/ci.yml`
- 各ステップにコメントを付け、読み手が CI/CD の流れを理解できるようにする。