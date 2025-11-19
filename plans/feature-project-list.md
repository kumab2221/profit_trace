# Feature Plan: プロジェクト一覧機能

## 1. Background（背景）

### 1.1 概要
- 複数プロジェクトの工数消化状況を一覧表示し、問題の有無を迅速に判断できるようにする機能
- 各プロジェクトの消化率を計算し、遅延・余剰を視覚的に識別可能にする
- 関連する要求・要件：STK-001 → REQ-F-004

### 1.2 関連ドキュメント
- docs/requirements/02_system-requirements.md（REQ-F-004）
- docs/design/02_domain-design.md（ConsumptionRateCalculator）
- docs/design/03_application-design.md（GetProjectListUseCase, ProjectDTO）
- docs/design/04_presentation-design.md（ProjectListWidget, ProjectListViewModel）
- ADR/ADR-002-mvvm-pattern.md

---

## 2. Objective（目的）

この機能の実装により達成すべき目標を **明確に** 記述する。

- **ユーザー視点での価値**: プロジェクト一覧から各プロジェクトの消化率が一目でわかり、問題プロジェクトを迅速に特定できる
- **システム視点での価値**:
  - ConsumptionRateCalculator により、消化率計算ロジックが Domain 層に集約される
  - ProjectDTO により、Presentation 層と Domain 層が分離され、変更容易性が向上する
  - 色分け表示により、消化遅延・余剰が視覚的に判断可能になる
- **非機能要件の達成**:
  - REQ-NF-003（操作性）: ワンクリックで詳細画面への遷移が可能
  - REQ-NF-008（安定性）: データ取得エラー時もクラッシュせず、エラーダイアログを表示

---

## 3. Scope（スコープ）

### 3.1 In Scope（含む）
この実装計画で **実装する** 機能・タスクを列挙する。

- Domain 層の実装
  - ConsumptionRateCalculator（工数消化率計算）
- Application 層の実装
  - GetProjectListUseCase（プロジェクト一覧取得）
  - ProjectDTO（プロジェクト情報の DTO）
- Presentation 層の実装
  - ProjectListWidget（プロジェクト一覧画面）
  - ProjectListViewModel（データバインディング）
  - 色分け表示（正常 / 遅延 / 余剰）
  - 詳細画面への遷移
- 単体テスト・統合テスト
  - ConsumptionRateCalculator のテスト
  - GetProjectListUseCase のテスト
  - ProjectListViewModel のテスト

### 3.2 Out of Scope（含まない）
この実装計画で **実装しない** 機能・タスクを明示する。

- プロジェクト詳細画面（理由：feature-burndown-chart.md で対応）
- ソート機能・フィルタリング機能（理由：要件定義で不要と記載）
- データのエクスポート機能（理由：feature-report.md で対応）

---

## 4. Tasks（タスク一覧）

実装タスクを **1〜2 時間粒度** に分解し、以下の形式で列挙する。

### 4.1 Domain 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-PROJ-001 | ConsumptionRateCalculator の実装 | 消化済み工数と契約工数から消化率を計算するドメインサービスを実装 | Domain | 1.0h | - | `src/domain/services/consumption_rate_calculator.py` |

### 4.2 Application 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-PROJ-002 | ProjectDTO の実装 | プロジェクト情報を Presentation 層に渡す DTO を実装 | Application | 0.5h | - | `src/application/dto/project_dto.py` |
| TASK-PROJ-003 | GetProjectListUseCase の実装 | Repository から全プロジェクトと工数実績を取得し、消化率を計算して ProjectDTO に変換 | Application | 2.0h | TASK-PROJ-001, TASK-PROJ-002 | `src/application/usecases/get_project_list_usecase.py` |

### 4.3 Presentation 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-PROJ-004 | ProjectListViewModel の実装 | GetProjectListUseCase を呼び出し、Signal/Slot でデータバインディング | Presentation | 1.5h | TASK-PROJ-003 | `src/presentation/viewmodels/project_list_viewmodel.py` |
| TASK-PROJ-005 | ProjectListWidget の実装 | プロジェクト一覧を QTableWidget で表示、色分け表示を実装 | Presentation | 2.5h | TASK-PROJ-004 | `src/presentation/views/project_list_widget.py` |
| TASK-PROJ-006 | 詳細画面への遷移機能の実装 | プロジェクトをクリックすると詳細画面（バーンダウンチャート）に遷移 | Presentation | 1.0h | TASK-PROJ-005 | `src/presentation/views/project_list_widget.py`（拡張） |
| TASK-PROJ-007 | MainWindow への統合 | メイン画面に ProjectListWidget を追加し、画面遷移を実装 | Presentation | 1.0h | TASK-PROJ-006 | `src/presentation/views/main_window.py`（拡張） |

