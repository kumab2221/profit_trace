# ADR-004: Repository パターンによる層間依存性管理

## Status
Accepted

## Context
- DDD Lite Monolith アーキテクチャにおいて Domain 層と Infrastructure 層の依存関係を管理する必要がある
- 関連要件: REQ-NF-004（保守性）、REQ-NF-008（テスト容易性）
- Domain 層のビジネスロジックを Infrastructure 層の実装詳細（SQLite の SQL クエリ等）から分離する必要がある
- テスト時に Infrastructure 層をモックに差し替え可能にし、テストカバレッジ 80% 以上の品質基準を維持する必要がある
- 将来の Infrastructure 層の変更（SQLite → PostgreSQL、CSV → API 連携）が Domain 層に影響しないようにする必要がある

## Decision
- Repository パターンを採用し、Repository インターフェースを Domain 層で定義する
- Infrastructure 層で Repository インターフェースを実装する（ProjectRepository, WorkRecordRepository, WorkdayCalendarRepository）
- Application 層は Repository インターフェース経由でのみデータにアクセスする
- 依存性逆転の原則を適用し、Domain 層は Infrastructure 層に依存しない
- Repository の実装は ORM を使用せず、生 SQL または pandas.read_sql で実装する

## Alternatives
- **Application 層が直接 SQLite にアクセス**: Repository の抽象化を行わず、Application 層で直接 SQLite にアクセスする。実装がシンプルだが、テスト時に SQLite のモックが困難になり、Infrastructure 層の変更が Application 層に影響する。
- **ORM（SQLAlchemy 等）を使用**: Repository の実装に ORM を使用し、SQL クエリの記述を抽象化する。学習コストと実行時オーバーヘッドが増加し、小規模データ（プロジェクト 50 件、工数実績 5000 件）では利点が少ない。
- **CQRS（Command Query Responsibility Segregation）**: 読み取りと書き込みの責務を分離する。本プロジェクトは読み取り中心（バーンダウンチャート、メンバー稼働状況の表示）であり、書き込み処理は CSV インポート時のみのため、過剰な抽象化となる。

## Rationale
- Repository インターフェースを Domain 層で定義することで、依存性逆転の原則を実現し、Domain 層を Infrastructure 層から独立させる
- テスト時に Repository をモックに差し替えることで、Domain 層と Application 層の単体テストが容易になる
- Infrastructure 層の変更（SQLite → PostgreSQL）が Repository 実装のみで完結し、Domain 層や Application 層に影響しない
- ORM を使用しないことで、学習コストと実行時オーバーヘッドを抑制し、小規模チーム（1〜3名）での実装効率を維持する
- pandas.read_sql を使用することで、SQLite から DataFrame への変換が容易になり、集計処理の実装が簡潔になる

## Consequences
### Positive
- Domain 層が Infrastructure 層に依存しないため、ビジネスロジックの変更影響範囲が明確になる
- Repository インターフェースによるモック化により、テストカバレッジ 80% 以上の品質基準を維持しやすい
- Infrastructure 層の変更（SQLite → PostgreSQL、CSV → API 連携）が Domain 層や Application 層に影響しない
- Repository の実装を差し替えることで、テスト環境と本番環境で異なるデータストアを使用できる
- コーディング規約で「Application 層は Repository インターフェース経由でのみデータにアクセスする」ルールを明文化でき、技術的負債の蓄積を抑制できる

### Negative / Risks
- Repository インターフェースと実装の両方を実装する必要があり、初期実装コストが増加する（1〜2 日程度）
- Repository の粒度（エンティティ単位か、集約単位か）の設計判断が必要である（軽減策: エンティティ単位で Repository を作成し、複雑なクエリは専用メソッドを追加）
- Repository の実装が肥大化するリスクがある（軽減策: Repository は CRUD 操作と集計クエリのみに責務を限定し、ビジネスロジックは Domain 層に委譲）
- Application 層が Repository の実装詳細（SQL クエリの性能特性）に依存する可能性がある（軽減策: Repository インターフェースにパフォーマンス要件をコメントで明記）

## Links
- docs/requirements/02_system-requirements.md
- docs/design/01_architecture-evaluation.md
- ADR-001-ddd-lite-monolith.md
