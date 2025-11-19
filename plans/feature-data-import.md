# Feature Plan: データインポート機能

## 1. Background（背景）

### 1.1 概要
- CSV/JSON ファイルから、プロジェクト契約情報・工数実績データ・休日マスタをインポートする機能
- 日次でデータを再読み込みし、SQLite を上書き更新することでデータの整合性を保証する
- 関連する要求・要件：STK-002, STK-003, STK-005 → REQ-F-001, REQ-F-002, REQ-F-003, REQ-F-008

### 1.2 関連ドキュメント
- docs/requirements/02_system-requirements.md（REQ-F-001, REQ-F-002, REQ-F-003, REQ-F-008, REQ-NF-001）
- docs/design/03_application-design.md（ImportProjectUseCase, ImportWorkRecordUseCase, ImportWorkdayCalendarUseCase）
- docs/design/04_presentation-design.md（ImportDialog, ImportViewModel）
- docs/design/05_infrastructure-design.md（CSVReader, JSONReader）
- ADR/ADR-003-sqlite-cache-strategy.md

---

## 2. Objective（目的）

この機能の実装により達成すべき目標を **明確に** 記述する。

- **ユーザー視点での価値**: CSV/JSON ファイルをドラッグ&ドロップまたはファイル選択で簡単にインポートできる
- **システム視点での価値**:
  - CSV/JSON フォーマットのバリデーションにより、不正データの混入を防ぐ
  - SQLite を上書き更新することで、データの整合性を保証する
  - プログレスバーとエラーダイアログにより、ユーザー体験が向上する
- **非機能要件の達成**:
  - REQ-NF-001（パフォーマンス）: プロジェクト契約 50 件の読み込みは 5 秒以内、工数実績 5000 件の読み込みは 10 秒以内
  - REQ-NF-003（操作性）: ドラッグ&ドロップでのファイル取り込み、明確なエラーメッセージ表示
  - REQ-NF-005（ログ記録）: エラー発生時にログファイルに記録

---

## 3. Scope（スコープ）

### 3.1 In Scope（含む）
この実装計画で **実装する** 機能・タスクを列挙する。

- Application 層の実装
  - ImportProjectUseCase（プロジェクト契約情報の CSV インポート）
  - ImportWorkRecordUseCase（工数実績データの CSV インポート）
  - ImportWorkdayCalendarUseCase（休日マスタの JSON インポート）
  - ImportResult DTO（インポート結果の返却）
- Presentation 層の実装
  - ImportDialog（ファイル選択・ドラッグ&ドロップ UI）
  - ImportViewModel（Application 層とのデータバインディング）
  - プログレスバー（インポート進捗表示）
  - エラーダイアログ（エラーメッセージ表示）
- 単体テスト・統合テスト
  - ユースケースの単体テスト（バリデーション、エラーハンドリング）
  - ViewModel のテスト（Signal/Slot の発火）

### 3.2 Out of Scope（含まない）
この実装計画で **実装しない** 機能・タスクを明示する。

- ドメインサービスの詳細ロジック（理由：別プランで対応）
- プロジェクト一覧画面（理由：feature-project-list.md で対応）
- データのエクスポート機能（理由：feature-report.md で対応）

---

## 4. Tasks（タスク一覧）

実装タスクを **1〜2 時間粒度** に分解し、以下の形式で列挙する。

### 4.1 Application 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-IMPORT-001 | ImportResult DTO の実装 | インポート結果を返す DTO を実装（success, imported_count, errors） | Application | 0.5h | - | `src/application/dto/import_result.py` |
| TASK-IMPORT-002 | ImportProjectUseCase の実装 | プロジェクト契約情報の CSV インポート処理、バリデーション、SQLite 上書き更新 | Application | 2.5h | TASK-IMPORT-001 | `src/application/usecases/import_project_usecase.py` |
| TASK-IMPORT-003 | ImportWorkRecordUseCase の実装 | 工数実績データの CSV インポート処理、バリデーション、SQLite 上書き更新 | Application | 3.0h | TASK-IMPORT-001 | `src/application/usecases/import_work_record_usecase.py` |
| TASK-IMPORT-004 | ImportWorkdayCalendarUseCase の実装 | 休日マスタの JSON インポート処理、バリデーション、SQLite 上書き更新 | Application | 2.0h | TASK-IMPORT-001 | `src/application/usecases/import_workday_calendar_usecase.py` |