### 4.4 テストタスク（Testing）

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-PROJ-008 | ConsumptionRateCalculator のテスト | 消化率計算ロジック（正常系・異常系）のテスト | Domain | 1.0h | TASK-PROJ-001 | `tests/domain/services/test_consumption_rate_calculator.py` |
| TASK-PROJ-009 | GetProjectListUseCase のテスト | プロジェクト一覧取得とステータス判定（正常 / 遅延 / 余剰）のテスト | Application | 1.5h | TASK-PROJ-003 | `tests/application/usecases/test_get_project_list_usecase.py` |
| TASK-PROJ-010 | ProjectListViewModel のテスト | Signal/Slot の発火タイミング、エラーハンドリングのテスト | Presentation | 1.0h | TASK-PROJ-004 | `tests/presentation/viewmodels/test_project_list_viewmodel.py` |
| TASK-PROJ-011 | ProjectListWidget の統合テスト | プロジェクト一覧表示〜詳細画面遷移までの一連の流れをテスト | Presentation | 1.5h | TASK-PROJ-007 | `tests/presentation/views/test_project_list_widget.py` |

---

## 5. Estimation（見積もり）

### 5.1 タスク別見積もり

| カテゴリ | タスク数 | 合計工数 |
|----------|---------|---------|
| Domain 層 | 1 | 1.0h |
| Application 層 | 2 | 2.5h |
| Presentation 層 | 4 | 6.0h |
| Testing | 4 | 5.0h |
| **合計** | **11** | **14.5h** |

### 5.2 スケジュール目安

- **開発期間**：3〜4 日（1 日 4〜5 時間作業想定）
- **マイルストーン**：
  - Day 1：Domain 層・Application 層完了
  - Day 2：Presentation 層完了
  - Day 3：テスト完了・統合確認
  - Day 4：バッファ（予備日）

---

## 6. Dependencies（依存関係）

### 6.1 外部依存

このプランの実装に必要な外部要素を列挙する。

- **ライブラリ**：`PySide6`（QTableWidget）、`pytest`、`pytest-qt`
- **環境**：Python 3.12、SQLite

### 6.2 内部依存

他のプラン・機能との依存関係を明示する。

- **依存先**：
  - `feature-infrastructure.md`（Repository 実装が必要）
  - `feature-data-import.md`（データインポート後にプロジェクト一覧を表示）
- **依存元**：`feature-burndown-chart.md`（プロジェクト一覧から詳細画面に遷移）

---

## 7. Risks（リスク/懸念点）

実装時に想定されるリスクと、その軽減策を記述する。

### 7.1 技術的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| プロジェクト数が多い場合の表示遅延 | 中 | Repository のクエリを最適化し、インデックスを活用 |
| 色分け表示のカラーリングが見づらい | 低 | ユーザーフィードバックを元に調整 |

### 7.2 仕様的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| 消化遅延・余剰の判定基準（±5%）が曖昧 | 中 | 要件定義書に明記されているため、その通り実装 |
| ソート機能の要望が出る可能性 | 低 | 要件定義で不要と明記されているが、将来の拡張候補として記録 |

---

## 8. Deliverables（成果物）

このプラン完了時点で生成されるファイル一覧。

### 8.1 実装ファイル

- `src/domain/services/consumption_rate_calculator.py`
- `src/application/dto/project_dto.py`
- `src/application/usecases/get_project_list_usecase.py`
- `src/presentation/viewmodels/project_list_viewmodel.py`
- `src/presentation/views/project_list_widget.py`
- `src/presentation/views/main_window.py`（拡張）

### 8.2 テストファイル

- `tests/domain/services/test_consumption_rate_calculator.py`
- `tests/application/usecases/test_get_project_list_usecase.py`
- `tests/presentation/viewmodels/test_project_list_viewmodel.py`
- `tests/presentation/views/test_project_list_widget.py`

---

## 9. Acceptance Criteria（受入条件）

このプランが「完了」と判断される条件を明確に記述する。

- [ ] すべてのタスクが完了している
- [ ] プロジェクト一覧画面から各プロジェクトの消化率が視覚的に判断できること
- [ ] 問題のあるプロジェクト（消化遅延・余剰）が色分け表示されること
- [ ] プロジェクト一覧から詳細画面（バーンダウンチャート）への遷移がワンクリックで可能であること
- [ ] データ取得エラー時にエラーダイアログが表示され、アプリがクラッシュしないこと
- [ ] 単体テストがすべて成功している（カバレッジ 80% 以上）
- [ ] 統合テストでプロジェクト一覧表示〜詳細画面遷移が正常動作すること
- [ ] コードレビューが完了している（ruff / mypy エラーなし）

---

## 10. Notes（備考）

実装時の注意事項や参考情報を記載する。

- 色分け表示は QTableWidget の setItem で QTableWidgetItem の背景色を設定する
- 消化遅延・余剰の判定基準は理想線から ±5%（REQ-F-004 の備考に記載）
- プロジェクト一覧のソート順はプロジェクト名の昇順（デフォルト）
- 詳細画面への遷移は QTableWidget の itemClicked Signal を使用
- MVVM パターンに従い、View はビジネスロジックを持たず、ViewModel 経由で Application 層を呼び出す
