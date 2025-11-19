# Feature Plan: レポート機能

## 1. Background（背景）

### 1.1 概要
- 経営層・PM 向けに、プロジェクトおよびメンバー稼働状況のレポートをグラフと数値の両方で表示し、CSV / JSON 形式でエクスポートする機能
- 全体サマリ（総契約工数、総消化工数、平均消化率）を提供する
- 関連する要求・要件：STK-001, STK-006 → REQ-F-009, REQ-NF-006

### 1.2 関連ドキュメント
- docs/requirements/02_system-requirements.md（REQ-F-009, REQ-NF-006）
- docs/design/03_application-design.md（GenerateReportUseCase, ExportDataUseCase, ReportDTO）
- docs/design/04_presentation-design.md（ReportWidget, ReportViewModel）
- docs/design/05_infrastructure-design.md（CSVWriter, JSONWriter）
- ADR/ADR-002-mvvm-pattern.md
- ADR/ADR-003-sqlite-cache-strategy.md

---

## 2. Objective（目的）

この機能の実装により達成すべき目標を **明確に** 記述する。

- **ユーザー視点での価値**: プロジェクトとメンバー稼働状況のレポートを一画面で確認し、CSV / JSON 形式でエクスポートできる
- **システム視点での価値**:
  - 既存のドメインサービス（ConsumptionRateCalculator, WorkloadAnalyzer）を組み合わせてレポートを生成できる
  - CSV / JSON Writer により、データのバックアップとリストアが可能になる
  - 全体サマリにより、プロジェクト全体の状況を把握できる
- **非機能要件の達成**:
  - REQ-NF-006（バックアップ）: データストアをエクスポート可能
  - REQ-NF-003（操作性）: レポートの表示形式が視覚的にわかりやすい

---

## 3. Scope（スコープ）

### 3.1 In Scope（含む）
この実装計画で **実装する** 機能・タスクを列挙する。

- Application 層の実装
  - GenerateReportUseCase（レポートデータの生成）
  - ExportDataUseCase（データのエクスポート）
  - ReportDTO（レポートデータの DTO）
- Presentation 層の実装
  - ReportWidget（レポート画面）
  - ReportViewModel（データバインディング）
  - グラフ表示（プロジェクト別工数消化、メンバー別稼働状況）
  - 数値表示（表形式）
  - エクスポートボタン（CSV / JSON 選択）
- Infrastructure 層の実装
  - ExportDataUseCase での CSVWriter / JSONWriter 使用
- 単体テスト・統合テスト
  - GenerateReportUseCase のテスト
  - ExportDataUseCase のテスト
  - ReportViewModel のテスト

### 3.2 Out of Scope（含まない）
この実装計画で **実装しない** 機能・タスクを明示する。

- PDF エクスポート（理由：要件定義で CSV / JSON のみ）
- レポートのカスタマイズ機能（理由：要件定義で不要）
- レポートの自動送信機能（理由：要件定義で不要）

---

## 4. Tasks（タスク一覧）

実装タスクを **1〜2 時間粒度** に分解し、以下の形式で列挙する。

### 4.1 Application 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-REPO-001 | ReportDTO の実装 | レポートデータを Presentation 層に渡す DTO を実装 | Application | 0.5h | - | `src/application/dto/report_dto.py` |
| TASK-REPO-002 | GenerateReportUseCase の実装 | Repository から全プロジェクト・工数実績・メンバーを取得し、ドメインサービスを呼び出してレポートデータを生成 | Application | 2.5h | TASK-REPO-001 | `src/application/usecases/generate_report_usecase.py` |
| TASK-REPO-003 | ExportDataUseCase の実装 | SQLite のデータを CSV / JSON 形式でエクスポートする処理を実装 | Application | 2.0h | - | `src/application/usecases/export_data_usecase.py` |

### 4.2 Presentation 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-REPO-004 | ReportViewModel の実装 | GenerateReportUseCase と ExportDataUseCase を呼び出し、Signal/Slot でデータバインディング | Presentation | 2.0h | TASK-REPO-002, TASK-REPO-003 | `src/presentation/viewmodels/report_viewmodel.py` |
| TASK-REPO-005 | ReportWidget の基本実装 | レポート画面の基本レイアウト（グラフエリア、数値エリア、エクスポートボタン）を実装 | Presentation | 2.0h | TASK-REPO-004 | `src/presentation/views/report_widget.py` |
| TASK-REPO-006 | プロジェクト別グラフ表示の実装 | プロジェクト別工数消化状況をグラフ化（plotly） | Presentation | 2.0h | TASK-REPO-005 | `src/presentation/views/report_widget.py`（拡張） |
| TASK-REPO-007 | メンバー別グラフ表示の実装 | メンバー別稼働状況をグラフ化（plotly） | Presentation | 2.0h | TASK-REPO-005 | `src/presentation/views/report_widget.py`（拡張） |
| TASK-REPO-008 | 数値データ表示の実装 | プロジェクト名、契約工数、消化済み工数、消化率などを表形式で表示 | Presentation | 1.5h | TASK-REPO-005 | `src/presentation/views/report_widget.py`（拡張） |
| TASK-REPO-009 | エクスポート機能の実装 | CSV / JSON 選択ダイアログとエクスポート処理を実装 | Presentation | 1.5h | TASK-REPO-004 | `src/presentation/views/report_widget.py`（拡張） |
| TASK-REPO-010 | MainWindow への統合 | メニューに「レポート」を追加し、画面遷移を実装 | Presentation | 1.0h | TASK-REPO-009 | `src/presentation/views/main_window.py`（拡張） |

