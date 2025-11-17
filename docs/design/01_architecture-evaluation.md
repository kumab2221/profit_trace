# 01. Architecture Evaluation

## 1. Context（文脈）

### システムの概要
Profit Trace は、複数プロジェクトの工数消化状況を日次で可視化するデスクトップアプリケーションである。外部サービスから取得した工数実績データ（CSV）、プロジェクト契約情報（CSV）、休日マスタ（JSON）を取り込み、バーンダウンチャート形式での進捗可視化、個人ごとの稼働状況可視化、工数余剰要因の分析支援を提供する。Python (uv) + PySide6 環境で動作し、各ローカル PC で単独実行される。

### 想定される利用シナリオ
- **日次データ更新**: チームリーダーが毎朝、外部サービスから CSV をエクスポートし、本アプリに取り込む（所要時間: 1〜2 分）
- **週次進捗確認**: 週次会議前に、全プロジェクトの一覧画面で消化率を確認し、問題プロジェクトを特定する（所要時間: 5〜10 分）
- **プロジェクト詳細分析**: 消化遅延が発見されたプロジェクトの詳細画面でバーンダウンチャートを確認し、実績線と理想線の乖離を分析する（所要時間: 3〜5 分）
- **メンバー稼働状況確認**: 工数余剰が発生している場合、メンバー別稼働状況画面で未稼働期間や他プロジェクト従事を確認し、要因を特定する（所要時間: 5〜10 分）
- **月次レポート作成**: 経営層・PM 向けに、全プロジェクトとメンバー稼働状況のレポートを CSV / JSON 形式でエクスポートする（所要時間: 1〜2 分）

### 技術・組織・運用上の制約の整理

#### 技術的制約
- **言語・フレームワーク**: Python 3.12、PySide6（GUI）、plotly（グラフ描画）
- **データソース**: CSV（工数実績、プロジェクト契約）、JSON（休日マスタ）のみ
- **データストア**: SQLite（ローカルファイル）
- **配布形態**: デスクトップアプリ（Web サーバー不要、マルチユーザー同時接続不要）
- **外部依存**: 外部サービスからの工数実績 CSV エクスポート機能（仕様変更時は対応が必要）

#### 運用制約
- **データ更新頻度**: 日次（1 日 1 回、手動取り込み）
- **想定稼働時間**: 1 日 30 分程度
- **ユーザー数**: 各ローカル PC で単独実行（10〜20 名程度が各自のマシンで使用）
- **データ編集方針**: 入力データ（CSV / JSON）の編集は別ツールで行い、編集後のファイルを再取り込みする

#### 組織的制約
- **ユーザー層**: チームリーダー、チームメンバー、経営層・PM（全員が同じツールを使用）
- **スキルセット**: Python 開発経験あり（PEP 8 準拠、テストカバレッジ 80% 以上の品質基準を維持できる体制）
- **開発体制**: 小規模チーム（1〜3 名程度）での開発・保守を想定

### データフローの前提（重要）
- **Single Source of Truth**: 外部 CSV / JSON ファイルがマスタデータ。SQLite は「表示・集計のためのキャッシュ」として機能する。
- **データフロー**: 外部ファイル（CSV / JSON）→ アプリ（インポート処理・バリデーション）→ SQLite（データストア）→ アプリ（集計・グラフ生成）→ UI（PySide6）
- **更新方針**: 日次で CSV / JSON を再取り込みし、SQLite を上書き更新する。データの整合性は CSV データで上書きすることで保証する。
- **バックアップ**: SQLite の内容を CSV / JSON 形式でエクスポート可能（REQ-NF-006）。

---

## 2. Quality Attributes（品質特性）

| ID     | Attribute       | 説明                                                                                                                                 | 関連 REQ-NF |
|--------|-----------------|--------------------------------------------------------------------------------------------------------------------------------------|------------|
| QA-001 | Performance     | CSV / JSON の読み込み時間（プロジェクト契約 50 件: 5 秒以内、工数実績 5000 件: 10 秒以内、休日マスタ 10 年: 3 秒以内）、チャート描画時間（バーンダウン: 3 秒以内、メンバー稼働: 5 秒以内）。長時間処理時は UI がフリーズせず、プログレスバーを表示すること。 | REQ-NF-001, REQ-NF-002 |
| QA-002 | Usability       | ドラッグ&ドロップでのファイル取り込み、ワンクリックでの画面遷移、エラー時の明確なメッセージ表示。操作マニュアルなしで基本操作が可能であること。 | REQ-NF-003 |
| QA-003 | Maintainability | PEP 8 準拠、docstring 記述、テストカバレッジ 80% 以上、モジュール構成の責務分離。将来の機能追加（新しいグラフ種類、新しい集計軸）が容易であること。 | REQ-NF-004 |
| QA-004 | Availability    | 不正ファイル読み込み時もクラッシュせず、エラーメッセージを表示して正常復帰。メモリリークなし、長時間稼働（30 分）でのパフォーマンス劣化なし。 | REQ-NF-008 |
| QA-005 | Operability     | エラーログの自動記録（エラー内容、日時、スタックトレース）、ログファイルのユーザー確認可能な場所への保存（アプリケーションディレクトリ）。 | REQ-NF-005 |
| QA-006 | Security        | データはローカル PC 上のみで管理、外部サーバーへの送信なし。OS のファイルアクセス権限に従う。                                      | REQ-NF-007 |
| QA-007 | Portability     | Python 3.12 + PySide6 + SQLite で動作。Windows ノート PC での動作保証（他 OS は Constraints に記載なし、要確認）。                  | 5. Constraints |
| QA-008 | Testability     | 単体テストカバレッジ 80% 以上、ビジネスロジック（工数集計、バーンダウン計算）の UI 層からの分離が容易であること。                   | REQ-NF-004 |