### 4.2 Presentation 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-IMPORT-005 | ImportViewModel の実装 | インポート処理を QThread で実行し、Signal/Slot でデータバインディング | Presentation | 2.5h | TASK-IMPORT-002, TASK-IMPORT-003, TASK-IMPORT-004 | `src/presentation/viewmodels/import_viewmodel.py` |
| TASK-IMPORT-006 | ImportDialog の実装 | ファイル選択ダイアログ、ドラッグ&ドロップ UI を PySide6 で実装 | Presentation | 2.0h | TASK-IMPORT-005 | `src/presentation/views/import_dialog.py` |
| TASK-IMPORT-007 | プログレスバーの実装 | インポート進捗を表示する QProgressDialog を実装 | Presentation | 1.0h | TASK-IMPORT-006 | `src/presentation/views/import_dialog.py`（拡張） |
| TASK-IMPORT-008 | エラーダイアログの実装 | エラーメッセージを表示する QMessageBox を実装 | Presentation | 0.5h | TASK-IMPORT-006 | `src/presentation/views/import_dialog.py`（拡張） |
| TASK-IMPORT-009 | MainWindow へのインポート機能統合 | メインメニューに「ファイル → インポート」を追加し、ImportDialog を表示 | Presentation | 1.0h | TASK-IMPORT-006 | `src/presentation/views/main_window.py`（拡張） |

### 4.3 テストタスク（Testing）

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-IMPORT-010 | ImportProjectUseCase の単体テスト | バリデーション（フォーマット不正、必須項目欠落）のテスト | Application | 1.5h | TASK-IMPORT-002 | `tests/application/usecases/test_import_project_usecase.py` |
| TASK-IMPORT-011 | ImportWorkRecordUseCase の単体テスト | バリデーション（フォーマット不正、未登録プロジェクト）のテスト | Application | 1.5h | TASK-IMPORT-003 | `tests/application/usecases/test_import_work_record_usecase.py` |
| TASK-IMPORT-012 | ImportWorkdayCalendarUseCase の単体テスト | バリデーション（JSON スキーマ不正）のテスト | Application | 1.0h | TASK-IMPORT-004 | `tests/application/usecases/test_import_workday_calendar_usecase.py` |
| TASK-IMPORT-013 | ImportViewModel のテスト | Signal/Slot の発火タイミング、エラーハンドリングのテスト | Presentation | 1.5h | TASK-IMPORT-005 | `tests/presentation/viewmodels/test_import_viewmodel.py` |
| TASK-IMPORT-014 | ImportDialog の統合テスト | ファイル選択〜インポート完了までの一連の流れをテスト | Presentation | 1.5h | TASK-IMPORT-009 | `tests/presentation/views/test_import_dialog.py` |

---

## 5. Estimation（見積もり）

### 5.1 タスク別見積もり

| カテゴリ | タスク数 | 合計工数 |
|----------|---------|---------|
| Application 層 | 4 | 8.0h |
| Presentation 層 | 5 | 7.0h |
| Testing | 5 | 7.0h |
| **合計** | **14** | **22.0h** |

### 5.2 スケジュール目安

- **開発期間**：5〜6 日（1 日 4〜5 時間作業想定）
- **マイルストーン**：
  - Day 1-2：Application 層完了（ユースケース実装）
  - Day 3-4：Presentation 層完了（UI 実装）
  - Day 5：テスト完了・統合確認
  - Day 6：バッファ（予備日）

---

## 6. Dependencies（依存関係）

### 6.1 外部依存

このプランの実装に必要な外部要素を列挙する。

- **ライブラリ**：
  - `pandas`（CSV パース用）
  - `PySide6`（UI 実装用）
  - `pytest`（テスト用）
  - `pytest-qt`（Qt テスト用）
- **ファイル**：サンプル CSV/JSON ファイル（テスト用）
- **環境**：Python 3.12、SQLite

### 6.2 内部依存

他のプラン・機能との依存関係を明示する。

- **依存先**：`feature-infrastructure.md`（Repository 実装、CSV/JSON Reader が必要）
- **依存元**：
  - `feature-project-list.md`（データインポート後にプロジェクト一覧を表示）
  - `feature-burndown-chart.md`（データインポート後にバーンダウンチャートを表示）
  - `feature-member-workload.md`（データインポート後にメンバー稼働状況を表示）

