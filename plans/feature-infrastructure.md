# Feature Plan: 基盤機能（Infrastructure & Domain）

## 1. Background（背景）

### 1.1 概要
- Profit Trace の全機能を支える基盤として、Domain 層と Infrastructure 層の実装が必要
- Domain 層にエンティティとビジネスロジックを集約し、Infrastructure 層でデータ永続化を実現する
- 関連する要求・要件：全機能の前提となる基盤（REQ-F-001〜REQ-F-009の前提）

### 1.2 関連ドキュメント
- docs/requirements/02_system-requirements.md（全セクション）
- docs/design/02_domain-design.md
- docs/design/05_infrastructure-design.md
- ADR/ADR-001-ddd-lite-monolith.md
- ADR/ADR-003-sqlite-cache-strategy.md
- ADR/ADR-004-repository-pattern.md

---

## 2. Objective（目的）

この機能の実装により達成すべき目標を **明確に** 記述する。

- **ユーザー視点での価値**: 全機能の基盤が整備され、データの永続化と取得が安定動作する
- **システム視点での価値**:
  - Domain 層のビジネスロジックが Infrastructure 層から独立し、テスト容易性が向上する
  - Repository パターンにより、データストアの変更が容易になる
  - SQLite のパフォーマンス最適化（インデックス）により、データ読み込み時間が要件を満たす
- **非機能要件の達成**:
  - REQ-NF-004（保守性）: レイヤー分離により変更容易性が向上
  - REQ-NF-008（テスト容易性）: Repository のモック化により単体テストが容易

---

## 3. Scope（スコープ）

### 3.1 In Scope（含む）
この実装計画で **実装する** 機能・タスクを列挙する。

- Domain 層の実装
  - エンティティ（Project, WorkRecord, WorkdayCalendar, Member）
  - Repository インターフェース（ProjectRepository, WorkRecordRepository, WorkdayCalendarRepository, MemberRepository）
  - ドメインサービスの基盤（BurndownCalculator, ConsumptionRateCalculator, WorkloadAnalyzer, FactorEstimator）
- Infrastructure 層の実装
  - SQLite データベースの初期化（テーブル作成、インデックス作成）
  - Repository 実装（ProjectRepositoryImpl, WorkRecordRepositoryImpl, WorkdayCalendarRepositoryImpl, MemberRepositoryImpl）
  - CSV/JSON Reader/Writer（CSVReader, JSONReader, CSVWriter, JSONWriter）
  - ログ設定（logging モジュール）
- 単体テスト
  - エンティティのバリデーションテスト
  - Repository のモックテスト

### 3.2 Out of Scope（含まない）
この実装計画で **実装しない** 機能・タスクを明示する。

- Application 層の実装（理由：別プラン feature-data-import.md で対応）
- Presentation 層の実装（理由：各画面機能のプランで対応）
- ドメインサービスの詳細ロジック実装（理由：各機能のプランで対応）
- CSV/JSON のフォーマットバリデーション（理由：Application 層で対応）

---

## 4. Tasks（タスク一覧）

実装タスクを **1〜2 時間粒度** に分解し、以下の形式で列挙する。