---

## 3. Candidate Architectures（候補アーキテクチャ）

### 3.1 Candidate A: Layered Monolith（3 層構成 + MVP パターン）

#### 概要
シンプルな 3 層構成（Presentation / Application / Infrastructure）のモノリスアーキテクチャ。Presentation 層に MVP（Model-View-Presenter）パターンを適用し、UI とビジネスロジックを分離する。小規模デスクトップアプリに適した構成で、学習コストが低く、実装速度が速い。

#### 主な構成要素
- **Presentation 層**:
  - PySide6（View: QMainWindow / QWidget / QDialog）
  - MVP パターン（Presenter が View ↔ Application 層の仲介）
  - 責務: ユーザー入力の受付、画面表示、プログレスバー / エラーダイアログの表示
- **Application 層**:
  - ビジネスロジック（工数集計、バーンダウン計算、メンバー稼働分析、要因推定）
  - ファイルインポート処理（CSV / JSON パース、バリデーション）
  - 責務: 業務ルールの実装、データの変換・集計
- **Infrastructure 層**:
  - SQLite アクセス（ORM なし、生 SQL または pandas.read_sql）
  - CSV / JSON ファイル I/O（pandas, json モジュール）
  - ログ出力（logging モジュール）
  - 責務: データ永続化、外部ファイル読み書き

#### 採用する主な技術スタック
- 言語: Python 3.12
- GUI フレームワーク: PySide6
- グラフ描画: plotly
- データストア: SQLite
- データ処理: pandas
- テスト: pytest
- インフラ: ローカル実行（uv 環境）

#### データフローと Single Source of Truth
- **インポートフロー**: CSV / JSON ファイル → Infrastructure 層（ファイル I/O）→ Application 層（バリデーション・集計）→ Infrastructure 層（SQLite 書き込み）→ Presentation 層（View 更新）
- **表示フロー**: Presentation 層（ユーザー操作）→ Application 層（集計処理）→ Infrastructure 層（SQLite 読み込み）→ Application 層（グラフデータ生成）→ Presentation 層（plotly 描画）
- **Single Source of Truth**: 外部 CSV / JSON ファイル。SQLite は「表示・集計のためのキャッシュ」として機能し、再取り込みで上書き更新される。
- **責務分離**: Presentation 層はデータを直接 SQLite から読まず、Application 層経由でアクセスする。Application 層は SQLite の存在を知らず、Infrastructure 層の抽象インターフェース（Repository 相当）を使用する。

---

### 3.2 Candidate B: DDD Lite Monolith（4 層構成 + MVP パターン）

#### 概要
Domain 層を独立させた 4 層構成（Presentation / Application / Domain / Infrastructure）のモノリスアーキテクチャ。DDD（Domain-Driven Design）の概念を軽量に導入し、ビジネスロジックを Domain 層に集約する。Presentation 層には Candidate A 同様 MVP パターンを適用する。将来の機能拡張（新しい集計軸、複雑な要因推定ロジック）を見据えた構成。

#### 主な構成要素
- **Presentation 層**:
  - PySide6（View: QMainWindow / QWidget / QDialog）
  - MVP パターン（Presenter が View ↔ Application 層の仲介）
  - 責務: ユーザー入力の受付、画面表示、プログレスバー / エラーダイアログの表示
- **Application 層**:
  - ユースケース実装（ファイルインポート、プロジェクト一覧取得、バーンダウンデータ生成、メンバー稼働分析）
  - Domain 層と Infrastructure 層の橋渡し
  - 責務: ユースケースの調整（Domain 層のロジックを呼び出し、Infrastructure 層でデータを永続化）
- **Domain 層**:
  - エンティティ（Project, WorkRecord, WorkdayCalendar, Member）
  - ビジネスロジック（工数消化率計算、バーンダウン理想線 / 実績線計算、営業日数計算、要因推定）
  - Repository インターフェース（ProjectRepository, WorkRecordRepository 等）
  - 責務: ビジネスルールの実装、データモデルの定義
