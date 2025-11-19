# Feature Plan: メンバー稼働状況機能

## 1. Background（背景）

### 1.1 概要
- メンバー単位で工数使用状況を表示し、他業務従事や長期休暇の可能性を判断できるようにする機能
- 期間内の工数使用量、複数プロジェクトへの配分状況、未稼働期間を可視化する
- 関連する要求・要件：STK-006 → REQ-F-006

### 1.2 関連ドキュメント
- docs/requirements/02_system-requirements.md（REQ-F-006, REQ-NF-002）
- docs/design/02_domain-design.md（WorkloadAnalyzer）
- docs/design/03_application-design.md（GetMemberWorkloadUseCase, MemberWorkloadDTO）
- docs/design/04_presentation-design.md（MemberWorkloadWidget, MemberWorkloadViewModel）
- ADR/ADR-002-mvvm-pattern.md

---

## 2. Objective（目的）

この機能の実装により達成すべき目標を **明確に** 記述する。

- **ユーザー視点での価値**: メンバー単位で工数の使用状況を把握し、他業務従事や長期休暇を判断できる
- **システム視点での価値**:
  - WorkloadAnalyzer により、稼働分析ロジックが Domain 層に集約される
  - 積み上げ棒グラフにより、複数プロジェクトへの配分状況が視覚的にわかる
  - 営業日カレンダーと照合し、未稼働期間を強調表示できる
- **非機能要件の達成**:
  - REQ-NF-002（パフォーマンス）: メンバー稼働状況グラフの描画時間が 5 秒以内
  - REQ-NF-003（操作性）: 未稼働期間が視覚的にわかる

---

## 3. Scope（スコープ）

### 3.1 In Scope（含む）
この実装計画で **実装する** 機能・タスクを列挙する。

- Domain 層の実装
  - WorkloadAnalyzer（メンバー別稼働状況の分析）
  - WorkloadAnalysis データクラス（分析結果）
- Application 層の実装
  - GetMemberWorkloadUseCase（メンバー別稼働状況の取得）
  - MemberWorkloadDTO（稼働状況データの DTO）
- Presentation 層の実装
  - MemberWorkloadWidget（メンバー稼働状況画面）
  - MemberWorkloadViewModel（データバインディング）
  - 積み上げ棒グラフ（plotly）
  - 未稼働期間の強調表示
- 単体テスト・統合テスト
  - WorkloadAnalyzer のテスト
  - GetMemberWorkloadUseCase のテスト
  - MemberWorkloadViewModel のテスト

### 3.2 Out of Scope（含まない）
この実装計画で **実装しない** 機能・タスクを明示する。

- 工数余剰要因の推定（理由：feature-factor-analysis.md で対応）
- レポートのエクスポート（理由：feature-report.md で対応）
- メンバーマスタの管理（理由：要件定義で不要）

---

## 4. Tasks（タスク一覧）

実装タスクを **1〜2 時間粒度** に分解し、以下の形式で列挙する。

### 4.1 Domain 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-WORK-001 | WorkloadAnalysis データクラスの実装 | 稼働分析結果を表す dataclass を実装（総工数、プロジェクト別配分、未稼働期間） | Domain | 0.5h | - | `src/domain/value_objects/workload_analysis.py` |
| TASK-WORK-002 | WorkloadAnalyzer の実装 | メンバー別の工数実績を集計し、未稼働期間を検出するドメインサービスを実装 | Domain | 2.5h | TASK-WORK-001 | `src/domain/services/workload_analyzer.py` |

### 4.2 Application 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-WORK-003 | MemberWorkloadDTO の実装 | メンバー別稼働状況を Presentation 層に渡す DTO を実装 | Application | 0.5h | TASK-WORK-001 | `src/application/dto/member_workload_dto.py` |
| TASK-WORK-004 | GetMemberWorkloadUseCase の実装 | Repository からメンバー・工数実績・営業日カレンダーを取得し、WorkloadAnalyzer を呼び出して稼働状況を生成 | Application | 2.0h | TASK-WORK-002, TASK-WORK-003 | `src/application/usecases/get_member_workload_usecase.py` |

### 4.3 Presentation 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-WORK-005 | MemberWorkloadViewModel の実装 | GetMemberWorkloadUseCase を呼び出し、plotly の JSON 形式に変換して Signal で View に通知 | Presentation | 2.0h | TASK-WORK-004 | `src/presentation/viewmodels/member_workload_viewmodel.py` |
| TASK-WORK-006 | MemberWorkloadWidget の実装 | QWebEngineView で積み上げ棒グラフを表示する画面を実装 | Presentation | 2.5h | TASK-WORK-005 | `src/presentation/views/member_workload_widget.py` |
| TASK-WORK-007 | plotly 積み上げ棒グラフ生成ロジックの実装 | プロジェクト別配分状況を積み上げ棒グラフで描画するロジックを実装 | Presentation | 2.0h | TASK-WORK-006 | `src/presentation/views/member_workload_widget.py`（拡張） |
| TASK-WORK-008 | 未稼働期間の強調表示の実装 | 営業日の未稼働期間を色分けで表示するロジックを実装 | Presentation | 1.5h | TASK-WORK-007 | `src/presentation/views/member_workload_widget.py`（拡張） |
| TASK-WORK-009 | MainWindow への統合 | メニューに「メンバー稼働状況」を追加し、画面遷移を実装 | Presentation | 1.0h | TASK-WORK-008 | `src/presentation/views/main_window.py`（拡張） |

