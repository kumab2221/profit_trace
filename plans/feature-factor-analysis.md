# Feature Plan: 工数余剰要因分析機能

## 1. Background（背景）

### 1.1 概要
- 工数が余剰している場合、他業務従事や長期休暇などの要因を推定し、提示する機能
- メンバー稼働状況と休日カレンダーを組み合わせて要因候補を分析する
- 関連する要求・要件：STK-007 → REQ-F-007

### 1.2 関連ドキュメント
- docs/requirements/02_system-requirements.md（REQ-F-007）
- docs/design/02_domain-design.md（FactorEstimator）
- docs/design/03_application-design.md（GetFactorAnalysisUseCase, FactorAnalysisDTO）
- docs/design/04_presentation-design.md（ProjectDetailWidget 拡張）
- ADR/ADR-002-mvvm-pattern.md

---

## 2. Objective（目的）

この機能の実装により達成すべき目標を **明確に** 記述する。

- **ユーザー視点での価値**: 工数余剰の要因候補が提示され、原因を迅速に特定できる
- **システム視点での価値**:
  - FactorEstimator により、要因推定ロジックが Domain 層に集約される
  - 信頼度を表示することで、推定精度を明示できる
  - 複数の要因候補を提示し、ユーザーの判断を支援できる
- **非機能要件の達成**:
  - REQ-NF-003（操作性）: 要因候補の提示形式が視覚的にわかりやすい
  - REQ-NF-008（安定性）: データ取得エラー時もクラッシュしない

---

## 3. Scope（スコープ）

### 3.1 In Scope（含む）
この実装計画で **実装する** 機能・タスクを列挙する。

- Domain 層の実装
  - FactorEstimator（工数余剰要因の推定）
  - Factor データクラス（要因候補）
- Application 層の実装
  - GetFactorAnalysisUseCase（要因分析の取得）
  - FactorAnalysisDTO（要因分析データの DTO）
- Presentation 層の実装
  - ProjectDetailWidget への要因分析セクション追加
  - 要因候補の表示（テキスト、リスト形式）
  - 信頼度の表示
- 単体テスト・統合テスト
  - FactorEstimator のテスト
  - GetFactorAnalysisUseCase のテスト

### 3.2 Out of Scope（含まない）
この実装計画で **実装しない** 機能・タスクを明示する。

- 機械学習モデルによる要因推定（理由：将来の拡張候補、現在は単純なルールベース）
- 要因の自動修正機能（理由：要件定義で不要）
- 要因候補のグラフ表示（理由：テキスト・リスト形式で十分）

---

## 4. Tasks（タスク一覧）

実装タスクを **1〜2 時間粒度** に分解し、以下の形式で列挙する。

### 4.1 Domain 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-FACT-001 | Factor データクラスの実装 | 要因候補を表す dataclass を実装（要因名、詳細、信頼度） | Domain | 0.5h | - | `src/domain/value_objects/factor.py` |
| TASK-FACT-002 | FactorEstimator の工数余剰検出実装 | 理想線と実績線の乖離から工数余剰を検出するロジックを実装 | Domain | 1.5h | TASK-FACT-001 | `src/domain/services/factor_estimator.py` |
| TASK-FACT-003 | FactorEstimator の要因推定実装 | メンバー稼働状況と営業日カレンダーから要因候補を推定するロジックを実装 | Domain | 2.5h | TASK-FACT-002 | `src/domain/services/factor_estimator.py`（拡張） |

### 4.2 Application 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-FACT-004 | FactorAnalysisDTO の実装 | 要因分析結果を Presentation 層に渡す DTO を実装 | Application | 0.5h | TASK-FACT-001 | `src/application/dto/factor_analysis_dto.py` |
| TASK-FACT-005 | GetFactorAnalysisUseCase の実装 | Repository からプロジェクト・工数実績・メンバー稼働・営業日カレンダーを取得し、FactorEstimator を呼び出して要因分析を生成 | Application | 2.0h | TASK-FACT-003, TASK-FACT-004 | `src/application/usecases/get_factor_analysis_usecase.py` |

### 4.3 Presentation 層タスク

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-FACT-006 | ProjectDetailViewModel の要因分析機能追加 | GetFactorAnalysisUseCase を呼び出し、Signal で View に通知 | Presentation | 1.5h | TASK-FACT-005 | `src/presentation/viewmodels/project_detail_viewmodel.py`（拡張） |
| TASK-FACT-007 | ProjectDetailWidget の要因分析セクション実装 | 要因候補をリスト形式で表示するセクションを追加 | Presentation | 2.0h | TASK-FACT-006 | `src/presentation/views/project_detail_widget.py`（拡張） |
| TASK-FACT-008 | 信頼度表示の実装 | 要因候補ごとに信頼度を表示するロジックを実装 | Presentation | 1.0h | TASK-FACT-007 | `src/presentation/views/project_detail_widget.py`（拡張） |