- **Infrastructure 層**:
  - Repository 実装（SQLite アクセス、ORM なし）
  - CSV / JSON ファイル I/O（pandas, json モジュール）
  - ログ出力（logging モジュール）
  - 責務: データ永続化、外部ファイル読み書き

#### 採用する主な技術スタック
- 言語: Python 3.12
- GUI フレームワーク: PySide6
- グラフ描画: plotly
- データストア: SQLite
- データ処理: pandas
- テスト: pytest
- インフラ: ローカル実行（uv 環境）

#### データフローと Single Source of Truth
- **インポートフロー**: CSV / JSON ファイル → Infrastructure 層（ファイル I/O）→ Application 層（ユースケース：ファイルインポート）→ Domain 層（バリデーション・エンティティ生成）→ Infrastructure 層（Repository 経由で SQLite 書き込み）→ Presentation 層（View 更新）
- **表示フロー**: Presentation 層（ユーザー操作）→ Application 層（ユースケース：バーンダウン取得）→ Domain 層（バーンダウン計算ロジック）→ Infrastructure 層（Repository 経由で SQLite 読み込み）→ Domain 層（エンティティ返却）→ Application 層（DTO 変換）→ Presentation 層（plotly 描画）
- **Single Source of Truth**: 外部 CSV / JSON ファイル（Candidate A と同じ）。
- **責務分離**: Domain 層は Infrastructure 層に依存しない（依存性逆転の原則）。Repository インターフェースは Domain 層で定義し、Infrastructure 層で実装する。Application 層は Domain 層のビジネスロジックを呼び出し、Infrastructure 層で永続化する。

---

### 3.3 Candidate C: Layered Monolith（3 層構成 + MVC パターン）

#### 概要
Candidate A と同じ 3 層構成だが、Presentation 層に MVC（Model-View-Controller）パターンを適用する。Controller が View と Application 層の仲介を行う。PySide6 の標準的な実装パターン（Qt Model/View フレームワーク）と親和性が高いが、データバインディングの複雑さが増す可能性がある。

#### 主な構成要素
- **Presentation 層**:
  - PySide6（View: QMainWindow / QWidget / QDialog、Model: QAbstractTableModel 等、Controller: カスタムクラス）
  - MVC パターン（Controller が View ↔ Application 層の仲介、Model が View ↔ データの橋渡し）
  - 責務: ユーザー入力の受付、画面表示、データバインディング
- **Application 層**:
  - Candidate A と同じ（ビジネスロジック、ファイルインポート処理）
- **Infrastructure 層**:
  - Candidate A と同じ（SQLite アクセス、CSV / JSON I/O、ログ出力）

#### 採用する主な技術スタック
- Candidate A と同じ

#### データフローと Single Source of Truth
- Candidate A とほぼ同じだが、Presentation 層内で View ↔ Model 間のデータバインディングが追加される。
- Qt Model/View フレームワークを使用する場合、QAbstractTableModel をカスタム実装し、Application 層からデータを取得して Model に格納する。

---

## 4. Evaluation（評価）

### 4.1 Quality Attributes × Candidate マトリクス

