# ADR-001: DDD Lite Monolith アーキテクチャの採用

## Status
Accepted

## Context
- Profit Trace は複数プロジェクトの工数消化状況を日次で可視化するデスクトップアプリケーションである
- 関連要件: REQ-F-001〜REQ-F-009（全機能要件）、REQ-NF-004（保守性）、REQ-NF-008（安定性）
- 技術制約として Python 3.12 + PySide6 + SQLite 環境で動作し、小規模チーム（1〜3名）での開発・保守が想定される
- 要件定義は凍結状態だが、ユーザーフィードバックにより将来の機能拡張（新しいグラフ種類、部署別集計、外部サービス統合）が予想される
- 主要品質特性として Maintainability（QA-003）と Testability（QA-008）を重視する必要がある

## Decision
- 4層構成の DDD Lite Monolith アーキテクチャを採用する
- Presentation / Application / Domain / Infrastructure の層構成とする
- Domain 層にビジネスロジック（工数消化率計算、バーンダウン計算、営業日数計算、要因推定）を集約する
- エンティティは Project, WorkRecord, WorkdayCalendar, Member とする
- Repository インターフェースを Domain 層で定義し、Infrastructure 層で実装する
- 過度な抽象化を避け、Aggregate Root や Value Object は最小限の使用とする

## Alternatives
- **Layered Monolith（3層構成）**: Presentation / Application / Infrastructure の 3 層構成。実装速度が速く（5〜6日）パフォーマンスが高いが、Application 層にビジネスロジックとユースケース調整が混在しやすく、将来の機能拡張時に肥大化リスクがある。
- **Layered Monolith（3層構成 + MVC）**: Qt Model/View フレームワークとの親和性が高いが、本プロジェクトはグラフ描画中心でありテーブル表示中心ではないため、利点を活かしにくい。MVC パターンの複雑さによりエラーハンドリングの責務が分散しやすい。
- **マイクロサービスアーキテクチャ**: 各機能を独立サービスに分離。小規模デスクトップアプリには過剰であり、運用コストが大幅に増加する。マルチユーザー同時接続が不要な本プロジェクトには不適切。

## Rationale
- Domain 層を独立させることで、ビジネスロジックの変更影響範囲を明確化し、長期的な保守性を向上させる
- Repository パターンにより、テスト時に Infrastructure 層をモックに差し替え可能となり、テストカバレッジ 80% 以上の品質基準を維持しやすい
- 将来の機能拡張（新しい集計軸の追加、複雑な要因推定ロジックの導入）時に Domain 層に集中して実装でき、既存コードへの影響を最小化できる
- 初期実装コストは 3 層構成比で 1.2〜1.5 倍（6〜9日 vs 5〜6日）増加するが、将来のリファクタリングコスト削減により長期的には開発効率が向上する
- 抽象化層が 1 段増えることによるパフォーマンス低下（1〜2秒程度）は、要件の性能基準（CSV読み込み: 5〜10秒、チャート描画: 3〜5秒）を十分に満たす範囲内である

## Consequences
### Positive
- ビジネスロジックの変更影響範囲が明確化され、長期的な保守性が向上する
- Repository インターフェースによるモック化により、Domain 層と Application 層の単体テストが容易になる
- 新しい集計軸や要因推定ロジックの追加が Domain 層に集中でき、既存処理への影響が最小化される
- Infrastructure 層の変更（SQLite → PostgreSQL、CSV → API連携）が Domain 層に影響しない設計となる
- コーディング規約（Domain 層以外にビジネスロジックを書かない）を明文化でき、技術的負債の蓄積を抑制できる

### Negative / Risks
- 初期実装コストが 3 層構成比で 1.2〜1.5 倍に増加する（6〜9日 vs 5〜6日）
- DDD の概念（エンティティ、Repository、依存性逆転の原則）の理解に 1〜2 日の学習コストが必要
- 抽象化層が 1 段増えることにより、処理時間が 1〜2 秒程度増加する可能性がある（要件の性能基準は満たす）
- 小規模チーム（1〜3名）では過度な抽象化がオーバーエンジニアリングになるリスクがある（軽減策: Aggregate Root や Value Object の最小限使用）
- Presentation 層や Infrastructure 層にビジネスロジックが漏れる可能性がある（軽減策: コードレビューで確認、月次アーキテクチャレビュー実施）

## Links
- docs/requirements/02_system-requirements.md
- docs/design/01_architecture-evaluation.md
