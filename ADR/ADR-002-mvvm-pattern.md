# ADR-002: MVVM パターンの採用

## Status
Accepted

## Context
- Presentation 層のアーキテクチャパターンを決定する必要がある
- 関連要件: REQ-F-004（プロジェクト一覧画面）、REQ-F-005（バーンダウンチャート）、REQ-F-006（個人稼働状況）、REQ-NF-003（操作性）
- PySide6（Qt）を GUI フレームワークとして使用し、Signal/Slot メカニズムが利用可能である
- グラフ描画中心の UI 構成（バーンダウンチャート、積み上げ棒グラフ）であり、テーブル表示は補助的である
- UI イベント処理とビジネスロジックの分離が求められる

## Decision
- Presentation 層に MVVM（Model-View-ViewModel）パターンを適用する
- View は PySide6 の QMainWindow / QWidget / QDialog で実装する
- ViewModel は View ↔ Application 層の仲介を行い、Signal/Slot でデータバインディングを実現する
- View が Signal で ViewModel に UI イベントを通知し、ViewModel が Application 層を呼び出す
- ViewModel が Application 層から取得したデータを Signal で View に通知し、View が Slot で受け取って UI を更新する
- ViewModel はビジネスロジックを持たず、Application 層に委譲する

## Alternatives
- **MVC パターン**: Controller が View ↔ Application 層の仲介を行う。Qt Model/View フレームワーク（QAbstractTableModel）を使用し、テーブル表示中心の UI に適している。ただし、View ↔ Qt Model ↔ Controller の三角関係により MVVM よりも複雑になり、グラフ描画中心の本プロジェクトでは利点を活かしにくい。
- **MVP パターン**: Presenter が View ↔ Application 層の仲介を行う。MVVM と類似だが、Presenter が View の参照を持つため View との結合度が高くなる。Qt の Signal/Slot メカニズムとの統合が MVVM ほど自然ではない。
- **パターンなし（View が直接 Application 層を呼び出す）**: 実装が最もシンプルだが、View にビジネスロジックが漏れるリスクが高く、テスト容易性が著しく低下する。

## Rationale
- MVVM パターンは Qt の Signal/Slot メカニズムと自然に統合され、データバインディングが容易である
- ViewModel が Signal を発行し View が Slot で受け取る仕組みは、Qt の標準的な実装パターンに沿っている
- View は UI イベントの受付と表示のみに集中でき、ViewModel がビジネスロジックを Application 層に委譲することでテスト容易性が向上する
- グラフ描画中心の UI 構成では、Qt Model/View フレームワーク（QAbstractTableModel）の複雑さを回避でき、シンプルな実装が可能である
- ViewModel と View の結合度が低く（Signal/Slot 経由）、View の差し替えやモック化が容易である

## Consequences
### Positive
- ViewModel が View ↔ Application 層の仲介を行うことで、UI イベント処理がシンプルになる
- Qt の Signal/Slot メカニズムと自然に統合され、学習コストが低い
- ドラッグ&ドロップやエラーダイアログなどの UI 操作を ViewModel 経由で統一的に処理できる
- ViewModel の単体テストが可能であり（Signal/Slot の発火を検証）、pytest-qt で対応できる
- View がビジネスロジックを持たないため、UI の変更が Application 層に影響しない

### Negative / Risks
- ViewModel のテストで Signal/Slot の発火タイミングを検証する必要があり、テストコードが若干増加する
- ViewModel が肥大化するリスクがある（軽減策: ViewModel はデータ変換のみ行い、集計処理は Application 層に委譲）
- Signal/Slot の命名規則や接続方法が統一されていないと、デバッグが困難になる可能性がある（軽減策: コーディング規約で Signal/Slot の命名規則を明文化）

## Links
- docs/requirements/02_system-requirements.md
- docs/design/01_architecture-evaluation.md
- ADR-001-ddd-lite-monolith.md