| QA \ Candidate | A（Layered + MVP） | B（DDD Lite + MVP） | C（Layered + MVC） | コメント（重要な理由・具体策） |
|----------------|---------------------|---------------------|---------------------|----------------------------------|
| QA-001<br>Performance | ◎ | ○ | ◎ | **A**: 処理経路が最短（Presentation → Application → Infrastructure）。CSV インポート時は pandas で一括読み込み→ SQLite 一括挿入。チャート描画は Application 層で集計後 plotly に渡すだけ。ワーカースレッド（QThread）でインポート / 描画を実行し、UI をフリーズさせない。<br>**B**: 抽象化層（Domain 層、Repository インターフェース）が 1 段増えるが、I/O 主体の処理のため影響は小さい（1〜2 秒程度の差）。Domain 層でのエンティティ生成コストが若干増加。<br>**C**: A とほぼ同等だが、Qt Model/View フレームワーク使用時のデータバインディングコストが追加される可能性。 |
| QA-002<br>Usability | ◎ | ◎ | ○ | **A / B**: MVP パターンにより、Presenter が UI イベントを受け取り、Application 層を呼び出すシンプルな構造。ドラッグ&ドロップは View で実装し、Presenter に委譲。エラーダイアログは Presenter が View に指示。<br>**C**: MVC パターンでは Controller が複雑になりやすく（View ↔ Model ↔ Controller の三角関係）、エラーハンドリングの責務が分散しやすい。Qt Model/View フレームワークの学習コストも高い。 |
| QA-003<br>Maintainability | ○ | ◎ | ○ | **A**: 3 層構成はシンプルだが、Application 層にビジネスロジックとユースケース調整が混在しやすい。将来の機能追加（新しい集計軸、複雑な要因推定）時に Application 層が肥大化するリスク。<br>**B**: Domain 層を独立させることで、ビジネスロジックの変更影響範囲を狭く保てる。Repository インターフェースにより、テスト時に Infrastructure 層をモックに差し替え可能。将来の拡張（新しいエンティティ、新しいビジネスルール）に強い。<br>**C**: A と同等だが、MVC パターンの複雑さ（View ↔ Model ↔ Controller の三角関係）により、変更時の影響範囲が読みにくくなる可能性。 |
| QA-004<br>Availability | ◎ | ◎ | ◎ | **全候補**: 不正ファイル読み込み時は Application 層（または Domain 層）でバリデーションエラーを検出し、例外を Presentation 層に返却。Presenter（または Controller）がエラーダイアログを表示し、処理を中止。メモリリークは pandas の DataFrame を適切に解放し、QThread を正しく終了することで回避。長時間稼働のパフォーマンス劣化は、SQLite のコネクションプーリング不要（単独実行）のため発生しにくい。 |
| QA-005<br>Operability | ◎ | ◎ | ◎ | **全候補**: logging モジュールを Infrastructure 層で初期化し、全層でロガーを使用。エラー発生時は Application 層（または Domain 層）で logger.error() を呼び出し、スタックトレースを記録。ログファイルはアプリケーションディレクトリに保存（例: logs/profit_trace.log）。 |
| QA-006<br>Security | ◎ | ◎ | ◎ | **全候補**: Infrastructure 層の SQLite アクセスおよび CSV / JSON I/O はローカルファイルシステムのみ。外部サーバーへの通信コードは一切含めない。OS のファイルアクセス権限に従う。 |
| QA-007<br>Portability | ◎ | ◎ | ◎ | **全候補**: Python 3.12 + PySide6 + SQLite はクロスプラットフォーム対応。Windows ノート PC での動作保証（Constraints より）。 |
| QA-008<br>Testability | ○ | ◎ | ○ | **A**: Presentation 層と Application 層が分離されているため、Application 層の単体テストは可能。ただし、Application 層が Infrastructure 層を直接呼び出すため、テスト時に SQLite のモックが必要。<br>**B**: Repository インターフェースにより、テスト時に Infrastructure 層をモックに差し替え可能。Domain 層のビジネスロジック（工数消化率計算、バーンダウン計算）は純粋な関数として実装でき、単体テストが容易。Application 層のユースケースも、Domain 層と Repository のモックで独立してテスト可能。<br>**C**: A と同等だが、MVC パターンの複雑さにより、Controller のテストが煩雑になる可能性。 |

---

### 4.2 リスクとトレードオフ

#### Candidate A: Layered Monolith（3 層構成 + MVP パターン）

**強み**
- **実装速度が速い**: 3 層構成はシンプルで、学習コストが低い。MVP パターンも理解しやすく、短期間で実装可能。
- **パフォーマンスが高い**: 処理経路が最短で、抽象化層が少ないため、オーバーヘッドが小さい。
- **小規模チームに適している**: 1〜3 名程度の開発体制では、過度な抽象化を避けることで開発効率を維持できる。

**弱み / リスク**
- **Application 層の肥大化リスク**: ビジネスロジックとユースケース調整が混在しやすく、将来の機能追加時に Application 層が肥大化する可能性。
- **テスト容易性の低下**: Application 層が Infrastructure 層を直接呼び出すため、テスト時に SQLite のモックが必要。
- **変更影響範囲の拡大**: ビジネスルールの変更時に Application 層全体を確認する必要があり、変更影響範囲が読みにくくなる可能性。

**向いているケース / 向いていないケース**
- **向いている**: 要件が凍結状態で、大規模な機能追加が想定されない場合。小規模チームで迅速に実装したい場合。
- **向いていない**: 将来の機能拡張（新しい集計軸、複雑な要因推定ロジック）が頻繁に予想される場合。複数チームでの並行開発が必要な場合。

**将来の機能拡張シナリオに対する見通し**
- **追加グラフ種類（例: ガントチャート、ヒートマップ）**: Application 層に新しい集計処理を追加するだけで対応可能（リファクタリング不要）。
- **新しい集計軸（例: 部署別、役職別）**: Application 層の集計処理を修正する必要があり、既存処理との影響範囲の確認が必要。
- **複雑な要因推定ロジック（例: 機械学習モデルの導入）**: Application 層が肥大化し、ビジネスロジックの責務分離が困難になる可能性。この時点で Domain 層の導入（Candidate B への移行）を検討する必要がある。

---

#### Candidate B: DDD Lite Monolith（4 層構成 + MVP パターン）

**強み**
- **変更容易性が高い**: Domain 層を独立させることで、ビジネスロジックの変更影響範囲を狭く保てる。Repository インターフェースにより、Infrastructure 層の変更（例: SQLite → PostgreSQL）が容易。
- **テスト容易性が高い**: Repository インターフェースにより、テスト時に Infrastructure 層をモックに差し替え可能。Domain 層のビジネスロジックは純粋な関数として実装でき、単体テストが容易。
- **将来の拡張性が高い**: 新しいエンティティ、新しいビジネスルールの追加が容易。複雑な要因推定ロジックも Domain 層に集約できる。