### 4.3 テストタスク（Testing）

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-REPO-011 | GenerateReportUseCase のテスト | レポートデータ生成〜DTO 変換までのテスト | Application | 1.5h | TASK-REPO-002 | `tests/application/usecases/test_generate_report_usecase.py` |
| TASK-REPO-012 | ExportDataUseCase のテスト | CSV / JSON エクスポート処理のテスト | Application | 1.5h | TASK-REPO-003 | `tests/application/usecases/test_export_data_usecase.py` |
| TASK-REPO-013 | ReportViewModel のテスト | Signal/Slot の発火タイミング、エラーハンドリングのテスト | Presentation | 1.0h | TASK-REPO-004 | `tests/presentation/viewmodels/test_report_viewmodel.py` |
| TASK-REPO-014 | ReportWidget の統合テスト | レポート表示〜エクスポートまでの一連の流れをテスト | Presentation | 1.5h | TASK-REPO-010 | `tests/presentation/views/test_report_widget.py` |

---

## 5. Estimation（見積もり）

### 5.1 タスク別見積もり

| カテゴリ | タスク数 | 合計工数 |
|----------|---------|---------|
| Application 層 | 3 | 5.0h |
| Presentation 層 | 7 | 12.0h |
| Testing | 4 | 5.5h |
| **合計** | **14** | **22.5h** |

### 5.2 スケジュール目安

- **開発期間**：5〜6 日（1 日 4〜5 時間作業想定）
- **マイルストーン**：
  - Day 1-2：Application 層完了
  - Day 3-4：Presentation 層完了
  - Day 5：テスト完了・統合確認
  - Day 6：バッファ（予備日）

---

## 6. Dependencies（依存関係）

### 6.1 外部依存

このプランの実装に必要な外部要素を列挙する。

- **ライブラリ**：`plotly`（グラフ描画）、`PySide6`（QWebEngineView）、`pytest`、`pytest-qt`
- **環境**：Python 3.12、SQLite

### 6.2 内部依存

他のプラン・機能との依存関係を明示する。

- **依存先**：
  - `feature-infrastructure.md`（Repository 実装、CSV/JSON Writer が必要）
  - `feature-data-import.md`（データインポート後にレポートを生成）
  - `feature-project-list.md`（ConsumptionRateCalculator を再利用）
  - `feature-member-workload.md`（WorkloadAnalyzer を再利用）
- **依存元**：なし

---

## 7. Risks（リスク/懸念点）

実装時に想定されるリスクと、その軽減策を記述する。

### 7.1 技術的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| QWebEngineView のメモリ消費（複数グラフ表示） | 中 | グラフは 1 画面に 2 つまでとし、必要に応じてタブ切り替えで表示 |
| エクスポートファイルサイズが大きい | 低 | 現在の想定（プロジェクト 50 件、工数実績 5000 件）では問題ないが、将来的に圧縮を検討 |

### 7.2 仕様的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| レポートの表示項目が不足 | 低 | 要件定義書に記載された項目（各プロジェクトの残工数（利益）、個人の負荷率）を実装 |
| エクスポート形式の要望が増える可能性 | 低 | 要件定義で CSV / JSON のみと明記されているため、将来の拡張候補として記録 |

---

## 8. Deliverables（成果物）

このプラン完了時点で生成されるファイル一覧。

### 8.1 実装ファイル

- `src/application/dto/report_dto.py`
- `src/application/usecases/generate_report_usecase.py`
- `src/application/usecases/export_data_usecase.py`
- `src/presentation/viewmodels/report_viewmodel.py`
- `src/presentation/views/report_widget.py`
- `src/presentation/views/main_window.py`（拡張）

### 8.2 テストファイル

- `tests/application/usecases/test_generate_report_usecase.py`
- `tests/application/usecases/test_export_data_usecase.py`
- `tests/presentation/viewmodels/test_report_viewmodel.py`
- `tests/presentation/views/test_report_widget.py`

---

## 9. Acceptance Criteria（受入条件）

このプランが「完了」と判断される条件を明確に記述する。

- [ ] すべてのタスクが完了している
- [ ] プロジェクトおよびメンバー稼働状況のレポートをグラフと数値の両方で表示できること
- [ ] レポートの表示形式が視覚的にわかりやすいこと
- [ ] レポートのエクスポート機能があること（CSV / JSON 選択可能）
- [ ] 全体サマリ（総契約工数、総消化工数、平均消化率）が表示されること
- [ ] レポートの表示項目が要件定義書の内容（各プロジェクトの残工数（利益）、個人の負荷率）を含むこと
- [ ] データストアをエクスポート可能であること（REQ-NF-006）
- [ ] バックアップファイルからリストアできること
- [ ] 単体テストがすべて成功している（カバレッジ 80% 以上）
- [ ] 統合テストでレポート表示〜エクスポートが正常動作すること
- [ ] コードレビューが完了している（ruff / mypy エラーなし）

---

## 10. Notes（備考）

実装時の注意事項や参考情報を記載する。

- レポートのエクスポート形式は CSV または JSON（REQ-F-009 の備考に記載）
- レポートの表示項目：各プロジェクトの残工数（利益）、個人の負荷率（REQ-F-009 の備考に記載）
- グラフは plotly で実装し、QWebEngineView で表示する
- 数値データは QTableWidget で表形式表示する
- エクスポート機能は ExportDataUseCase を使用し、CSVWriter / JSONWriter で実装する
- リストア時のデータ整合性チェックは不要（REQ-NF-006 の備考に記載）
- ADR-003 の「Single Source of Truth は CSV / JSON ファイル」という方針に従い、エクスポート機能を実装する