### 4.1 基盤タスク（Infrastructure / Domain）

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-INFRA-001 | プロジェクト構造の作成 | src/ 配下に domain, application, infrastructure, presentation ディレクトリを作成 | 全般 | 0.5h | - | `src/domain/`, `src/application/`, `src/infrastructure/`, `src/presentation/` |
| TASK-INFRA-002 | Project エンティティの実装 | プロジェクト契約情報を表すエンティティを dataclass で実装、バリデーションロジックを含む | Domain | 1.0h | TASK-INFRA-001 | `src/domain/entities/project.py` |
| TASK-INFRA-003 | WorkRecord エンティティの実装 | 工数実績データを表すエンティティを dataclass で実装、バリデーションロジックを含む | Domain | 1.0h | TASK-INFRA-001 | `src/domain/entities/work_record.py` |
| TASK-INFRA-004 | WorkdayCalendar エンティティの実装 | 営業日カレンダーを表すエンティティを dataclass で実装、バリデーションロジックを含む | Domain | 0.5h | TASK-INFRA-001 | `src/domain/entities/workday_calendar.py` |
| TASK-INFRA-005 | Member エンティティの実装 | メンバー情報を表すエンティティを dataclass で実装、バリデーションロジックを含む | Domain | 0.5h | TASK-INFRA-001 | `src/domain/entities/member.py` |
| TASK-INFRA-006 | ProjectRepository インターフェースの定義 | Project エンティティの永続化インターフェースを abc.ABC で定義 | Domain | 0.5h | TASK-INFRA-002 | `src/domain/repositories/project_repository.py` |
| TASK-INFRA-007 | WorkRecordRepository インターフェースの定義 | WorkRecord エンティティの永続化インターフェースを abc.ABC で定義 | Domain | 0.5h | TASK-INFRA-003 | `src/domain/repositories/work_record_repository.py` |
| TASK-INFRA-008 | WorkdayCalendarRepository インターフェースの定義 | WorkdayCalendar エンティティの永続化インターフェースを abc.ABC で定義 | Domain | 0.5h | TASK-INFRA-004 | `src/domain/repositories/workday_calendar_repository.py` |
| TASK-INFRA-009 | MemberRepository インターフェースの定義 | Member エンティティの永続化インターフェースを abc.ABC で定義 | Domain | 0.5h | TASK-INFRA-005 | `src/domain/repositories/member_repository.py` |
| TASK-INFRA-010 | DatabaseInitializer の実装 | SQLite のテーブル作成・インデックス作成を行う初期化クラスを実装 | Infrastructure | 1.5h | TASK-INFRA-001 | `src/infrastructure/database/initializer.py` |
| TASK-INFRA-011 | ProjectRepositoryImpl の実装 | ProjectRepository インターフェースの SQLite 実装、pandas.read_sql を使用 | Infrastructure | 2.0h | TASK-INFRA-006, TASK-INFRA-010 | `src/infrastructure/repositories/project_repository_impl.py` |
| TASK-INFRA-012 | WorkRecordRepositoryImpl の実装 | WorkRecordRepository インターフェースの SQLite 実装、pandas.read_sql を使用 | Infrastructure | 2.5h | TASK-INFRA-007, TASK-INFRA-010 | `src/infrastructure/repositories/work_record_repository_impl.py` |
| TASK-INFRA-013 | WorkdayCalendarRepositoryImpl の実装 | WorkdayCalendarRepository インターフェースの SQLite 実装、pandas.read_sql を使用 | Infrastructure | 2.0h | TASK-INFRA-008, TASK-INFRA-010 | `src/infrastructure/repositories/workday_calendar_repository_impl.py` |
| TASK-INFRA-014 | MemberRepositoryImpl の実装 | MemberRepository インターフェースの SQLite 実装、pandas.read_sql を使用 | Infrastructure | 1.5h | TASK-INFRA-009, TASK-INFRA-010 | `src/infrastructure/repositories/member_repository_impl.py` |
| TASK-INFRA-015 | CSVReader の実装 | CSV ファイルを pandas で読み込むクラスを実装 | Infrastructure | 1.0h | TASK-INFRA-001 | `src/infrastructure/file_io/csv_reader.py` |
| TASK-INFRA-016 | JSONReader の実装 | JSON ファイルを json モジュールで読み込むクラスを実装 | Infrastructure | 0.5h | TASK-INFRA-001 | `src/infrastructure/file_io/json_reader.py` |
| TASK-INFRA-017 | CSVWriter の実装 | DataFrame を CSV ファイルに書き込むクラスを実装（エクスポート機能） | Infrastructure | 1.0h | TASK-INFRA-001 | `src/infrastructure/file_io/csv_writer.py` |
| TASK-INFRA-018 | JSONWriter の実装 | dict を JSON ファイルに書き込むクラスを実装（エクスポート機能） | Infrastructure | 0.5h | TASK-INFRA-001 | `src/infrastructure/file_io/json_writer.py` |
| TASK-INFRA-019 | ログ設定の実装 | logging モジュールを使用してログ設定を行う setup_logging 関数を実装 | Infrastructure | 1.0h | TASK-INFRA-001 | `src/infrastructure/logging/logger.py` |

### 4.2 テストタスク（Testing）