**弱み / リスク**
- **実装コストの増加**: 4 層構成と Repository インターフェースの実装により、Candidate A よりも実装コストが 1.2〜1.5 倍程度増加する可能性。
- **学習コストの増加**: DDD の概念（エンティティ、Repository、依存性逆転の原則）を理解する必要があり、小規模チームではオーバーエンジニアリングになる可能性。
- **パフォーマンスのわずかな低下**: 抽象化層が 1 段増えるため、処理時間が 1〜2 秒程度増加する可能性（ただし、要件の性能基準は満たす）。

**向いているケース / 向いていないケース**
- **向いている**: 将来の機能拡張が頻繁に予想される場合。複数チームでの並行開発が必要な場合。ビジネスロジックの複雑化が予想される場合。
- **向いていない**: 要件が凍結状態で、機能追加が一切想定されない場合。極めて小規模（1 名）での開発で、実装速度を最優先する場合。

**将来の機能拡張シナリオに対する見通し**
- **追加グラフ種類（例: ガントチャート、ヒートマップ）**: Domain 層に新しいビジネスロジックを追加し、Application 層で新しいユースケースを実装するだけで対応可能（既存処理への影響なし）。
- **新しい集計軸（例: 部署別、役職別）**: Domain 層に新しいエンティティ（Department, Role）と集計ロジックを追加するだけで対応可能。Repository インターフェースに新しいメソッドを追加し、Infrastructure 層で実装。
- **複雑な要因推定ロジック（例: 機械学習モデルの導入）**: Domain 層に新しいサービスクラス（FactorEstimationService）を追加し、Repository 経由でデータを取得して推定ロジックを実装。既存の Domain 層との影響範囲が明確に分離される。
- **外部サービス統合（例: Slack 通知、API 連携）**: Infrastructure 層に新しい実装（SlackNotifier, ExternalApiClient）を追加し、Application 層で呼び出すだけで対応可能。Domain 層は変更不要。

---

#### Candidate C: Layered Monolith（3 層構成 + MVC パターン）

**強み**
- **Qt Model/View フレームワークとの親和性**: PySide6 の標準的な実装パターン（QAbstractTableModel 等）を使用でき、データバインディングが自動化される。

**弱み / リスク**
- **MVC パターンの複雑さ**: View ↔ Model ↔ Controller の三角関係により、エラーハンドリングの責務が分散しやすく、変更時の影響範囲が読みにくくなる。
- **学習コストの増加**: Qt Model/View フレームワークの理解が必要で、MVP パターンよりも学習コストが高い。
- **テスト容易性の低下**: Controller のテストが煩雑になる可能性。

**向いているケース / 向いていないケース**
- **向いている**: Qt Model/View フレームワークの経験が豊富で、データバインディングを活用したい場合。テーブル表示が中心の UI 構成の場合。
- **向いていない**: MVP パターンの経験が豊富で、シンプルな構造を優先する場合。グラフ描画が中心の UI 構成の場合（本プロジェクトはバーンダウンチャートが中心）。

**将来の機能拡張シナリオに対する見通し**
- Candidate A とほぼ同等だが、MVC パターンの複雑さにより、変更時の影響範囲の確認コストが増加する可能性。

---

## 5. Recommended Architecture（推奨アーキテクチャ）

### 5.1 採用するアーキテクチャ

**採用候補**: Candidate B（DDD Lite Monolith: 4 層構成 + MVP パターン）

**採用理由**:
- **主要品質特性（QA-003, QA-008）に対する適合性が最も高い**: Domain 層を独立させることで、Maintainability（変更容易性）と Testability（テスト容易性）が大幅に向上する。将来の機能拡張（新しい集計軸、複雑な要因推定ロジック）に強く、技術的負債の蓄積を抑制できる。
- **既存システム / チームスキルとの整合性**: 小規模チーム（1〜3 名）でも実装可能な構成。DDD の概念は軽量に導入し、過度な抽象化を避ける（例: Aggregate Root は使用しない、Value Object は最小限）。PEP 8 準拠、テストカバレッジ 80% 以上の品質基準を維持しやすい。
- **将来の拡張性**: 要件定義書（02_system-requirements.md）は凍結状態だが、ユーザーフィードバックにより機能追加が予想される（例: 新しいグラフ種類、部署別集計、Slack 通知）。Domain 層を独立させることで、これらの拡張が容易になる。
- **データフローと Single Source of Truth の観点で一貫性を保ちやすい**: Repository インターフェースにより、Infrastructure 層の変更（例: SQLite → PostgreSQL、CSV → API 連携）が容易。Domain 層は Infrastructure 層に依存しないため、データソースの変更が Domain 層に影響しない。
- **UI アーキテクチャの方針が選択したアプリケーションアーキテクチャと整合**: MVP パターンにより、Presentation 層と Application 層の責務が明確に分離される。Presenter が View ↔ Application 層の仲介を行い、View は UI イベントの受付と表示のみに集中できる。