### 4.4 テストタスク（Testing）

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-FACT-009 | FactorEstimator 工数余剰検出のテスト | 工数余剰の検出ロジック（理想線と実績線の差分）のテスト | Domain | 1.0h | TASK-FACT-002 | `tests/domain/services/test_factor_estimator.py` |
| TASK-FACT-010 | FactorEstimator 要因推定のテスト | 要因候補の推定ロジック（他業務従事、長期休暇、未稼働）のテスト | Domain | 1.5h | TASK-FACT-003 | `tests/domain/services/test_factor_estimator.py`（拡張） |
| TASK-FACT-011 | GetFactorAnalysisUseCase のテスト | 要因分析取得〜DTO 変換までのテスト | Application | 1.5h | TASK-FACT-005 | `tests/application/usecases/test_get_factor_analysis_usecase.py` |
| TASK-FACT-012 | ProjectDetailWidget 要因分析表示のテスト | 要因候補の表示と信頼度表示のテスト | Presentation | 1.0h | TASK-FACT-008 | `tests/presentation/views/test_project_detail_widget.py`（拡張） |

---

## 5. Estimation（見積もり）

### 5.1 タスク別見積もり

| カテゴリ | タスク数 | 合計工数 |
|----------|---------|---------|
| Domain 層 | 3 | 4.5h |
| Application 層 | 2 | 2.5h |
| Presentation 層 | 3 | 4.5h |
| Testing | 4 | 5.0h |
| **合計** | **12** | **16.5h** |

### 5.2 スケジュール目安

- **開発期間**：4〜5 日（1 日 4〜5 時間作業想定）
- **マイルストーン**：
  - Day 1-2：Domain 層・Application 層完了
  - Day 3：Presentation 層完了
  - Day 4：テスト完了・統合確認
  - Day 5：バッファ（予備日）

---

## 6. Dependencies（依存関係）

### 6.1 外部依存

このプランの実装に必要な外部要素を列挙する。

- **ライブラリ**：`PySide6`、`pytest`、`pytest-qt`
- **環境**：Python 3.12、SQLite

### 6.2 内部依存

他のプラン・機能との依存関係を明示する。

- **依存先**：
  - `feature-infrastructure.md`（Repository 実装が必要）
  - `feature-data-import.md`（データインポート後に要因分析を実施）
  - `feature-burndown-chart.md`（バーンダウンチャート画面に要因分析を追加）
  - `feature-member-workload.md`（メンバー稼働状況を要因推定に使用）
- **依存元**：なし

---

## 7. Risks（リスク/懸念点）

実装時に想定されるリスクと、その軽減策を記述する。

### 7.1 技術的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| 要因推定の精度が低い | 中 | 信頼度を表示し、複数の要因候補を提示してユーザーの判断を支援 |
| 要因候補が多すぎて判断が困難 | 低 | 信頼度の高い候補のみを表示（例: 信頼度 50% 以上） |

### 7.2 仕様的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| 工数余剰の検出基準が不明確 | 中 | 要件定義書に「正確な数値で検出（理想線と実績線の差分を表示）」と記載されているため、その通り実装 |
| 要因推定ロジックの複雑化 | 中 | 単純なルールベースで実装し、将来的に機械学習モデル導入を検討 |

---

## 8. Deliverables（成果物）

このプラン完了時点で生成されるファイル一覧。

### 8.1 実装ファイル

- `src/domain/value_objects/factor.py`
- `src/domain/services/factor_estimator.py`
- `src/application/dto/factor_analysis_dto.py`
- `src/application/usecases/get_factor_analysis_usecase.py`
- `src/presentation/viewmodels/project_detail_viewmodel.py`（拡張）
- `src/presentation/views/project_detail_widget.py`（拡張）

### 8.2 テストファイル

- `tests/domain/services/test_factor_estimator.py`
- `tests/application/usecases/test_get_factor_analysis_usecase.py`
- `tests/presentation/views/test_project_detail_widget.py`（拡張）

---

## 9. Acceptance Criteria（受入条件）

このプランが「完了」と判断される条件を明確に記述する。

- [ ] すべてのタスクが完了している
- [ ] メンバー稼働状況と休日カレンダーを組み合わせて要因候補を提示できること
- [ ] 要因候補の提示形式（テキスト、リスト）が視覚的にわかりやすいこと
- [ ] 要因候補ごとに信頼度が表示されること
- [ ] 工数余剰の検出が正確な数値で行われること（理想線と実績線の差分）
- [ ] 単体テストがすべて成功している（カバレッジ 80% 以上）
- [ ] 統合テストで要因分析が正常動作すること
- [ ] コードレビューが完了している（ruff / mypy エラーなし）

---

## 10. Notes（備考）

実装時の注意事項や参考情報を記載する。

- 工数余剰の検出基準：正確な数値で検出（理想線と実績線の差分を表示）（REQ-F-007 の備考に記載）
- 要因候補の推定ロジック：信頼度を表示（REQ-F-007 の備考に記載）
- 要因候補の例：
  - メンバー A が他プロジェクト B に XX 時間使用
  - メンバー C が期間中 YY 日間未稼働（長期休暇の可能性）
  - 営業日の未稼働が ZZ 日間発生
- 将来的に機械学習モデルを使用した要因推定を検討（ADR-001 の将来拡張シナリオに記載）