| ID | タスク名 | 説明 | レイヤ | 見積 | 依存 | 成果物 |
|----|---------|------|--------|------|------|--------|
| TASK-INFRA-020 | Project エンティティの単体テスト | バリデーションロジック（contracted_hours > 0, start_date < end_date）のテスト | Domain | 1.0h | TASK-INFRA-002 | `tests/domain/entities/test_project.py` |
| TASK-INFRA-021 | WorkRecord エンティティの単体テスト | バリデーションロジック（hours >= 0, member_name not empty）のテスト | Domain | 1.0h | TASK-INFRA-003 | `tests/domain/entities/test_work_record.py` |
| TASK-INFRA-022 | WorkdayCalendar エンティティの単体テスト | バリデーションロジック（year_month 形式、day 範囲）のテスト | Domain | 0.5h | TASK-INFRA-004 | `tests/domain/entities/test_workday_calendar.py` |
| TASK-INFRA-023 | Member エンティティの単体テスト | バリデーションロジック（member_name not empty）のテスト | Domain | 0.5h | TASK-INFRA-005 | `tests/domain/entities/test_member.py` |
| TASK-INFRA-024 | ProjectRepositoryImpl の統合テスト | SQLite への保存・取得・削除をテスト（テスト用 DB を使用） | Infrastructure | 1.5h | TASK-INFRA-011 | `tests/infrastructure/repositories/test_project_repository_impl.py` |
| TASK-INFRA-025 | WorkRecordRepositoryImpl の統合テスト | SQLite への一括保存・検索（プロジェクト名、メンバー名、日付範囲）をテスト | Infrastructure | 2.0h | TASK-INFRA-012 | `tests/infrastructure/repositories/test_work_record_repository_impl.py` |
| TASK-INFRA-026 | WorkdayCalendarRepositoryImpl の統合テスト | SQLite への保存・営業日判定（is_workday）をテスト | Infrastructure | 1.5h | TASK-INFRA-013 | `tests/infrastructure/repositories/test_workday_calendar_repository_impl.py` |
| TASK-INFRA-027 | MemberRepositoryImpl の統合テスト | SQLite への保存・取得をテスト | Infrastructure | 1.0h | TASK-INFRA-014 | `tests/infrastructure/repositories/test_member_repository_impl.py` |
| TASK-INFRA-028 | CSVReader の単体テスト | CSV ファイル読み込み（正常系・異常系）のテスト | Infrastructure | 1.0h | TASK-INFRA-015 | `tests/infrastructure/file_io/test_csv_reader.py` |
| TASK-INFRA-029 | JSONReader の単体テスト | JSON ファイル読み込み（正常系・異常系）のテスト | Infrastructure | 0.5h | TASK-INFRA-016 | `tests/infrastructure/file_io/test_json_reader.py` |

---

## 5. Estimation（見積もり）

### 5.1 タスク別見積もり

| カテゴリ | タスク数 | 合計工数 |
|----------|---------|---------|
| Domain（エンティティ・Repository インターフェース） | 9 | 5.5h |
| Infrastructure（Repository 実装、File I/O、DB 初期化） | 10 | 13.5h |
| Testing | 10 | 10.5h |
| **合計** | **29** | **29.5h** |

### 5.2 スケジュール目安

- **開発期間**：6〜7 日（1 日 4〜5 時間作業想定）
- **マイルストーン**：
  - Day 1-2：Domain 層完了（エンティティ、Repository インターフェース）
  - Day 3-4：Infrastructure 層完了（Repository 実装、File I/O）
  - Day 5-6：テスト完了・統合確認
  - Day 7：バッファ（予備日）

---

## 6. Dependencies（依存関係）

### 6.1 外部依存

このプランの実装に必要な外部要素を列挙する。

- **ライブラリ**：
  - `pandas`（CSV パース、DataFrame 操作）
  - `pytest`（テスト用）
  - `sqlite3`（Python 標準ライブラリ、SQLite アクセス）
- **ファイル**：サンプル CSV/JSON ファイル（テスト用）
- **環境**：Python 3.12、SQLite

### 6.2 内部依存

他のプラン・機能との依存関係を明示する。

- **依存先**：なし（このプランが最初に実装される）
- **依存元**：
  - `feature-data-import.md`（データインポート機能が Repository 実装を使用）
  - `feature-project-list.md`（プロジェクト一覧画面が Repository 実装を使用）
  - `feature-burndown-chart.md`（バーンダウンチャートが Repository 実装とドメインサービスを使用）
  - `feature-member-workload.md`（メンバー稼働状況が Repository 実装とドメインサービスを使用）
  - `feature-factor-analysis.md`（要因分析が Repository 実装とドメインサービスを使用）
  - `feature-report.md`（レポート機能が Repository 実装とドメインサービスを使用）

---

## 7. Risks（リスク/懸念点）

実装時に想定されるリスクと、その軽減策を記述する。