**Performance（QA-001）への影響について**:
- Candidate B は Candidate A に比べて抽象化層が 1 段増えるが、要件の性能基準（CSV 読み込み: 5〜10 秒、チャート描画: 3〜5 秒）は十分に満たす。パフォーマンスのわずかな低下（1〜2 秒程度）は、Maintainability と Testability の大幅な向上によるトレードオフとして許容範囲内。

---

### 5.2 選択しなかった候補と理由

#### Candidate A を採用しない理由

**長所**:
- 実装速度が速く、パフォーマンスが高い。
- 小規模チームに適したシンプルな構成。

**それでも優先度が下がる理由**:
- **将来の機能拡張に対する脆弱性**: 要件定義書は凍結状態だが、ユーザーフィードバックにより機能追加が予想される。Application 層の肥大化リスクがあり、将来のリファクタリングコストが増加する可能性。
- **テスト容易性の低下**: Application 層が Infrastructure 層を直接呼び出すため、テスト時に SQLite のモックが必要。テストカバレッジ 80% 以上の品質基準を維持するコストが増加する。
- **技術的負債の蓄積**: ビジネスロジックとユースケース調整が混在しやすく、長期的には保守性が低下する可能性。

**判断**: 実装速度の優位性（Candidate B より 20〜30% 速い）よりも、長期的な保守性とテスト容易性を優先し、Candidate B を採用する。

---

#### Candidate C を採用しない理由

**長所**:
- Qt Model/View フレームワークとの親和性が高く、データバインディングが自動化される。

**それでも優先度が下がる理由**:
- **MVC パターンの複雑さ**: 本プロジェクトはテーブル表示よりもグラフ描画（バーンダウンチャート）が中心であり、Qt Model/View フレームワークの利点を活かしにくい。
- **学習コストの増加**: MVP パターンよりも学習コストが高く、小規模チームでは実装効率が低下する可能性。
- **エラーハンドリングの分散**: View ↔ Model ↔ Controller の三角関係により、エラーハンドリングの責務が分散しやすく、変更時の影響範囲が読みにくくなる。

**判断**: Qt Model/View フレームワークの利点を活かせない UI 構成（グラフ中心）であり、MVP パターンの方がシンプルで実装しやすい。Candidate B を採用する。

---

## 6. Impact & Risks（影響とリスク）

### 開発コストへの影響

**初期実装コスト**:
- **Candidate A 比**: 1.2〜1.5 倍程度の増加を想定。
  - Domain 層の設計（エンティティ、Repository インターフェース、ビジネスロジック）: 2〜3 日
  - Application 層の実装（ユースケース）: 2〜3 日
  - Infrastructure 層の実装（Repository 実装）: 2〜3 日
  - 合計: 6〜9 日（Candidate A は 5〜6 日を想定）
- **学習コスト**: DDD の概念（エンティティ、Repository、依存性逆転の原則）の理解に 1〜2 日。ただし、軽量導入（Aggregate Root は使用しない）により、学習コストを抑制。

**テスト設計・テスト自動化のコスト**:
- **Candidate A 比**: 同等またはわずかに減少。
  - Repository インターフェースによるモック化により、Domain 層と Application 層のテストが容易になる。
  - テストカバレッジ 80% 以上の品質基準を維持しやすい。

---

### 運用コストへの影響

**インフラ構成の複雑さ**:
- **モノリス構成**: デスクトップアプリとして単独実行されるため、インフラ構成は極めてシンプル。配布形態は uv 環境（Python 3.12 + PySide6 + SQLite）のインストールのみ。
- **データストア**: SQLite（ローカルファイル）のため、DB サーバーの構築・運用は不要。

**障害対応の難易度**:
- **ログ収集**: logging モジュールにより、エラー内容・日時・スタックトレースをログファイル（logs/profit_trace.log）に自動記録。
- **障害分析**: Domain 層のビジネスロジックが独立しているため、障害発生時の影響範囲の特定が容易。例: バーンダウン計算エラー → Domain 層の BurndownCalculator クラスを確認。

**ログ収集・監視・バックアップの仕組み**:
- **ログ収集**: logging モジュールによる自動記録（アプリケーションディレクトリに保存）。ログローテーション不要（REQ-NF-005）。
- **監視**: 不要（ローカル実行のため）。
- **バックアップ**: SQLite の内容を CSV / JSON 形式でエクスポート可能（REQ-NF-006）。バックアップファイルからのリストアも可能。

---

### 組織・プロセスへの影響

**チームサイズと役割分担**:
- **想定チームサイズ**: 1〜3 名
- **役割分担**:
  - Domain 層担当（ビジネスロジック実装）: 1 名
  - Application / Infrastructure 層担当（ユースケース実装、Repository 実装）: 1 名
  - Presentation 層担当（UI 実装、Presenter 実装）: 1 名
