# Feature Plan: バーンダウンチャート機能

## 1. Background（背景）

### 1.1 概要
- プロジェクト詳細画面で、終了日までの残日数と工数消化状況をバーンダウンチャート形式で表示する機能
- 理想線と実績線を比較し、現在日の位置をマーキングすることで進捗状況を可視化する
- 関連する要求・要件：STK-004, STK-005 → REQ-F-005

### 1.2 関連ドキュメント
- docs/requirements/02_system-requirements.md（REQ-F-005, REQ-NF-002）
- docs/design/02_domain-design.md（BurndownCalculator）
- docs/design/03_application-design.md（GetBurndownChartUseCase, BurndownChartDTO）
- docs/design/04_presentation-design.md（ProjectDetailWidget, ProjectDetailViewModel）
- ADR/ADR-002-mvvm-pattern.md

---

## 2. Objective（目的）

この機能の実装により達成すべき目標を **明確に** 記述する。

- **ユーザー視点での価値**: バーンダウンチャートで理想線と実績線を比較し、進捗の遅れや余剰を直感的に把握できる
- **システム視点での価値**:
  - BurndownCalculator により、バーンダウン計算ロジックが Domain 層に集約される
  - 営業日カレンダーを考慮した正確な理想線が計算できる
  - plotly によるインタラクティブなチャート表示が可能になる
- **非機能要件の達成**:
  - REQ-NF-002（パフォーマンス）: チャート描画時間が 3 秒以内
  - REQ-NF-003（操作性）: チャートがインタラクティブ（ズーム、ホバー表示）

---

## 3. Scope（スコープ）

### 3.1 In Scope（含む）
この実装計画で **実装する** 機能・タスクを列挙する。

- Domain 層の実装
  - BurndownCalculator（理想線・実績線の計算）
  - Point データクラス（チャートのデータポイント）
- Application 層の実装
  - GetBurndownChartUseCase（バーンダウンチャートデータの取得）
  - BurndownChartDTO（チャートデータの DTO）
- Presentation 層の実装
  - ProjectDetailWidget（バーンダウンチャート画面）
  - ProjectDetailViewModel（データバインディング）
  - QWebEngineView による plotly チャート表示
  - 現在日マーカーの表示
- 単体テスト・統合テスト
  - BurndownCalculator のテスト（理想線・実績線計算）
  - GetBurndownChartUseCase のテスト
  - ProjectDetailViewModel のテスト

### 3.2 Out of Scope（含まない）
この実装計画で **実装しない** 機能・タスクを明示する。

- 工数余剰要因の分析（理由：feature-factor-analysis.md で対応）
- チャートのエクスポート機能（理由：feature-report.md で対応）
- リアルタイム更新（理由：要件定義で不要）

---

## 4. Tasks（タスク一覧）

実装タスクを **1〜2 時間粒度** に分解し、以下の形式で列挙する。

### 4.1 Domain 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-BURN-001 | Point データクラスの実装 | チャートのデータポイント（日付、残工数）を表す dataclass を実装 | Domain | 0.5h | - | `src/domain/value_objects/point.py` |
| TASK-BURN-002 | BurndownCalculator の理想線計算実装 | 営業日カレンダーを考慮して理想線を計算するメソッドを実装 | Domain | 2.0h | TASK-BURN-001 | `src/domain/services/burndown_calculator.py` |
| TASK-BURN-003 | BurndownCalculator の実績線計算実装 | 工数実績データから実績線を計算するメソッドを実装 | Domain | 2.0h | TASK-BURN-001, TASK-BURN-002 | `src/domain/services/burndown_calculator.py`（拡張） |

### 4.2 Application 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-BURN-004 | BurndownChartDTO の実装 | バーンダウンチャートデータを Presentation 層に渡す DTO を実装 | Application | 0.5h | TASK-BURN-001 | `src/application/dto/burndown_chart_dto.py` |
| TASK-BURN-005 | GetBurndownChartUseCase の実装 | Repository からプロジェクト・工数実績・営業日カレンダーを取得し、BurndownCalculator を呼び出してチャートデータを生成 | Application | 2.5h | TASK-BURN-003, TASK-BURN-004 | `src/application/usecases/get_burndown_chart_usecase.py` |

### 4.3 Presentation 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-BURN-006 | ProjectDetailViewModel の実装 | GetBurndownChartUseCase を呼び出し、plotly の JSON 形式に変換してSignal で View に通知 | Presentation | 2.0h | TASK-BURN-005 | `src/presentation/viewmodels/project_detail_viewmodel.py` |
| TASK-BURN-007 | ProjectDetailWidget の実装 | QWebEngineView で plotly チャートを表示する画面を実装 | Presentation | 2.5h | TASK-BURN-006 | `src/presentation/views/project_detail_widget.py` |
| TASK-BURN-008 | plotly チャート生成ロジックの実装 | 理想線・実績線・現在日マーカーを plotly で描画するロジックを実装 | Presentation | 2.0h | TASK-BURN-007 | `src/presentation/views/project_detail_widget.py`（拡張） |
| TASK-BURN-009 | MainWindow への統合 | プロジェクト一覧から詳細画面への遷移を実装 | Presentation | 1.0h | TASK-BURN-008 | `src/presentation/views/main_window.py`（拡張） |