### 7.1 技術的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| SQLite のパフォーマンス低下（大規模データ） | 中 | インデックスを適切に設定し、クエリを最適化。将来的に PostgreSQL 移行を検討 |
| pandas.read_sql のメモリ消費増加 | 低 | 現在の想定（工数実績 5000 件）では問題ないが、将来的にチャンク読み込みを検討 |
| Repository の粒度設計ミス | 中 | エンティティ単位で Repository を作成し、複雑なクエリは専用メソッドを追加 |
| エンティティのバリデーション不足 | 高 | 単体テストで網羅的にバリデーションロジックをテスト |

### 7.2 仕様的リスク

| リスク | 影響度 | 軽減策 |
|--------|--------|--------|
| Domain 層へのビジネスロジック集約不足 | 高 | コーディング規約で「Domain 層以外にビジネスロジックを書かない」を明文化、コードレビューで確認 |
| Repository インターフェースの肥大化 | 中 | Repository は CRUD 操作と基本的な検索のみに責務を限定、複雑な集計はドメインサービスに委譲 |

---

## 8. Deliverables（成果物）

このプラン完了時点で生成されるファイル一覧。

### 8.1 実装ファイル

**Domain 層**
- `src/domain/entities/project.py`
- `src/domain/entities/work_record.py`
- `src/domain/entities/workday_calendar.py`
- `src/domain/entities/member.py`
- `src/domain/repositories/project_repository.py`
- `src/domain/repositories/work_record_repository.py`
- `src/domain/repositories/workday_calendar_repository.py`
- `src/domain/repositories/member_repository.py`

**Infrastructure 層**
- `src/infrastructure/database/initializer.py`
- `src/infrastructure/repositories/project_repository_impl.py`
- `src/infrastructure/repositories/work_record_repository_impl.py`
- `src/infrastructure/repositories/workday_calendar_repository_impl.py`
- `src/infrastructure/repositories/member_repository_impl.py`
- `src/infrastructure/file_io/csv_reader.py`
- `src/infrastructure/file_io/json_reader.py`
- `src/infrastructure/file_io/csv_writer.py`
- `src/infrastructure/file_io/json_writer.py`
- `src/infrastructure/logging/logger.py`

### 8.2 テストファイル

- `tests/domain/entities/test_project.py`
- `tests/domain/entities/test_work_record.py`
- `tests/domain/entities/test_workday_calendar.py`
- `tests/domain/entities/test_member.py`
- `tests/infrastructure/repositories/test_project_repository_impl.py`
- `tests/infrastructure/repositories/test_work_record_repository_impl.py`
- `tests/infrastructure/repositories/test_workday_calendar_repository_impl.py`
- `tests/infrastructure/repositories/test_member_repository_impl.py`
- `tests/infrastructure/file_io/test_csv_reader.py`
- `tests/infrastructure/file_io/test_json_reader.py`

### 8.3 ドキュメント

- なし（設計書は既存）

---

## 9. Acceptance Criteria（受入条件）

このプランが「完了」と判断される条件を明確に記述する。

- [ ] すべてのタスクが完了している
- [ ] Domain 層のエンティティが dataclass で実装され、バリデーションロジックが含まれている
- [ ] Domain 層の Repository インターフェースが abc.ABC で定義されている
- [ ] Infrastructure 層の Repository 実装が pandas.read_sql を使用して実装されている
- [ ] SQLite のテーブルとインデックスが正しく作成される
- [ ] CSV/JSON Reader/Writer が正常に動作する
- [ ] 単体テストがすべて成功している（カバレッジ 80% 以上）
- [ ] 統合テストで Repository 実装が正常動作する
- [ ] コードレビューが完了している（ruff / mypy エラーなし）
- [ ] ログ設定が正常に動作し、ログファイルが生成される

---

## 10. Notes（備考）

実装時の注意事項や参考情報を記載する。

- エンティティは dataclass を使用し、`__post_init__` でバリデーションを実装する
- Repository インターフェースは abc.ABC を継承し、@abstractmethod で抽象メソッドを定義する
- Repository 実装は pandas.read_sql を使用して SQLite からデータを取得し、DataFrame をエンティティに変換する
- CSV/JSON Reader は pandas.read_csv と json.load を使用する
- ログ設定は logging モジュールを使用し、ファイルハンドラとストリームハンドラの両方を設定する
- テストは pytest を使用し、テスト用の SQLite データベースは :memory: または一時ファイルを使用する
- ADR-001, ADR-003, ADR-004 の方針を遵守する