- **並行開発**: Domain 層の Repository インターフェースを先に定義することで、Application 層と Infrastructure 層の並行開発が可能。

**必要となるスキルセット**:
- **Python 3.12**: 全員必須
- **PySide6**: Presentation 層担当者が必須
- **DDD の基礎知識**: Domain 層担当者が必須（エンティティ、Repository、依存性逆転の原則）
- **pytest**: 全員必須（テストカバレッジ 80% 以上の品質基準）
- **pandas, plotly**: Application 層担当者が必須

**既存プロセス（リリースフロー、運用手順）との整合**:
- **リリースフロー**: uv 環境でのビルド（uv build）→ 配布（各ローカル PC に uv install）→ 動作確認。
- **運用手順**: 日次で CSV / JSON ファイルを外部サービスからエクスポート → 本アプリに取り込み → バーンダウンチャート確認。

---

### 技術的負債になりうるポイント

**ビジネスロジックの散在（UI・Infrastructure への漏れ）**:
- **リスク**: Presenter や Repository 実装にビジネスロジックが漏れる可能性。
- **対策**:
  - コーディング規約で「Domain 層以外にビジネスロジックを書かない」ルールを明文化。
  - コードレビューで、Presenter や Repository 実装にビジネスロジックが含まれていないか確認。

**層間の密結合（特に Application ↔ Infrastructure）**:
- **リスク**: Application 層が Infrastructure 層の実装詳細（SQLite の SQL クエリ等）に依存する可能性。
- **対策**:
  - Repository インターフェースを Domain 層で定義し、Application 層は Interface 経由でのみアクセス。
  - Infrastructure 層の変更（例: SQLite → PostgreSQL）が Application 層に影響しないことを、統合テストで検証。

**データフローが曖昧な部分（CSV vs DB の整合性など）**:
- **リスク**: CSV ファイルと SQLite の整合性が取れなくなる可能性（例: CSV を編集したが SQLite に反映されていない）。
- **対策**:
  - 「Single Source of Truth は CSV / JSON ファイル」というルールを明文化。
  - CSV / JSON 再取り込み時に SQLite を上書き更新する処理を実装（REQ-F-008）。
  - 整合性チェック機能（CSV と SQLite のレコード数を比較）を追加（将来の拡張候補）。

---

### リスク軽減策の概要

**コーディング規約／レイヤ間の依存ルールの明文化**:
- **規約**: PEP 8 準拠、docstring 記述、テストカバレッジ 80% 以上。
- **依存ルール**:
  - Presentation 層 → Application 層（Presenter が Application 層のユースケースを呼び出す）
  - Application 層 → Domain 層（ユースケースが Domain 層のビジネスロジックを呼び出す）
  - Application 層 → Infrastructure 層（ユースケースが Repository 経由で Infrastructure 層にアクセス）
  - Domain 層 → Infrastructure 層（× 禁止、依存性逆転の原則）
  - Infrastructure 層 → Domain 層（Repository 実装が Domain 層のエンティティを使用）

**リポジトリパターンやインターフェースによる抽象化の導入**:
- Repository インターフェースを Domain 層で定義し、Infrastructure 層で実装。
- Application 層は Repository インターフェース経由でのみデータにアクセス。
- テスト時は Repository をモックに差し替え。

**定期的なアーキテクチャレビュー**:
- 月次でアーキテクチャレビューを実施し、技術的負債の蓄積を確認。
- レビュー項目:
  - Domain 層以外にビジネスロジックが漏れていないか
  - Repository インターフェースが適切に使用されているか
  - テストカバレッジが 80% 以上を維持しているか

**「どのような変更要求が来たらアーキテクチャの再評価を行うか」のトリガー定義**:
- **トリガー 1**: 新しいデータソースの追加（例: CSV → API 連携、外部 DB 連携）
  - 対応: Infrastructure 層に新しい Repository 実装を追加（Domain 層は変更不要）
- **トリガー 2**: マルチユーザー・マルチテナント化（例: Web アプリ化、SaaS 化）
  - 対応: アーキテクチャの再評価が必要（モノリス → マイクロサービス、SQLite → PostgreSQL / MySQL）
- **トリガー 3**: リアルタイム更新（例: WebSocket、メッセージキュー）
  - 対応: アーキテクチャの再評価が必要（イベント駆動アーキテクチャの導入）
- **トリガー 4**: 複雑な要因推定ロジック（例: 機械学習モデルの導入）
  - 対応: Domain 層に新しいサービスクラス（FactorEstimationService）を追加（アーキテクチャ変更不要）

---

## 7. Inputs for ADR（ADR 作成のための要約）

### Problem（問題）

複数プロジェクトの工数消化状況を日次で可視化するデスクトップアプリケーション（Profit Trace）のアーキテクチャを決定する必要がある。