---

## 7. Risks（リスク/懸念点）

実装時に想定されるリスクと、その軽減策を記述する。

### 7.1 技術的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| CSV エンコーディングが不明（UTF-8 以外） | 中 | chardet ライブラリでエンコーディング自動判定を実装 |
| 大容量 CSV（10 万行以上）の処理時間 | 高 | チャンク読み込み（pandas.read_csv の chunksize）を使用し、プログレスバーで進捗表示 |
| QThread のメモリリーク | 中 | QThread を正しく終了（quit + wait）し、単体テストで検証 |
| SQLite への一括挿入のパフォーマンス | 中 | executemany を使用し、トランザクション（commit）を適切に管理 |

### 7.2 仕様的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| CSV フォーマットのバリエーション（列名の違い） | 中 | サンプルファイルを複数パターン用意してテスト |
| インポート失敗時のロールバック方針が不明確 | 高 | 要件定義書に戻って確認（現在は上書き更新のため、ロールバック不要） |
| 未登録プロジェクトの工数実績の扱い | 中 | 警告表示し、該当データをスキップ |

---

## 8. Deliverables（成果物）

このプラン完了時点で生成されるファイル一覧。

### 8.1 実装ファイル

**Application 層**
- `src/application/dto/import_result.py`
- `src/application/usecases/import_project_usecase.py`
- `src/application/usecases/import_work_record_usecase.py`
- `src/application/usecases/import_workday_calendar_usecase.py`

**Presentation 層**
- `src/presentation/viewmodels/import_viewmodel.py`
- `src/presentation/views/import_dialog.py`
- `src/presentation/views/main_window.py`（拡張）

### 8.2 テストファイル

- `tests/application/usecases/test_import_project_usecase.py`
- `tests/application/usecases/test_import_work_record_usecase.py`
- `tests/application/usecases/test_import_workday_calendar_usecase.py`
- `tests/presentation/viewmodels/test_import_viewmodel.py`
- `tests/presentation/views/test_import_dialog.py`

### 8.3 ドキュメント

- サンプル CSV/JSON ファイル（`tests/fixtures/sample_project.csv`, `tests/fixtures/sample_work_record.csv`, `tests/fixtures/sample_workday_calendar.json`）

---

## 9. Acceptance Criteria（受入条件）

このプランが「完了」と判断される条件を明確に記述する。

- [ ] すべてのタスクが完了している
- [ ] CSV/JSON ファイルをドラッグ&ドロップまたはファイル選択でインポート可能であること
- [ ] CSV/JSON フォーマットのバリデーション（必須項目、日付形式、数値の妥当性）が実装されていること
- [ ] 不正フォーマット検出時にエラーメッセージを表示し、取り込みを中止すること
- [ ] 未登録プロジェクトを検出し、警告表示すること
- [ ] SQLite を上書き更新し、データの整合性が保証されること
- [ ] インポート中にプログレスバーが表示され、UI がフリーズしないこと（QThread 使用）
- [ ] インポート完了後に完了ダイアログが表示されること
- [ ] エラー発生時にエラーダイアログが表示され、ログファイルに記録されること
- [ ] 単体テストがすべて成功している（カバレッジ 80% 以上）
- [ ] 統合テストで CSV/JSON インポート〜SQLite 保存〜データ取得が正常動作すること
- [ ] コードレビューが完了している（ruff / mypy エラーなし）

---

## 10. Notes（備考）

実装時の注意事項や参考情報を記載する。

- CSV パーサーは pandas.read_csv() を使用するが、エラー処理は独自実装する
- JSON パーサーは json.load() を使用し、JSON Schema でバリデーションを行う
- UI は PySide6 の QFileDialog（ファイル選択）と QProgressDialog（プログレスバー）を使用する
- インポート処理は QThread で実行し、UI をフリーズさせない（ADR-002 の方針に従う）
- CSV/JSON ファイルのエンコーディングは UTF-8 を推奨し、chardet で自動判定する
- SQLite への一括挿入は executemany を使用し、パフォーマンスを最適化する
- ADR-003 の「Single Source of Truth は CSV/JSON ファイル」という方針を遵守する
