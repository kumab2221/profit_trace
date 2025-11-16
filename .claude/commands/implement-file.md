# コード実装（仕様 + プラン → ファイル生成）

docs/requirements/02_system-requirements.md と
plans/feature-<機能名>.md を参照し、
src/<ファイル>.py を生成または更新する。

## 制約
- 型アノテーション必須
- ruff / mypy / pytest でエラーなし
- 必要に応じて tests/ に pytest テストも生成