**前提条件**:
- **技術制約**: Python 3.12 + PySide6 + SQLite + plotly。デスクトップアプリ（マルチユーザー同時接続不要）。
- **運用制約**: 日次データ更新、1 日 30 分程度の稼働、各ローカル PC で単独実行。
- **組織制約**: 小規模チーム（1〜3 名）での開発・保守。PEP 8 準拠、テストカバレッジ 80% 以上の品質基準を維持。
- **データフロー**: 外部 CSV / JSON ファイル（Single Source of Truth）→ SQLite（キャッシュ）→ UI。日次で CSV / JSON を再取り込みし、SQLite を上書き更新。

**重視すべき品質特性**:
- Performance: CSV 読み込み 5〜10 秒、チャート描画 3〜5 秒、UI フリーズなし（QA-001）
- Maintainability: 将来の機能拡張（新しい集計軸、複雑な要因推定）が容易（QA-003）
- Testability: テストカバレッジ 80% 以上、ビジネスロジックの単体テストが容易（QA-008）
- Usability: ドラッグ&ドロップ、ワンクリック遷移、明確なエラーメッセージ（QA-002）
- Availability: 不正ファイル読み込み時もクラッシュせず、正常復帰（QA-004）

---

### Decision（決定）

**DDD Lite Monolith（4 層構成: Presentation / Application / Domain / Infrastructure + MVP パターン）** を採用する。

**一文要約**: モジュラモノリス構成の 4 層アーキテクチャを採用し、Presentation / Application / Domain / Infrastructure の層で構成する。Presentation 層には MVP パターンを適用し、Domain 層にビジネスロジックを集約する。Repository パターンにより Domain 層と Infrastructure 層を分離し、依存性逆転の原則を適用する。

---

### Alternatives（代替案）

**Candidate A: Layered Monolith（3 層構成 + MVP パターン）**
- **退けた理由**: 実装速度が速くパフォーマンスが高いが、Application 層の肥大化リスクがあり、将来の機能拡張時のリファクタリングコストが増加する可能性。テスト容易性も Candidate B に劣る。

**Candidate C: Layered Monolith（3 層構成 + MVC パターン）**
- **退けた理由**: Qt Model/View フレームワークとの親和性が高いが、本プロジェクトはグラフ描画中心であり、利点を活かしにくい。MVC パターンの複雑さにより、エラーハンドリングの責務が分散しやすく、変更時の影響範囲が読みにくくなる。

---

### Rationale（根拠）

**主要品質特性との関係**:
- **QA-003（Maintainability）**: Domain 層を独立させることで、ビジネスロジックの変更影響範囲を狭く保てる。将来の機能拡張（新しい集計軸、複雑な要因推定）に強い。
- **QA-008（Testability）**: Repository インターフェースにより、テスト時に Infrastructure 層をモックに差し替え可能。Domain 層のビジネスロジックは純粋な関数として実装でき、単体テストが容易。
- **QA-001（Performance）**: 抽象化層が 1 段増えるが、要件の性能基準（CSV 読み込み: 5〜10 秒、チャート描画: 3〜5 秒）は十分に満たす。パフォーマンスのわずかな低下（1〜2 秒程度）は、Maintainability と Testability の大幅な向上によるトレードオフとして許容範囲内。
- **QA-002（Usability）**: MVP パターンにより、Presenter が View ↔ Application 層の仲介を行い、UI イベントの処理がシンプルになる。

**データフローとの整合性**:
- Repository インターフェースにより、Infrastructure 層の変更（例: SQLite → PostgreSQL、CSV → API 連携）が容易。Domain 層は Infrastructure 層に依存しないため、データソースの変更が Domain 層に影響しない。

---

### Consequences（結果・影響）

**ポジティブな影響**:
- **変更容易性の向上**: Domain 層の独立により、ビジネスロジックの変更影響範囲が明確になり、長期的な保守性が向上する。
- **テスト容易性の向上**: Repository インターフェースによるモック化により、テストカバレッジ 80% 以上の品質基準を維持しやすい。
- **将来の拡張性の向上**: 新しい集計軸、複雑な要因推定ロジック、外部サービス統合が容易になる。

**ネガティブな影響**:
- **初期実装コストの増加**: Candidate A 比で 1.2〜1.5 倍程度の増加（6〜9 日 vs 5〜6 日）。
- **学習コストの増加**: DDD の概念（エンティティ、Repository、依存性逆転の原則）の理解に 1〜2 日。
- **パフォーマンスのわずかな低下**: 抽象化層が 1 段増えるため、処理時間が 1〜2 秒程度増加する可能性（ただし、要件の性能基準は満たす）。

**将来の拡張時に必要となるリファクタリングや見直しポイント**:
- **マルチユーザー・マルチテナント化**: モノリス → マイクロサービス、SQLite → PostgreSQL / MySQL への移行が必要。
- **リアルタイム更新**: イベント駆動アーキテクチャの導入が必要。
- **機械学習モデルの導入**: Domain 層に新しいサービスクラス（FactorEstimationService）を追加（アーキテクチャ変更不要）。