### 4.4 テストタスク（Testing）

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-BURN-010 | BurndownCalculator 理想線計算のテスト | 営業日数計算、理想線計算（正常系・異常系）のテスト | Domain | 1.5h | TASK-BURN-002 | `tests/domain/services/test_burndown_calculator.py` |
| TASK-BURN-011 | BurndownCalculator 実績線計算のテスト | 工数実績から実績線を計算するロジックのテスト | Domain | 1.5h | TASK-BURN-003 | `tests/domain/services/test_burndown_calculator.py`（拡張） |
| TASK-BURN-012 | GetBurndownChartUseCase のテスト | プロジェクト取得〜チャートデータ生成までのテスト | Application | 1.5h | TASK-BURN-005 | `tests/application/usecases/test_get_burndown_chart_usecase.py` |
| TASK-BURN-013 | ProjectDetailViewModel のテスト | Signal/Slot の発火タイミング、エラーハンドリングのテスト | Presentation | 1.0h | TASK-BURN-006 | `tests/presentation/viewmodels/test_project_detail_viewmodel.py` |
| TASK-BURN-014 | ProjectDetailWidget の統合テスト | チャート表示〜画面遷移までの一連の流れをテスト | Presentation | 1.5h | TASK-BURN-009 | `tests/presentation/views/test_project_detail_widget.py` |

---

## 5. Estimation（見積もり）

### 5.1 タスク別見積もり

| カテゴリ | タスク数 | 合計工数 |
|----------|---------|---------|
| Domain 層 | 3 | 4.5h |
| Application 層 | 2 | 3.0h |
| Presentation 層 | 4 | 7.5h |
| Testing | 5 | 7.0h |
| **合計** | **14** | **22.0h** |

### 5.2 スケジュール目安

- **開発期間**：5〜6 日（1 日 4〜5 時間作業想定）
- **マイルストーン**：
  - Day 1-2：Domain 層完了（BurndownCalculator 実装）
  - Day 3-4：Application 層・Presentation 層完了
  - Day 5：テスト完了・統合確認
  - Day 6：バッファ（予備日）

---

## 6. Dependencies（依存関係）

### 6.1 外部依存

このプランの実装に必要な外部要素を列挙する。

- **ライブラリ**：`plotly`（チャート描画）、`PySide6`（QWebEngineView）、`pytest`、`pytest-qt`
- **環境**：Python 3.12、SQLite

### 6.2 内部依存

他のプラン・機能との依存関係を明示する。

- **依存先**：
  - `feature-infrastructure.md`（Repository 実装が必要）
  - `feature-data-import.md`（データインポート後にチャートを表示）
  - `feature-project-list.md`（プロジェクト一覧から詳細画面に遷移）
- **依存元**：なし

---

## 7. Risks（リスク/懸念点）

実装時に想定されるリスクと、その軽減策を記述する。

### 7.1 技術的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| QWebEngineView のメモリ消費が大きい | 中 | チャートは 1 画面に 1 つのみ表示し、画面遷移で切り替える |
| 営業日カレンダーが未登録の場合の処理 | 中 | カレンダー日数で代替し、警告表示する（REQ-F-005 の例外処理に記載） |
| 大規模データ（工数実績 10 万件以上）でのチャート描画遅延 | 低 | 現在の想定（5000 件）では問題ないが、将来的にデータ集約を検討 |

### 7.2 仕様的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| 理想線の計算方法（均等消化）が実態に合わない可能性 | 低 | 要件定義で均等消化と明記されているため、その通り実装 |

---

## 8. Deliverables（成果物）

このプラン完了時点で生成されるファイル一覧。

### 8.1 実装ファイル

- `src/domain/value_objects/point.py`
- `src/domain/services/burndown_calculator.py`
- `src/application/dto/burndown_chart_dto.py`
- `src/application/usecases/get_burndown_chart_usecase.py`
- `src/presentation/viewmodels/project_detail_viewmodel.py`
- `src/presentation/views/project_detail_widget.py`
- `src/presentation/views/main_window.py`（拡張）

### 8.2 テストファイル

- `tests/domain/services/test_burndown_calculator.py`
- `tests/application/usecases/test_get_burndown_chart_usecase.py`
- `tests/presentation/viewmodels/test_project_detail_viewmodel.py`
- `tests/presentation/views/test_project_detail_widget.py`

---

## 9. Acceptance Criteria（受入条件）

このプランが「完了」と判断される条件を明確に記述する。

- [ ] すべてのタスクが完了している
- [ ] 横軸が営業日ベースの残日数、縦軸が残工数でチャートを表示すること
- [ ] 理想線（契約工数を営業日数で均等消化した線）と実績線を表示すること
- [ ] 現在日の位置が明確にわかること（マーカー、縦線など）
- [ ] 営業日カレンダーが未登録の場合はカレンダー日数で代替し、警告表示すること
- [ ] チャート描画時間が 3 秒以内であること（REQ-NF-002）
- [ ] プロジェクト一覧から詳細画面への遷移がワンクリックで可能であること
- [ ] 単体テストがすべて成功している（カバレッジ 80% 以上）
- [ ] 統合テストでチャート表示が正常動作すること
- [ ] コードレビューが完了している（ruff / mypy エラーなし）

---

## 10. Notes（備考）

実装時の注意事項や参考情報を記載する。

- チャートライブラリは plotly を使用（REQ-F-005 の備考に記載）
- 実績線の補間方法は直線補間（REQ-F-005 の備考に記載）
- QWebEngineView で plotly の HTML を表示する（ADR-002 の判断に従う）
- 営業日数計算は WorkdayCalendarRepository.is_workday() を使用
- 現在日マーカーは plotly の add_vline で実装
- plotly のインタラクティブ機能（ズーム、ホバー表示）はデフォルトで有効