### 4.4 テストタスク（Testing）

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-WORK-010 | WorkloadAnalyzer のテスト | 工数集計、未稼働期間検出ロジックのテスト | Domain | 1.5h | TASK-WORK-002 | `tests/domain/services/test_workload_analyzer.py` |
| TASK-WORK-011 | GetMemberWorkloadUseCase のテスト | 稼働状況取得〜DTO 変換までのテスト | Application | 1.5h | TASK-WORK-004 | `tests/application/usecases/test_get_member_workload_usecase.py` |
| TASK-WORK-012 | MemberWorkloadViewModel のテスト | Signal/Slot の発火タイミング、エラーハンドリングのテスト | Presentation | 1.0h | TASK-WORK-005 | `tests/presentation/viewmodels/test_member_workload_viewmodel.py` |
| TASK-WORK-013 | MemberWorkloadWidget の統合テスト | グラフ表示〜画面遷移までの一連の流れをテスト | Presentation | 1.5h | TASK-WORK-009 | `tests/presentation/views/test_member_workload_widget.py` |

---

## 5. Estimation（見積もり）

### 5.1 タスク別見積もり

| カテゴリ | タスク数 | 合計工数 |
|----------|---------|---------|
| Domain 層 | 2 | 3.0h |
| Application 層 | 2 | 2.5h |
| Presentation 層 | 5 | 9.0h |
| Testing | 4 | 5.5h |
| **合計** | **13** | **20.0h** |

### 5.2 スケジュール目安

- **開発期間**：4〜5 日（1 日 4〜5 時間作業想定）
- **マイルストーン**：
  - Day 1：Domain 層・Application 層完了
  - Day 2-3：Presentation 層完了
  - Day 4：テスト完了・統合確認
  - Day 5：バッファ（予備日）

---

## 6. Dependencies（依存関係）

### 6.1 外部依存

このプランの実装に必要な外部要素を列挙する。

- **ライブラリ**：`plotly`（積み上げ棒グラフ）、`PySide6`（QWebEngineView）、`pytest`、`pytest-qt`
- **環境**：Python 3.12、SQLite

### 6.2 内部依存

他のプラン・機能との依存関係を明示する。

- **依存先**：
  - `feature-infrastructure.md`（Repository 実装が必要）
  - `feature-data-import.md`（データインポート後に稼働状況を表示）
- **依存元**：`feature-factor-analysis.md`（稼働状況から要因分析を行う）

---

## 7. Risks（リスク/懸念点）

実装時に想定されるリスクと、その軽減策を記述する。

### 7.1 技術的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| メンバー数が多い場合の表示遅延 | 中 | Repository のクエリを最適化し、インデックスを活用 |
| QWebEngineView のメモリ消費 | 中 | チャートは 1 画面に 1 つのみ表示 |

### 7.2 仕様的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| 表示粒度（月次）が粗すぎる可能性 | 低 | 要件定義で月次と明記されているため、その通り実装 |
| 未稼働理由の推定精度 | 中 | 営業日カレンダーから推定し、信頼度を表示 |

---

## 8. Deliverables（成果物）

このプラン完了時点で生成されるファイル一覧。

### 8.1 実装ファイル

- `src/domain/value_objects/workload_analysis.py`
- `src/domain/services/workload_analyzer.py`
- `src/application/dto/member_workload_dto.py`
- `src/application/usecases/get_member_workload_usecase.py`
- `src/presentation/viewmodels/member_workload_viewmodel.py`
- `src/presentation/views/member_workload_widget.py`
- `src/presentation/views/main_window.py`（拡張）

### 8.2 テストファイル

- `tests/domain/services/test_workload_analyzer.py`
- `tests/application/usecases/test_get_member_workload_usecase.py`
- `tests/presentation/viewmodels/test_member_workload_viewmodel.py`
- `tests/presentation/views/test_member_workload_widget.py`

---

## 9. Acceptance Criteria（受入条件）

このプランが「完了」と判断される条件を明確に記述する。

- [ ] すべてのタスクが完了している
- [ ] メンバー単位で、期間内の工数使用量を表示できること
- [ ] 複数プロジェクトへの配分状況が積み上げ棒グラフで確認できること
- [ ] 未稼働期間が視覚的にわかること（色分け表示）
- [ ] メンバー稼働状況グラフの描画時間が 5 秒以内であること（REQ-NF-002）
- [ ] 単体テストがすべて成功している（カバレッジ 80% 以上）
- [ ] 統合テストでグラフ表示が正常動作すること
- [ ] コードレビューが完了している（ruff / mypy エラーなし）

---

## 10. Notes（備考）

実装時の注意事項や参考情報を記載する。

- 表示粒度は月次（REQ-F-006 の備考に記載）
- 可視化形式は積み上げ棒グラフ（REQ-F-006 の備考に記載）
- QWebEngineView で plotly の HTML を表示する
- 未稼働期間の検出は営業日カレンダーと照合する
- メンバー名のマスタ管理は不要（REQ-F-002 の備考に記載）
